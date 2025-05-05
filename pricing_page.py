#fastapi_app/pricing_page.py 

#fastapi_app\pricing_page.py
"""from django.utils import timezone
from dateutil.relativedelta import relativedelta
from appln.models import UserSubscription, UserData
from asgiref.sync import sync_to_async

@sync_to_async
def create_subscription_for_user(user: UserData,  email=None, userid=None, first_name=None, last_name =None):
    # Check if subscription already exists
    subscription, created = UserSubscription.objects.get_or_create(user=user)
    
    # If it's a new subscription, we set the initial plan details
    if created:
        # Default plan and pricing
        subscription.current_plan = 'basic'  # Default plan
        subscription.pricing = 0  # Example pricing for 'basic' plan
        
        # Set plan expiration date and renews_on (next month)
        subscription.plan_expiring_date = timezone.now() + relativedelta(months=1)
        subscription.renews_on = timezone.now().date() + relativedelta(months=1)
        
        # Set default credits
        subscription.total_credits = 10  # Default credits
        subscription.used_credits = 0
        subscription.total_credits_used_all_time = 0
        if email:
            subscription.email = email
        if userid:
            subscription.userid = userid
        if first_name:
            subscription.first_name = first_name
        
        # Save the subscription details
        subscription.save()
    else:
        # Optional: update the subscription if needed (e.g., if the plan changes)
        if subscription.current_plan != 'basic':  # Only if plan is not 'basic'
            subscription.pricing = get_price_for_plan(subscription.current_plan)
            subscription.plan_expiring_date = timezone.now() + relativedelta(months=1)
            subscription.renews_on = timezone.now().date() + relativedelta(months=1)
            subscription.save()

    return subscription

def get_price_for_plan(plan):
    pricing = {
        "basic": 0.00,
        "silver": 10.00,
        "gold": 20.00
    }
    if plan not in pricing:
        raise ValueError(f"Unknown plan: {plan}")
    return pricing[plan]"""

"""from fastapi import APIRouter, Depends, HTTPException
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from appln.models import UserData, UserSubscription
from asgiref.sync import sync_to_async
from fastapi_app.auth import verify_token   # Ensure this import is correct

router = APIRouter()

# Price mapping
def get_price_for_plan(plan: str, duration: str) -> float:
    pricing = {
        "silver": {"monthly": 10.00, "yearly": 100.00},
        "gold": {"monthly": 20.00, "yearly": 200.00},
        "platinum": {"monthly": 30.00, "yearly": 300.00},
        "basic": {"monthly": 0.00, "yearly": 0.00},
    }
    if plan not in pricing or duration not in pricing[plan]:
        raise ValueError(f"Invalid plan or duration: {plan}, {duration}")
    return pricing[plan][duration]

# Members count mapping
def get_total_members(plan: str) -> int:
    return {
        "basic": 1,
        "silver": 1,
        "gold": 5,
        "platinum": 7
    }.get(plan, 1)

@sync_to_async
def create_subscription_for_user(subscription, new_plan: str, new_duration: str):
    # Update subscription details
    subscription.current_plan = new_plan
    subscription.duration = new_duration
    subscription.start_date = timezone.now().date()
    subscription.total_members = get_total_members(new_plan)
    subscription.pricing = get_price_for_plan(new_plan, new_duration)

    # Set renew and expiry based on plan duration
    if new_duration == 'monthly':
        subscription.renews_on = timezone.now().date() + relativedelta(months=1)
        subscription.plan_expiring_date = timezone.now() + relativedelta(months=1)
    elif new_duration == 'yearly':
        subscription.renews_on = timezone.now().date() + relativedelta(years=1)
        subscription.plan_expiring_date = timezone.now() + relativedelta(years=1)
    else:
        subscription.renews_on = None
        subscription.plan_expiring_date = None

    # Save subscription updates
    subscription.save()
    return subscription

# Route to update subscription
@router.post("/update-subscription/")
async def update_subscription(new_plan: str, new_duration: str, token_data: dict = Depends(verify_token)):
    email = token_data.get("email")
    userid = token_data.get("userid")

    # Check if token data contains email or userid
    if not (email or userid):
        raise HTTPException(status_code=401, detail="Invalid token")

    # Find the user from the database using email or userid
    try:
        if email:
            user = await sync_to_async(UserData.objects.get)(email=email)
        else:
            user = await sync_to_async(UserData.objects.get)(userid=userid)
    except UserData.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    # Find the user's subscription
    try:
        subscription = await sync_to_async(UserSubscription.objects.get)(user=user)
    except UserSubscription.DoesNotExist:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Update the subscription with the new plan and duration
    updated = await create_subscription_for_user(subscription, new_plan, new_duration)

    # Return the updated subscription details
    return {
        "message": "Subscription updated successfully",
        "plan": updated.current_plan,
        "duration": updated.duration,
        "pricing": updated.pricing,
        "renews_on": updated.renews_on,
        "plan_expiring_date": updated.plan_expiring_date
    }
"""
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from appln.models import UserData, UserSubscription
from asgiref.sync import sync_to_async
#from fastapi_app.auth import get_current_user  
from jose import JWTError, jwt
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv() # Make sure to define this function to extract current user from OAuth2 token

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM =os.getenv("ALGORITHM") 

router = APIRouter()

# OAuth2PasswordBearer is a class that helps in getting the token from the "Authorization" header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # tokenUrl can be the URL where users get the token

# Price mapping
def get_price_for_plan(plan: str, duration: str) -> float:
    pricing = {
        "silver": {"monthly": 10.00, "yearly": 100.00},
        "gold": {"monthly": 20.00, "yearly": 200.00},
        "platinum": {"monthly": 30.00, "yearly": 300.00},
        "basic": {"monthly": 0.00, "yearly": 0.00},
    }
    if plan not in pricing or duration not in pricing[plan]:
        raise ValueError(f"Invalid plan or duration: {plan}, {duration}")
    return pricing[plan][duration]

# Members count mapping
def get_total_members(plan: str) -> int:
    return {
        "basic": 1,
        "silver": 1,
        "gold": 5,
        "platinum": 7
    }.get(plan, 1)

#credit mapping 
def get_credits_for_plan(plan: str) -> int:
    plan = plan.lower()
    return {
        "basic": 10,
        "silver": 20,
        "gold": 50,
        "platinum": 100
    }.get(plan, 0)

@sync_to_async
def create_subscription_for_user(subscription, new_plan: str, new_duration: str):
    subscription.current_plan = new_plan
    subscription.duration = new_duration
    subscription.start_date = timezone.now().date()
    subscription.total_members = get_total_members(new_plan)
    subscription.pricing = get_price_for_plan(new_plan, new_duration)
    subscription.total_credits = get_credits_for_plan(new_plan)

    # Set renew and expiry
    if new_duration == 'monthly':
        subscription.renews_on = timezone.now().date() + relativedelta(months=1)
        subscription.plan_expiring_date = timezone.now() + relativedelta(months=1)
    elif new_duration == 'yearly':
        subscription.renews_on = timezone.now().date() + relativedelta(years=1)
        subscription.plan_expiring_date = timezone.now() + relativedelta(years=1)
    else:
        subscription.renews_on = None
        subscription.plan_expiring_date = None

    subscription.save()
    return subscription

# Extract the current user from the OAuth2 token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Here you can implement the code to get the user from your OAuth2 authentication system (e.g., Auth0)
    # This could include decoding the JWT token and extracting the user information.
    # For now, we assume the token has email and userid fields.
    
    try:
        # Decode the token and extract user info
        # Assuming you already have a function to decode JWT or OAuth token and extract user info
        # For example, using JWT: jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        userid = payload.get("userid")
        return email, userid
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# Route to update subscription
"""@router.post("/update-subscription/")
async def update_subscription(new_plan: str, new_duration: str, token_data: dict = Depends(get_current_user)):
    email, userid = token_data

    if not (email or userid):
        raise HTTPException(status_code=401, detail="Invalid token")

    # Find the user from the database
    try:
        user = await sync_to_async(UserData.objects.get)(email=email) if email else await sync_to_async(UserData.objects.get)(userid=userid)
    except UserData.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    # Find the user's subscription
    try:
        subscription = await sync_to_async(UserSubscription.objects.get)(user=user)
    except UserSubscription.DoesNotExist:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Update the subscription
    updated = await create_subscription_for_user(subscription, new_plan, new_duration)

    return {
        "message": "Subscription updated successfully",
        "plan": updated.current_plan,
        "duration": updated.duration,
        "pricing": updated.pricing,
        "renews_on": updated.renews_on,
        "plan_expiring_date": updated.plan_expiring_date
    }"""

@router.post("/update-subscription/")
async def update_subscription(
    new_plan: str,
    new_duration: str,
    email: str = None,
    userid: str = None
):
    if not (email or userid):
        raise HTTPException(status_code=400, detail="Email or UserID required for testing")

    try:
        user = await sync_to_async(UserData.objects.get)(email=email) if email else await sync_to_async(UserData.objects.get)(userid=userid)
    except UserData.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        subscription = await sync_to_async(UserSubscription.objects.get)(user=user)
    except UserSubscription.DoesNotExist:
        raise HTTPException(status_code=404, detail="Subscription not found")

    updated = await create_subscription_for_user(subscription, new_plan, new_duration)

    return {
        "message": "Subscription updated successfully",
        "plan": updated.current_plan,
        "duration": updated.duration,
        "pricing": updated.pricing,
        "renews_on": updated.renews_on,
        "plan_expiring_date": updated.plan_expiring_date
    }


