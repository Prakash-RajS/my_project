from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

import os
# Import routers for auth and image processing
from fastapi_app.auth import router as auth_router
from fastapi_app import image_processing, auth # Import separately for clarity

from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Auth routes (login/signup)
app.include_router(auth_router, prefix="/auth")
app.include_router(auth.router)

# Image processing routes (upload/generate)
app.include_router(image_processing.router)

# Serve index.html for frontend
@app.get("/")
async def serve_index():
    index_path = os.path.join("fastapi_app", "frontend", "index.html")
    print(f"Serving index from: {index_path}")  # Print to check file path
    return FileResponse(index_path)


# Mount static files for frontend assets (e.g., CSS, JS, images)
#app.mount("/static", StaticFiles(directory="fastapi_app/frontend/static"), name="static")

# Mount image folders to serve uploaded and generated images
app.mount("/uploads", StaticFiles(directory="fastapi_app/uploads"), name="uploads")
app.mount("/generated", StaticFiles(directory="fastapi_app/generated"), name="generated")

AUTH0_DOMAIN = "dev-58msavvh172405v3.us.auth0.com"
CLIENT_ID = "fJT5VMzB7Puv4bmVvCFuEBCmRa5HZf5F"
REDIRECT_URI = "http://localhost:8000/callback"

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

