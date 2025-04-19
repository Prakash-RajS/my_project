# fastapi_app/image_processing.py

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import os
import shutil
from PIL import Image, ImageFilter
import uuid

router = APIRouter()

UPLOAD_DIR = "fastapi_app/uploads"
GENERATED_DIR = "fastapi_app/generated"

# Create folders if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

@router.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    # Save uploaded image
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    upload_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Simulate AI processing (apply a blur filter)
    img = Image.open(upload_path)
    processed_img = img.filter(ImageFilter.GaussianBlur(radius=3))

    # Save generated image
    generated_filename = f"generated_{filename}"
    generated_path = os.path.join(GENERATED_DIR, generated_filename)
    processed_img.save(generated_path)

    return {
        "uploaded_image_url": f"/uploads/{filename}",
        "generated_image_url": f"/generated/{generated_filename}"
    }

@router.get("/generated/{filename}")
async def get_generated_image(filename: str):
    file_path = os.path.join(GENERATED_DIR, filename)
    return FileResponse(file_path)

@router.get("/uploads/{filename}")
async def get_uploaded_image(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    return FileResponse(file_path)
