from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.logger import logger
from asgiref.sync import sync_to_async


from starlette.concurrency import run_in_threadpool
import os
import django
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()


AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")



# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_project.settings")
django.setup()

from appln.models import UserData
from social_django.models import UserSocialAuth 

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/signup")
async def signup(user: User):
    def create_user():
        if UserData.objects.filter(email=user.email).exists():
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_password = hash_password(user.password)
        UserData.objects.create(email=user.email, password=hashed_password, provider="email")

    try:
        await run_in_threadpool(create_user)
        return JSONResponse(status_code=201, content={"message": "User created successfully"})
    except HTTPException as e:
        raise e
    except Exception as e:
        print("Internal Server Error:", e)
        raise HTTPException(status_code=500, detail="Something went wrong")

@router.post("/login")
async def login(user: User):
    def get_user():
        try:
            user_obj = UserData.objects.get(email=user.email)
            if not verify_password(user.password, user_obj.password):
                raise HTTPException(status_code=401, detail="Invalid password")
            return user_obj
        except UserData.DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

    try:
        await run_in_threadpool(get_user)
        return {"message": "Login successful"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(" Login Error:", e)
        raise HTTPException(status_code=500, detail="Something went wrong")
    

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

    response = requests.post(
        token_url,
        data=urlencode(data),
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    token_info = response.json()
    access_token = token_info.get('access_token')
    if not access_token:
        raise HTTPException(status_code=400, detail="Token exchange failed")

    # Step 2: Get user info using access token
    user_info_url = f"https://{AUTH0_DOMAIN}/userinfo"
    user_info_response = requests.get(
        user_info_url,
        headers={'Authorization': f'Bearer {access_token}'}
    )
    user_info = user_info_response.json()

    # Extract data from Auth0 response
    email = user_info.get('email')  # Google will give email
    sub = user_info.get('sub')      # e.g. google-oauth2|12345
    provider = sub.split("|")[0]    # google-oauth2 / facebook / apple
    user_id = sub                   # full unique ID for fb/apple
    first_name = user_info.get('given_name') or user_info.get('name') or "User"

    # Email is only required for Google
    if provider == "google-oauth2" and not email:
        raise HTTPException(status_code=400, detail="User email not found")

    # Step 3: Route to provider-specific handler
    if provider == "google-oauth2":
        return await handle_google_signup_login(email, first_name)
    elif provider == "facebook":
        return await handle_facebook_signup_login(user_id, first_name)
    elif provider == "apple":
        return await handle_apple_signup_login(user_id)
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")


async def handle_google_signup_login(email, first_name):
    # Handle Google login/signup logic
    user = await sync_to_async(UserData.objects.filter(email=email).first)()
    if user:
        return RedirectResponse(url="/profile", status_code=302)
    else:
        # Store new user data in the database
        await sync_to_async(UserData.objects.create)(email=email, first_name=first_name, provider="google")
        return RedirectResponse(url="/profile", status_code=302)

async def handle_facebook_signup_login(user_id, first_name):
    # Handle Facebook login/signup logic
    user = await sync_to_async(UserData.objects.filter(userid=user_id).first)()
    if user:
        return RedirectResponse(url="/profile", status_code=302)
    else:
        # Store new user data in the database
        await sync_to_async(UserData.objects.create)(userid=user_id, first_name=first_name, provider="facebook")
        return RedirectResponse(url="/profile", status_code=302)

async def handle_apple_signup_login(user_id):
    user = await sync_to_async(UserData.objects.filter(userid=user_id).first)()
    if user:
        return RedirectResponse(url="/profile", status_code=302)
    else:
        await sync_to_async(UserData.objects.create)(
            userid=user_id,
            provider="apple"
        )
        return RedirectResponse(url="/profile", status_code=302)
