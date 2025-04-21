import os
import sys
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi_app.django_setup import django_setup
from fastapi_app.auth import router as auth_router
from fastapi_app import image_processing, auth
from fastapi_app.update_profile import router as profile_router
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist


from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Ensure that the fastapi_app folder is in the sys.path for correct imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fastapi_app'))

# Set up Django
django_setup()
from appln.models import UserData

# Initialize FastAPI app
app = FastAPI()

# Include authentication and image processing routers
app.include_router(auth_router, prefix="/auth")
app.include_router(auth.router)
app.include_router(image_processing.router)
app.include_router(profile_router)

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
async def serve_profile():
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
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "dev-58msavvh172405v3.us.auth0.com")
CLIENT_ID = os.getenv("AUTH0_CLIENT_ID", "fJT5VMzB7Puv4bmVvCFuEBCmRa5HZf5F")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/callback")

@app.get("/login/google")
def login_google():
    return RedirectResponse(
        url=f"https://{AUTH0_DOMAIN}/authorize"
            f"?client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=openid profile email"
            f"&connection=google-oauth2"
    )

@app.get("/login/facebook")
def login_facebook():
    return RedirectResponse(
        url=f"https://{AUTH0_DOMAIN}/authorize"
            f"?client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=openid profile email"
            f"&connection=facebook"
    )

@app.get("/login/apple")
def login_apple():
    return RedirectResponse(
        url=f"https://{AUTH0_DOMAIN}/authorize"
            f"?client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
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

@app.get("/get_profile")
async def get_profile(email: str = Query(...)):
    user = await get_user_by_email(email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return JSONResponse(content={
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone_number": user.phone_number,
        "location": user.location,
        "provider": user.provider,
        "profile_pic": user.profile_pic,
    })
