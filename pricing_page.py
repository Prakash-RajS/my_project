import stripe
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
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")
