from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse


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

    response = requests.post(token_url, data=urlencode(data), headers={'Content-Type': 'application/x-www-form-urlencoded'})
    token_info = response.json()
    access_token = token_info.get('access_token')

    if not access_token:
        raise HTTPException(status_code=400, detail="Token exchange failed")

    # Step 2: Get user info
    user_info_url = f"https://{AUTH0_DOMAIN}/userinfo"
    user_info_response = requests.get(user_info_url, headers={'Authorization': f'Bearer {access_token}'})
    user_info = user_info_response.json()

    email = user_info.get('email')
    provider = user_info.get('sub').split('|')[0]

    if not email:
        raise HTTPException(status_code=400, detail="User email not found")


    def handle_user():
        user = UserData.objects.filter(email=email).first()
        if user:
            # Login → Redirect to home (simulated)
            return RedirectResponse(url="/home", status_code=302)
        else:
            #  Not in DB → Create user and treat as signup
            UserData.objects.create(email=email, provider=provider, password=None)
            return RedirectResponse(url="/home", status_code=302)

    return await run_in_threadpool(handle_user)

@router.get("/home")
async def home():
    return {"message": "Welcome to the Home Page!"}
