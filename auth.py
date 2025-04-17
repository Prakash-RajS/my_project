from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
import os
import django

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
        print(" Internal Server Error:", e)
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

# Route for social login (Google, Facebook, Apple)
@router.post("/social-login")
async def social_login(provider: str, user: User):
    try:
        social_user = UserSocialAuth.objects.get(provider=provider, user__email=user.email)
    except UserSocialAuth.DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Social account not found for {provider}")

    # Check if social account exists, and perform necessary actions (like creating or logging in user)
    user_obj = UserData.objects.get(email=user.email)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"{provider} login successful"}
