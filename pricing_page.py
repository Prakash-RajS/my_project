"""import stripe
from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from appln.models import UserData, UserSubscription, BillingHistory, BillingInfo
from asgiref.sync import sync_to_async
from uuid import uuid4
from pydantic import BaseModel
from fastapi_app.invoice_generator import generate_invoice_pdf
import smtplib
from email.message import EmailMessage
from django.db import transaction
from fastapi import Query
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
FRONTEND_SUCCESS_URL = os.getenv("FRONTEND_SUCCESS_URL")  # URL after payment success
FRONTEND_CANCEL_URL = os.getenv("FRONTEND_CANCEL_URL")    # URL after payment cancel

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class BillingInfoModel(BaseModel):
    full_name: str
    phone_number: str
    street_address: str
    city: str
    state: str
    country: str
    pincode: str

class SubscriptionData(BaseModel):
    email: str = None
    userid: str = None
    plan: str
    duration: str
    coupon_code: str = None
    payment_method: str
    billing_info: BillingInfoModel
    payment_success: bool = True

def send_invoice_email(to_email, customer_name, invoice_path):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Thank You for Upgrading Your Plan!"
        msg["From"] = os.getenv("SMTP_SENDER_EMAIL")
        msg["To"] = to_email
        msg.set_content(f
Hi {customer_name},

Thank you for upgrading your plan with us. Please find the invoice for your recent purchase attached.

If you have any questions, feel free to reach out.

Best regards,
Your Team
)

        # Attach invoice PDF
        with open(invoice_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(invoice_path)
            msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

        # Send email
        with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
            server.send_message(msg)

    except Exception as e:
        print(f"Failed to send email: {e}")

@router.get("/verify-payment/")
async def verify_payment(session_id: str = Query(..., description="Stripe Checkout Session ID")):
    try:
        # Retrieve the session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        # Check if payment was successful
        if checkout_session.payment_status == "paid":
            return {
                "success": True,
                "message": "Payment verified",
                "payment_intent": checkout_session.payment_intent,
                "customer_email": checkout_session.customer_details.email if checkout_session.customer_details else None
            }
        else:
            return {
                "success": False,
                "message": "Payment not completed yet",
                "status": checkout_session.payment_status
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying payment: {str(e)}")

@router.post("/create-checkout-session/")
async def create_checkout_session(subscription_data: SubscriptionData):
    try:
        price = get_price_for_plan(subscription_data.plan, subscription_data.duration)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': f"{subscription_data.plan.capitalize()} Plan - {subscription_data.duration.capitalize()}"
                    },
                    'unit_amount': int(price * 100),
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=FRONTEND_SUCCESS_URL + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=FRONTEND_CANCEL_URL,
            metadata={
                "email": subscription_data.email or subscription_data.userid,
                "plan": subscription_data.plan,
                "duration": subscription_data.duration,
                "payment_method": subscription_data.payment_method,
                "full_name": subscription_data.billing_info.full_name
            }
        )
        return {"checkout_url": checkout_session.url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-subscription/")
async def update_subscription(subscription_data: SubscriptionData, session_id: str):
    if not (subscription_data.email or subscription_data.userid):
        raise HTTPException(status_code=400, detail="Email or UserID required")

    try:
        # Fetch the user
        if subscription_data.email:
            user = await sync_to_async(UserData.objects.get)(email=subscription_data.email)
        else:
            user = await sync_to_async(UserData.objects.get)(userid=subscription_data.userid)
    except UserData.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Fetch the Stripe session details to get the transaction ID
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        payment_intent_id = checkout_session.payment_intent  # This will be the transaction ID

        # Run DB operations inside a transaction
        @sync_to_async
        @transaction.atomic
        def perform_db_operations():
            # Original price logic
            original_price = get_price_for_plan(subscription_data.plan, subscription_data.duration)
            discount_price = original_price  # apply discount if needed

            # Create or update subscription
            subscription, _ = UserSubscription.objects.get_or_create(user=user)
            subscription.current_plan = subscription_data.plan
            subscription.duration = subscription_data.duration
            subscription.start_date = timezone.now().date()
            subscription.original_price = original_price
            subscription.discount_price = discount_price
            subscription.total_members = get_total_members(subscription_data.plan)
            subscription.total_credits = get_credits_for_plan(subscription_data.plan)

            if subscription_data.duration == 'monthly':
                subscription.renews_on = timezone.now().date() + relativedelta(months=1)
                subscription.plan_expiring_date = timezone.now() + relativedelta(months=1)
            elif subscription_data.duration == 'yearly':
                subscription.renews_on = timezone.now().date() + relativedelta(years=1)
                subscription.plan_expiring_date = timezone.now() + relativedelta(years=1)
            else:
                subscription.renews_on = None
                subscription.plan_expiring_date = None

            subscription.save()

            # Save billing info
            BillingInfo.objects.create(
                user=user,
                full_name=subscription_data.billing_info.full_name,
                email=subscription_data.email,
                phone_number=subscription_data.billing_info.phone_number,
                street_address=subscription_data.billing_info.street_address,
                city=subscription_data.billing_info.city,
                state=subscription_data.billing_info.state,
                zip_code=subscription_data.billing_info.pincode,
                country=subscription_data.billing_info.country
            )

            # Create billing history with dynamic transaction ID from Stripe
            billing = BillingHistory.objects.create(
                user=user,
                plan_name=subscription_data.plan,
                amount=discount_price,
                payment_method=subscription_data.payment_method,
                status="paid",
                invoice_id=str(uuid4()),
                transaction_id=payment_intent_id,  # Save the transaction ID here
                paid_on=timezone.now().date()
            )

            # Generate invoice PDF
            invoice_path = generate_invoice_pdf({
                "customer_name": subscription_data.billing_info.full_name,
                "email": subscription_data.email,
                "invoice_id": billing.invoice_id,
                "paid_on": billing.paid_on.strftime("%d-%m-%Y"),
                "renews_on": subscription.renews_on.strftime("%d-%m-%Y") if subscription.renews_on else "N/A",
                "plan": billing.plan_name,
                "duration": subscription.duration,
                "start_date": subscription.start_date.strftime("%d-%m-%Y"),
                "expire_date": subscription.plan_expiring_date.strftime("%d-%m-%Y") if subscription.plan_expiring_date else "N/A",
                "amount": billing.amount,
                "payment_method": billing.payment_method,
                "transaction_id": billing.transaction_id,
                "logo_path": None,
            })

            billing.invoice = invoice_path
            billing.save()

            # Send thank you email with invoice
            send_invoice_email(
                to_email=subscription_data.email,
                customer_name=subscription_data.billing_info.full_name,
                invoice_path=invoice_path
            )

        await perform_db_operations()

        return {
            "message": "Subscription and billing completed successfully",
            "subscription": subscription_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")"""


#stripe updated file, well working and tesing complete
"""import stripe
import json
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.security import OAuth2PasswordBearer
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from appln.models import UserData, UserSubscription, BillingHistory, BillingInfo
from asgiref.sync import sync_to_async
import random
from pydantic import BaseModel
from fastapi_app.invoice_generator import generate_invoice_pdf
import smtplib
import os
from email.message import EmailMessage
from django.db import transaction
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
FRONTEND_SUCCESS_URL = os.getenv("FRONTEND_SUCCESS_URL")  # URL after payment success
FRONTEND_CANCEL_URL = os.getenv("FRONTEND_CANCEL_URL")    # URL after payment cancel

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_price_for_plan(plan: str, duration: str) -> float:
    pricing = {
        "silver": {"monthly": 100.00, "yearly": 500.00},
        "gold": {"monthly": 200.00, "yearly": 700.00},
        "platinum": {"monthly": 300.00, "yearly": 900.00},
        "basic": {"monthly": 0.00, "yearly": 0.00},
    }
    if plan not in pricing or duration not in pricing[plan]:
        raise ValueError(f"Invalid plan or duration: {plan}, {duration}")
    return pricing[plan][duration]

def get_total_members(plan: str) -> int:
    return {
        "basic": 1,
        "silver": 1,
        "gold": 5,
        "platinum": 7
    }.get(plan, 1)

def get_credits_for_plan(plan: str) -> int:
    return {
        "basic": 10,
        "silver": 20,
        "gold": 50,
        "platinum": 100
    }.get(plan.lower(), 0)

class BillingInfoModel(BaseModel):
    full_name: str
    phone_number: str
    street_address: str
    city: str
    state: str
    country: str
    pincode: str

class SubscriptionData(BaseModel):
    email: str = None
    userid: str = None
    plan: str
    duration: str
    coupon_code: str = None
    payment_method: str
    billing_info: BillingInfoModel
    payment_success: bool = True

def send_invoice_email(to_email, customer_name, invoice_path):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Thank You for Upgrading Your Plan!"
        msg["From"] = os.getenv("SMTP_SENDER_EMAIL")
        msg["To"] = to_email
        msg.set_content(f
Hi {customer_name},

Thank you for upgrading your plan with us. Please find the invoice for your recent purchase attached.

If you have any questions, feel free to reach out.

Best regards,
Your Team
)

        # Attach invoice PDF
        with open(invoice_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(invoice_path)
            msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

        # Send email
        with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
            server.send_message(msg)

    except Exception as e:
        print(f"Failed to send email: {e}")

@router.get("/verify-payment/")
async def verify_payment(session_id: str = Query(..., description="Stripe Checkout Session ID")):
    try:
        # Retrieve the session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        # Check if payment was successful
        if checkout_session.payment_status == "paid":
            return {
                "success": True,
                "message": "Payment verified",
                "payment_intent": checkout_session.payment_intent,
                "customer_email": checkout_session.customer_details.email if checkout_session.customer_details else None
            }
        else:
            return {
                "success": False,
                "message": "Payment not completed yet",
                "status": checkout_session.payment_status
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying payment: {str(e)}")


"""@router.post("/stripe-webhook/")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session["id"]
        try:
            from fastapi_app.pricing_page import update_subscription
            await update_subscription(session_id=session_id)
        except Exception as e:
            print(f"Failed to update subscription from webhook: {str(e)}")

    return {"status": "success"}
"""
@router.post("/create-checkout-session/")
async def create_checkout_session(subscription_data: SubscriptionData):
    try:
        price = get_price_for_plan(subscription_data.plan, subscription_data.duration)
        
        # Convert billing_info to string (JSON)
        billing_info_str = json.dumps({
            "full_name": subscription_data.billing_info.full_name,
            "email" :subscription_data.email,
            "phone_number": subscription_data.billing_info.phone_number,
            "street_address": subscription_data.billing_info.street_address,
            "city": subscription_data.billing_info.city,
            "state": subscription_data.billing_info.state,
            "country": subscription_data.billing_info.country,
            "pincode": subscription_data.billing_info.pincode
        })

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': f"{subscription_data.plan.capitalize()} Plan - {subscription_data.duration.capitalize()}"
                    },
                    'unit_amount': int(price * 100),
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=FRONTEND_SUCCESS_URL + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=FRONTEND_CANCEL_URL,
            metadata={  # Saving details as metadata for later processing
                "email": str(subscription_data.email),
                "userid": str(subscription_data.userid),
                "plan": str(subscription_data.plan),
                "duration": str(subscription_data.duration),
                "coupon_code": str(subscription_data.coupon_code),
                "payment_method": str(subscription_data.payment_method),
                "billing_info": billing_info_str,
                "payment_success": str(subscription_data.payment_success)
            }
        )
        return {"checkout_url": checkout_session.url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-subscription/")
async def update_subscription(session_id: str):
    try:
        # Retrieve Stripe session to get payment details and metadata
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        metadata = checkout_session.metadata
        payment_intent_id = checkout_session.payment_intent

        # Get user from metadata (email or user ID) and create subscription
        user_email = metadata.get("email")
        user = await sync_to_async(UserData.objects.get)(email=user_email)

        # Retrieve billing info from metadata
        billing_info_data = json.loads(metadata.get("billing_info"))

        # Check if payment was successful
        if checkout_session.payment_status != "paid":
            raise HTTPException(status_code=400, detail="Payment not successful.")

        # Create or update the subscription
        @sync_to_async
        @transaction.atomic
        def perform_db_operations():
            original_price = get_price_for_plan(metadata["plan"], metadata["duration"])
            discount_price = original_price

            subscription, _ = UserSubscription.objects.get_or_create(user=user)
            subscription.current_plan = metadata["plan"]
            subscription.duration = metadata["duration"]
            subscription.start_date = timezone.now().date()
            subscription.original_price = original_price
            subscription.discount_price = discount_price
            subscription.total_members = get_total_members(metadata["plan"])
            subscription.total_credits = get_credits_for_plan(metadata["plan"])

            if metadata["duration"] == "monthly":
                subscription.renews_on = timezone.now().date() + relativedelta(months=1)
                subscription.plan_expiring_date = timezone.now() + relativedelta(months=1)
            elif metadata["duration"] == "yearly":
                subscription.renews_on = timezone.now().date() + relativedelta(years=1)
                subscription.plan_expiring_date = timezone.now() + relativedelta(years=1)
            else:
                subscription.renews_on = None
                subscription.plan_expiring_date = None

            subscription.save()

            # Save billing info
            BillingInfo.objects.create(
                user=user,
                full_name=billing_info_data["full_name"],
                email=user_email,
                phone_number=billing_info_data["phone_number"],
                street_address=billing_info_data["street_address"],
                city=billing_info_data["city"],
                state=billing_info_data["state"],
                zip_code=billing_info_data["pincode"],
                country=billing_info_data["country"]
            )

            # Create billing history
            billing = BillingHistory.objects.create(
                user=user,
                plan_name=metadata["plan"],
                amount=discount_price,
                payment_method=metadata["payment_method"],
                status="paid",
                invoice_id=f"INV-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                transaction_id=payment_intent_id,
                paid_on=timezone.now().date()
            )

            # Generate invoice PDF with minimal data (price, name, email, etc.)
            invoice_path = generate_invoice_pdf({
                "customer_name": billing_info_data["full_name"],
                "email": user_email,
                "invoice_id": billing.invoice_id,
                "paid_on": billing.paid_on.strftime("%d-%m-%Y"),
                "renews_on": subscription.renews_on.strftime("%d-%m-%Y") if subscription.renews_on else "N/A",
                "plan": billing.plan_name,
                "duration": subscription.duration,
                "start_date": subscription.start_date.strftime("%d-%m-%Y"),
                "expire_date": subscription.plan_expiring_date.strftime("%d-%m-%Y") if subscription.plan_expiring_date else "N/A",
                "amount": billing.amount,
                "payment_method": billing.payment_method,
                "transaction_id": billing.transaction_id,
                "logo_path": None,
            })
            billing.invoice = invoice_path
            billing.save()


            # Send invoice email
            send_invoice_email(
                to_email=user_email,
                customer_name=billing_info_data["full_name"],
                invoice_path=invoice_path
            )

            return {"message": "Subscription updated successfully!"}

        # Perform database operation
        result = await perform_db_operations()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))"""

#this file well working and testing complete(update coupan code login and invoice pdf ) 

import stripe
import json
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.security import OAuth2PasswordBearer
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from appln.models import UserData, UserSubscription, BillingHistory, BillingInfo
from asgiref.sync import sync_to_async
import random
from pydantic import BaseModel
from fastapi_app.invoice_generator import generate_invoice_pdf
import smtplib
import os
from email.message import EmailMessage
from django.db import transaction
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
FRONTEND_SUCCESS_URL = os.getenv("FRONTEND_SUCCESS_URL")  # URL after payment success
FRONTEND_CANCEL_URL = os.getenv("FRONTEND_CANCEL_URL")    # URL after payment cancel

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_price_for_plan(plan: str, duration: str) -> float:
    pricing = {
        "silver": {"monthly": 100.00, "yearly": 500.00},
        "gold": {"monthly": 200.00, "yearly": 700.00},
        "platinum": {"monthly": 300.00, "yearly": 900.00},
        "basic": {"monthly": 0.00, "yearly": 0.00},
    }
    if plan not in pricing or duration not in pricing[plan]:
        raise ValueError(f"Invalid plan or duration: {plan}, {duration}")
    return pricing[plan][duration]

def get_total_members(plan: str) -> int:
    return {
        "basic": 1,
        "silver": 1,
        "gold": 5,
        "platinum": 7
    }.get(plan, 1)

def get_credits_for_plan(plan: str) -> int:
    return {
        "basic": 10,
        "silver": 20,
        "gold": 50,
        "platinum": 100
    }.get(plan.lower(), 0)

def get_discount_for_coupon(coupon_code: str, original_price: float) -> float:
    #Calculate discount based on coupon code.
    discount_percentage = 0
    if coupon_code == "DISCOUNT20":
        discount_percentage = 20
    # Add more coupons here in the future
    discount_amount = (original_price * discount_percentage) / 100
    return discount_amount

class BillingInfoModel(BaseModel):
    full_name: str
    phone_number: str
    street_address: str
    city: str
    state: str
    country: str
    pincode: str

class SubscriptionData(BaseModel):
    email: str = None
    userid: str = None
    plan: str
    duration: str
    coupon_code: str = None
    payment_method: str
    billing_info: BillingInfoModel
    payment_success: bool = True

def send_invoice_email(to_email, customer_name, invoice_path):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Thank You for Upgrading Your Plan!"
        msg["From"] = os.getenv("SMTP_SENDER_EMAIL")
        msg["To"] = to_email
        msg.set_content(f"""
Hi {customer_name},

Thank you for upgrading your plan with us. Please find the invoice for your recent purchase attached.

If you have any questions, feel free to reach out.

Best regards,
Your Team
""")

        # Attach invoice PDF
        with open(invoice_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(invoice_path)
            msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

        # Send email
        with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
            server.send_message(msg)

    except Exception as e:
        print(f"Failed to send email: {e}")

@router.get("/verify-payment/")
async def verify_payment(session_id: str = Query(..., description="Stripe Checkout Session ID")):
    try:
        # Retrieve the session from Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)

        # Check if payment was successful
        if checkout_session.payment_status == "paid":
            return {
                "success": True,
                "message": "Payment verified",
                "payment_intent": checkout_session.payment_intent,
                "customer_email": checkout_session.customer_details.email if checkout_session.customer_details else None
            }
        else:
            return {
                "success": False,
                "message": "Payment not completed yet",
                "status": checkout_session.payment_status
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying payment: {str(e)}")


"""@router.post("/stripe-webhook/")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session["id"]
        try:
            from fastapi_app.pricing_page import update_subscription
            await update_subscription(session_id=session_id)
        except Exception as e:
            print(f"Failed to update subscription from webhook: {str(e)}")

    return {"status": "success"}
"""
@router.post("/create-checkout-session/")
async def create_checkout_session(subscription_data: SubscriptionData):
    try:
        price = get_price_for_plan(subscription_data.plan, subscription_data.duration)
        
        # Convert billing_info to string (JSON)
        billing_info_str = json.dumps({
            "full_name": subscription_data.billing_info.full_name,
            "email" :subscription_data.email,
            "phone_number": subscription_data.billing_info.phone_number,
            "street_address": subscription_data.billing_info.street_address,
            "city": subscription_data.billing_info.city,
            "state": subscription_data.billing_info.state,
            "country": subscription_data.billing_info.country,
            "pincode": subscription_data.billing_info.pincode
        })

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': f"{subscription_data.plan.capitalize()} Plan - {subscription_data.duration.capitalize()}"
                    },
                    'unit_amount': int(price * 100),
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=FRONTEND_SUCCESS_URL + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=FRONTEND_CANCEL_URL,
            metadata={  # Saving details as metadata for later processing
                "email": str(subscription_data.email),
                "userid": str(subscription_data.userid),
                "plan": str(subscription_data.plan),
                "duration": str(subscription_data.duration),
                "coupon_code": str(subscription_data.coupon_code),
                "payment_method": str(subscription_data.payment_method),
                "billing_info": billing_info_str,
                "payment_success": str(subscription_data.payment_success)
            }
        )
        return {"checkout_url": checkout_session.url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-subscription/")
async def update_subscription(session_id: str):
    try:
        # Retrieve Stripe session to get payment details and metadata
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        metadata = checkout_session.metadata
        payment_intent_id = checkout_session.payment_intent

        # Get user from metadata (email or user ID) and create subscription
        user_email = metadata.get("email")
        user = await sync_to_async(UserData.objects.get)(email=user_email)

        # Retrieve billing info from metadata
        billing_info_data = json.loads(metadata.get("billing_info"))

        # Check if payment was successful
        if checkout_session.payment_status != "paid":
            raise HTTPException(status_code=400, detail="Payment not successful.")

        # Create or update the subscription
        @sync_to_async
        @transaction.atomic
        def perform_db_operations():
            original_price = get_price_for_plan(metadata["plan"], metadata["duration"])
            discount_amount = get_discount_for_coupon(metadata["coupon_code"], original_price)
            discount_price = original_price - discount_amount

            if discount_price < original_price:
                discount_amount_inr = discount_amount
                discount_percent = round((discount_amount_inr / original_price) * 100)
            else:
                discount_amount_inr = 0
                discount_percent = 0

            subscription, _ = UserSubscription.objects.get_or_create(user=user)
            subscription.current_plan = metadata["plan"]
            subscription.duration = metadata["duration"]
            subscription.start_date = timezone.now().date()
            subscription.original_price = original_price
            subscription.discount_price = discount_price
            subscription.total_members = get_total_members(metadata["plan"])
            subscription.total_credits = get_credits_for_plan(metadata["plan"])
            subscription.coupon_code = metadata.get("coupon_code", None)

            if metadata["duration"] == "monthly":
                subscription.renews_on = timezone.now().date() + relativedelta(months=1)
                subscription.plan_expiring_date = timezone.now() + relativedelta(months=1)
            elif metadata["duration"] == "yearly":
                subscription.renews_on = timezone.now().date() + relativedelta(years=1)
                subscription.plan_expiring_date = timezone.now() + relativedelta(years=1)
            else:
                subscription.renews_on = None
                subscription.plan_expiring_date = None

            subscription.save()

            # Save billing info
            BillingInfo.objects.create(
                user=user,
                full_name=billing_info_data["full_name"],
                email=user_email,
                phone_number=billing_info_data["phone_number"],
                street_address=billing_info_data["street_address"],
                city=billing_info_data["city"],
                state=billing_info_data["state"],
                zip_code=billing_info_data["pincode"],
                country=billing_info_data["country"]
            )

            # Create billing history
            billing = BillingHistory.objects.create(
                user=user,
                plan_name=metadata["plan"],
                amount=discount_price,
                payment_method=metadata["payment_method"],
                status="paid",
                invoice_id=f"INV-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                transaction_id=payment_intent_id,
                paid_on=timezone.now().date()
            )

            # Generate invoice PDF with minimal data (price, name, email, etc.)
            invoice_path = generate_invoice_pdf({
                "customer_name": billing_info_data["full_name"],
                "email": user_email,
                "invoice_id": billing.invoice_id,
                "paid_on": billing.paid_on.strftime("%d-%m-%Y"),
                "renews_on": subscription.renews_on.strftime("%d-%m-%Y") if subscription.renews_on else "N/A",
                "plan": billing.plan_name,
                "duration": subscription.duration,
                "start_date": subscription.start_date.strftime("%d-%m-%Y"),
                "expire_date": subscription.plan_expiring_date.strftime("%d-%m-%Y") if subscription.plan_expiring_date else "N/A",
                #"amount": billing.amount,
                "amount" : subscription.original_price,
                "payment_method": billing.payment_method,
                "transaction_id": billing.transaction_id,
                "logo_path": None,
                "discount_price": subscription.discount_price,
                "discount_amount": discount_amount_inr,  # Discount amount in ₹
                "discount_percent": discount_percent,
            })
            billing.invoice = invoice_path
            billing.save()


            # Send invoice email
            send_invoice_email(
                to_email=user_email,
                customer_name=billing_info_data["full_name"],
                invoice_path=invoice_path
            )

            return {"message": "Subscription updated successfully!"}

        # Perform database operation
        result = await perform_db_operations()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

