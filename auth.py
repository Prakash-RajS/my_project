from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from asgiref.sync import sync_to_async
from jose import JWTError, jwt
from django.core.exceptions import ObjectDoesNotExist
from fastapi_app.config import SECRET_KEY, ALGORITHM
from fastapi_app.django_setup import django_setup
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db import transaction
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password
import os, requests
from urllib.parse import urlencode
from dotenv import load_dotenv
from fastapi.logger import logger

# Setup
load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_project.settings")
django_setup()

from appln.models import UserData, UserSubscription

# Auth0 config
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    email: EmailStr
    password: str


def hash_password(password: str) -> str:
    return make_password(password)


def verify_password(plain: str, hashed: str) -> bool:
    return check_password(plain, hashed)


@sync_to_async
def user_exists(email: str):
    return UserData.objects.filter(email=email).exists()


@sync_to_async
def create_subscription_for_user(user: UserData):
    subscription, created = UserSubscription.objects.get_or_create(user=user)
    if created:
        subscription.email = user.email or None  # [UPDATED]
        subscription.userid = user.userid or None  # [UPDATED]
        subscription.first_name = user.first_name or None  # [UPDATED]
        subscription.last_name = user.last_name or None  # [UPDATED]
        subscription.current_plan = 'basic'
        subscription.pricing = 0.00
        subscription.plan_expiring_date = timezone.now() + relativedelta(months=1)
        subscription.renews_on = timezone.now().date() + relativedelta(months=1)
        subscription.total_credits = 10
        subscription.used_credits = 0
        subscription.total_credits_used_all_time = 0
        subscription.save()
    return subscription


@router.post("/signup")
async def signup(user_data: User):
    try:
        if await user_exists(user_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_pwd = hash_password(user_data.password)
        user = await sync_to_async(UserData.objects.create)(
            email=user_data.email,
            password=hashed_pwd,
            provider="email"
        )
        await create_subscription_for_user(user)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "User created successfully"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(user_data: User):
    try:
        user = await sync_to_async(UserData.objects.get)(email=user_data.email)
        if not verify_password(user_data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid password")
        return {"message": "Login successful"}
    except UserData.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")

    # Step 1: Exchange code for access token
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': AUTH0_CLIENT_ID,
        'client_secret': AUTH0_CLIENT_SECRET,
        'code': code,
        'redirect_uri': AUTH0_CALLBACK_URL,
    }

    response = requests.post(token_url, data=urlencode(data), headers={'Content-Type': 'application/x-www-form-urlencoded'})
    token_info = response.json()
    access_token = token_info.get('access_token')
    if not access_token:
        raise HTTPException(status_code=400, detail="Token exchange failed")

    # Step 2: Get user info from Auth0
    user_info_url = f"https://{AUTH0_DOMAIN}/userinfo"
    user_info_response = requests.get(user_info_url, headers={'Authorization': f'Bearer {access_token}'})
    user_info = user_info_response.json()

    sub = user_info.get('sub')  # e.g. 'google-oauth2|123456789'
    if not sub:
        raise HTTPException(status_code=400, detail="Auth0 user info missing 'sub'")

    provider = sub.split('|')[0]
    user_id = sub.split('|')[1] if '|' in sub else sub
    email = user_info.get('email')
    first_name = user_info.get('given_name') or user_info.get('name') or ""
    last_name = user_info.get('family_name') or ""

    if provider == "google-oauth2":
        if not email:
            raise HTTPException(status_code=400, detail="Google login failed: email not provided")
        return await handle_provider_signup_login(email=email, first_name=first_name, last_name=last_name, provider="google", user_id=None)

    elif provider == "facebook":
        if not user_id or not first_name:
            raise HTTPException(status_code=400, detail="Facebook login missing required info")
        return await handle_provider_signup_login(email=None, first_name=first_name, last_name=last_name, provider="facebook", user_id=user_id)

    elif provider == "apple":
        if not user_id:
            raise HTTPException(status_code=400, detail="Apple login missing user ID")
        return await handle_provider_signup_login(email=None, first_name=None, last_name=None, provider="apple", user_id=user_id)

    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")


async def handle_provider_signup_login(email: str, first_name: str, last_name: str, provider: str, user_id: str = None):
    try:
        @sync_to_async
        def process_user():
            with transaction.atomic():
                if provider == "google":
                    if not email:
                        raise ValueError("Email required for Google login")
                    user, created = UserData.objects.get_or_create(
                        email=email,
                        defaults={
                            "first_name": first_name or "",
                            "last_name": last_name or "",
                            "password": hash_password(email),
                            "userid": None,
                            "provider": provider,
                        }
                    )
                else:  # Facebook and Apple
                    user, created = UserData.objects.get_or_create(
                        userid=user_id,
                        provider=provider,
                        defaults={
                            "first_name": first_name or "",
                            "last_name": last_name or "",
                            "password": hash_password(user_id),
                            "email": None,  #  Use None instead of empty string
                        }
                    )

                if created:
                    UserSubscription.objects.create(
                        user=user,
                        email=user.email or "",
                        userid=user.userid,
                        name=" ".join(filter(None, [user.first_name, user.last_name])).strip(),
                        current_plan='basic',
                        pricing=0.00,
                        plan_expiring_date=timezone.now() + relativedelta(months=1),
                        renews_on=timezone.now().date() + relativedelta(months=1),
                        total_credits=10,
                        used_credits=0,
                        total_credits_used_all_time=0
                    )
                return user, created

        user, created = await process_user()
        token = jwt.encode({"sub": user.email or user.userid}, SECRET_KEY, algorithm=ALGORITHM)

        response = JSONResponse({
            "message": "Signup successful" if created else "Login successful",
            "access_token": token
        })
        response.set_cookie(key="access_token", value=token, httponly=True, secure=True)
        return response

    except Exception as e:
        logger.error(f"{provider} login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"{provider} authentication failed")


# Manual routes for testing without Auth0 redirects
@router.post("/google_signup_login")
async def google_signup(email: str, first_name: str, last_name: str):
    return await handle_provider_signup_login(email, first_name, last_name, provider="google")


@router.post("/facebook_signup_login")
async def facebook_signup(userid: str, first_name: str, last_name: str):
    return await handle_provider_signup_login(None, first_name, last_name, provider="facebook", user_id=userid)


@router.post("/apple_signup_login")
async def apple_signup(userid: str):
    return await handle_provider_signup_login(None, None, None, provider="apple", user_id=userid)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
