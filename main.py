
"""import os
import sys
from fastapi import FastAPI, HTTPException, Query, Request, status ,Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi_app.django_setup import django_setup
from fastapi_app.auth import router as auth_router
from fastapi_app import image_processing, auth
from fastapi_app.update_profile import router as profile_router
#from fastapi_app.forget_password import router as forget_router
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from jose import JWTError, jwt #used for update_profile.py
from datetime import datetime, timedelta #used for update_profile.py
from pydantic import BaseModel #used for forget_password
from fastapi_app.forget_password import OTPManager #used for forget_password
from django.contrib.auth.models import User #used for forget_password
from django.core.mail import send_mail #used for forget_password
from fastapi_app.config import settings #used for forget_password
from django.contrib.auth import get_user_model #used for forget_password
from typing import Optional #used for forget_password
from starlette.concurrency import run_in_threadpool #used for forget_password
import hashlib#used for forget_password


# Ensure that the fastapi_app folder is in the sys.path for correct imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fastapi_app'))

# Set up Django
django_setup()
from appln.models import UserData

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")

# Initialize FastAPI app
app = FastAPI()

# Include authentication and image processing routers
app.include_router(auth_router, prefix="/auth")
app.include_router(auth.router)
app.include_router(image_processing.router)
app.include_router(profile_router)
#app.include_router(forget_router)

# Serve index.html for frontend
@app.get("/")
async def serve_index():
    index_path = os.path.join("fastapi_app", "frontend", "index.html")
    return FileResponse(index_path)

# Serve login.html page
@app.get("/login")
async def serve_login():
    login_path = os.path.join("fastapi_app", "frontend", "login.html")
    return FileResponse(login_path)

# Profile route (just as an example, it will retrieve user data)
@app.get("/profile")
async def serve_profile(request: Request):
    # Get token from cookies
    token = request.cookies.get("access_token")
    
    # If the token is not present, return an error
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Try to verify the token
    try:
        user_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # If verification is successful, serve the profile page
    profile_path = os.path.join("fastapi_app", "frontend", "profile.html")
    return FileResponse(profile_path)

# Mount static files for frontend assets (e.g., CSS, JS, images)
app.mount("/static", StaticFiles(directory="fastapi_app/frontend"), name="static")

# For loading profile images and other static files
app.mount("/media", StaticFiles(directory="fastapi_app/media"), name="media")

# For uploading and generating images
app.mount("/uploads", StaticFiles(directory="fastapi_app/uploads"), name="uploads")
app.mount("/generated", StaticFiles(directory="fastapi_app/generated"), name="generated")

# OAuth endpoints (Auth0 login)

@app.get("/login/google")
def login_google():
    return RedirectResponse(
        url=f"https://{AUTH0_DOMAIN}/authorize"
        f"?client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
        f"&response_type=code"
        f"&scope=openid profile email"
        f"&connection=google-oauth2"
    )

@app.get("/login/facebook")
def login_facebook():
    return RedirectResponse(
        url=f"https://{AUTH0_DOMAIN}/authorize"
        f"?client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
        f"&response_type=code"
        f"&scope=openid profile email"
        f"&connection=facebook"
    )


@app.get("/login/apple")
def login_apple():
    return RedirectResponse(
        url=f"https://{AUTH0_DOMAIN}/authorize"
        f"?client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
        f"&response_type=code"
        f"&scope=openid profile email"
        f"&connection=apple"
    )

# Route for fetching user profile data
# Convert the database query to an async operation
@sync_to_async
def get_user_by_email(email: str):
    try:
        return UserData.objects.get(email=email)
    except ObjectDoesNotExist:
        return None

@sync_to_async   
def get_user_by_userid(userid: str):
    try:
        return UserData.objects.get(userid=userid)
    except ObjectDoesNotExist:
        return None

@app.get("/get_profile")
async def get_profile(email: str = Query(...)):
    user = await get_user_by_email(email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the profile_pic is an image and return its URL or base64 encoded value
    profile_pic_url = None
    if user.profile_pic:
        profile_pic_url = f"{settings.MEDIA_URL}{user.profile_pic.name}"  # If you are serving the media files via FastAPI

    return JSONResponse(content={
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "location": user.location,
        "provider": user.provider,
        "profile_pic": profile_pic_url,
    })

# Route to fetch profile data using Facebook/Apple user ID
@app.get("/get_profile_by_userid")
async def get_profile_by_userid(userid: str = Query(...)):
    user = await get_user_by_userid(userid)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the profile_pic is an image and return its URL or base64 encoded value
    profile_pic_url = None
    if user.profile_pic:
        profile_pic_url = f"{settings.MEDIA_URL}{user.profile_pic.name}"  # If you are serving the media files via FastAPI

    return JSONResponse(content={
        "first_name": user.first_name,
        "last_name": user.last_name,
        "userid": user.userid,
        "email": user.email,
        "phone_number": user.phone_number,
        "location": user.location,
        "provider": user.provider,
        "profile_pic": profile_pic_url,
    })

#used for update profile page to access the token and show user mail or userid to froent end 
# Secret key and algorithm
SECRET_KEY = "asdfghjkl_cgcvcgcvc"  
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#for forget password
# Request Models

class ForgotRequest(BaseModel):
    email: str

class ResetRequest(BaseModel):
    email: str
    otp: str
    new_password: str
    confirm_password: str

# Response Models
class ForgotResponse(BaseModel):
    message: str
    debug_info: Optional[dict] = None



# Helper functions for database access (make them synchronous within the async context)
async def get_user_by_email(email: str):
    # This function should be run in a thread pool as Django ORM calls are synchronous
    def _get_user():
        try:
            return UserData.objects.get(email=email)
        except UserData.DoesNotExist:
            return None

    return await run_in_threadpool(_get_user)

@app.post("/forgot-password", response_model=ForgotResponse)
async def forgot_password(request: ForgotRequest):
    #Step 1: Send OTP to email
    # Check if email exists in DB
    user = await get_user_by_email(request.email)
    if not user:
        return ForgotResponse(message="If this email exists, an OTP was sent.")

    otp = OTPManager.generate_otp(request.email)
    return ForgotResponse(message="OTP sent to email", debug_info={"otp": otp if settings.DEBUG else "hidden"})


@app.post("/reset-password", response_model=ForgotResponse)
async def reset_password(request: ResetRequest):
    """Step 2: Verify OTP and update password"""
    # Check if email exists in DB
    user = await get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Step 1: Check if OTP is valid
    if not OTPManager.verify_otp(request.email, request.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Step 2: Check if new password and confirm password match
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Step 3: Save new password (hash it)
    hashed_pw = hashlib.sha256(request.new_password.encode()).hexdigest()

    # Save password in DB - must be done asynchronously
    def _save_password():
        user.password = hashed_pw
        user.save()

    # Run the saving function in a thread pool to avoid async issues
    await run_in_threadpool(_save_password)

    # Mark OTP as used
    OTPManager.mark_used(request.email)

    return ForgotResponse(message="Password updated successfully")"""
import os
import sys
from fastapi import FastAPI, HTTPException, Query, Request, status ,Depends, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse,Response
from fastapi_app.django_setup import django_setup
from fastapi_app.auth import router as auth_router
from fastapi_app import image_processing, auth
from fastapi_app.update_profile import router as profile_router
#from fastapi_app.forget_password import router as forget_router
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from jose import JWTError, jwt #used for update_profile.py
from datetime import datetime, timedelta #used for update_profile.py
from pydantic import BaseModel #used for forget_password
from fastapi_app.forget_password import OTPManager #used for forget_password
from django.contrib.auth.models import User #used for forget_password
from django.core.mail import send_mail #used for forget_password
from fastapi_app.config import settings #used for forget_password
from django.contrib.auth import get_user_model #used for forget_password
from typing import Optional #used for forget_password
from starlette.concurrency import run_in_threadpool #used for forget_password
import hashlib#used for forget_password
from fastapi_app.contact import router as contact_router #used for contact us
from fastapi_app import help_center #used for Help center 
from fastapi_app.pricing_page import create_subscription_for_user

#from fastapi import FastAPI, UploadFile, File, Form
#from fastapi.responses import Response
from fastapi_app.image_processing import router as image_router
from django.contrib.auth.hashers import make_password #used for reset password



# Ensure that the fastapi_app folder is in the sys.path for correct imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fastapi_app'))

# Set up Django
django_setup()
from appln.models import UserData

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")

# Initialize FastAPI app
app = FastAPI()

# Include authentication and image processing routers
app.include_router(auth_router, prefix="/auth")
app.include_router(auth.router)
app.include_router(image_router, prefix="/api", tags=["Image Generation"])
#app.include_router(image_processing.router)
app.include_router(profile_router)
app.include_router(contact_router)
app.include_router(help_center.router) 
#app.include_router(forget_router)

# Serve index.html for frontend
@app.get("/")
async def serve_index():
    index_path = os.path.join("fastapi_app", "frontend", "index.html")
    return FileResponse(index_path)

# Serve login.html page
@app.get("/login")
async def serve_login():
    login_path = os.path.join("fastapi_app", "frontend", "login.html")
    return FileResponse(login_path)

# Profile route (just as an example, it will retrieve user data)
@app.get("/profile")
async def serve_profile(request: Request):
    # Get token from cookies
    token = request.cookies.get("access_token")
    
    # If the token is not present, return an error
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Try to verify the token
    try:
        user_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # If verification is successful, serve the profile page
    profile_path = os.path.join("fastapi_app", "frontend", "profile.html")
    return FileResponse(profile_path)

# Mount static files for frontend assets (e.g., CSS, JS, images)
app.mount("/static", StaticFiles(directory="fastapi_app/frontend"), name="static")

# For loading profile images and other static files
app.mount("/media", StaticFiles(directory="fastapi_app/media"), name="media")

# For uploading and generating images
app.mount("/uploads", StaticFiles(directory="fastapi_app/uploads"), name="uploads")
app.mount("/generated", StaticFiles(directory="fastapi_app/generated"), name="generated")

# OAuth endpoints (Auth0 login)

@app.get("/login/google")
def login_google():
    return RedirectResponse(
        url=f"https://{AUTH0_DOMAIN}/authorize"
        f"?client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
        f"&response_type=code"
        f"&scope=openid profile email"
        f"&connection=google-oauth2"
    )

@app.get("/login/facebook")
def login_facebook():
    return RedirectResponse(
        url=f"https://{AUTH0_DOMAIN}/authorize"
        f"?client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
        f"&response_type=code"
        f"&scope=openid profile email"
        f"&connection=facebook"
    )


@app.get("/login/apple")
def login_apple():
    return RedirectResponse(
        url=f"https://{AUTH0_DOMAIN}/authorize"
        f"?client_id={AUTH0_CLIENT_ID}"
        f"&redirect_uri={AUTH0_CALLBACK_URL}"
        f"&response_type=code"
        f"&scope=openid profile email"
        f"&connection=apple"
    )

# Route for fetching user profile data
# Convert the database query to an async operation
@sync_to_async
def get_user_by_email(email: str):
    try:
        return UserData.objects.get(email=email)
    except ObjectDoesNotExist:
        return None

@sync_to_async   
def get_user_by_userid(userid: str):
    try:
        return UserData.objects.get(userid=userid)
    except ObjectDoesNotExist:
        return None

@app.get("/get_profile")
async def get_profile(email: str = Query(...)):
    user = await get_user_by_email(email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the profile_pic is an image and return its URL or base64 encoded value
    profile_pic_url = None
    if user.profile_pic:
        profile_pic_url = f"{settings.MEDIA_URL}{user.profile_pic.name}"  # If you are serving the media files via FastAPI

    return JSONResponse(content={
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "location": user.location,
        "provider": user.provider,
        "profile_pic": profile_pic_url,
    })

# Route to fetch profile data using Facebook/Apple user ID
@app.get("/get_profile_by_userid")
async def get_profile_by_userid(userid: str = Query(...)):
    user = await get_user_by_userid(userid)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the profile_pic is an image and return its URL or base64 encoded value
    profile_pic_url = None
    if user.profile_pic:
        profile_pic_url = f"{settings.MEDIA_URL}{user.profile_pic.name}"  # If you are serving the media files via FastAPI

    return JSONResponse(content={
        "first_name": user.first_name,
        "last_name": user.last_name,
        "userid": user.userid,
        "email": user.email,
        "phone_number": user.phone_number,
        "location": user.location,
        "provider": user.provider,
        "profile_pic": profile_pic_url,
    })

#used for update profile page to access the token and show user mail or userid to froent end 
# Secret key and algorithm
SECRET_KEY = "asdfghjkl_cgcvcgcvc"  
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#for forget password
# Request Models

class ForgotRequest(BaseModel):
    email: str

class ResetRequest(BaseModel):
    email: str
    otp: str
    new_password: str
    confirm_password: str

# Response Models
class ForgotResponse(BaseModel):
    message: str
    debug_info: Optional[dict] = None



# Helper functions for database access (make them synchronous within the async context)
async def get_user_by_email(email: str):
    # This function should be run in a thread pool as Django ORM calls are synchronous
    def _get_user():
        try:
            return UserData.objects.get(email=email)
        except UserData.DoesNotExist:
            return None

    return await run_in_threadpool(_get_user)

@app.post("/forgot-password", response_model=ForgotResponse)
async def forgot_password(request: ForgotRequest):
    """Step 1: Send OTP to email"""
    # Check if email exists in DB
    user = await get_user_by_email(request.email)
    if not user:
        return ForgotResponse(message="If this email exists, an OTP was sent.")

    otp = OTPManager.generate_otp(request.email)
    return ForgotResponse(message="OTP sent to email", debug_info={"otp": otp if settings.DEBUG else "hidden"})


@app.post("/reset-password", response_model=ForgotResponse)
async def reset_password(request: ResetRequest):
    """Reset password with OTP verification"""

    # Step 1: Check if user exists
    user = await get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Step 2: Verify OTP
    if not OTPManager.verify_otp(request.email, request.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Step 3: Check if passwords match
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Step 4: Hash new password using Django's `make_password`
    new_hashed_password = make_password(request.new_password)

    # Step 5: Save password to DB
    def _save_password():
        user.password = new_hashed_password
        user.save()

    await run_in_threadpool(_save_password)

    # Step 6: Mark OTP as used
    OTPManager.mark_used(request.email)

    return ForgotResponse(message="Password updated successfully")

@app.get("/")
async def root():
    return {"message": "Welcome to the Image Generation API!"}

