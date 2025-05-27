import os
import shutil
import requests
import base64
import random
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from PIL import Image
import io
import hashlib
from typing import List

load_dotenv()

router = APIRouter(tags=["AI Design Transformation"])

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image"

HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {STABILITY_API_KEY}",
}

# Design variations with different styles
DESIGN_VARIANTS = [
    {
        "name": "Modern Luxury",
        "prompt": "A luxurious modern bedroom with king-size bed, floor-to-ceiling windows, contemporary furniture, warm ambient lighting, high-end materials, 4K realistic interior design",
        "negative_prompt": "blurry, low quality, distorted, cluttered, outdated furniture, poor lighting"
    },
    {
        "name": "Minimalist Scandinavian",
        "prompt": "Scandinavian minimalist bedroom with light wood furniture, cozy textiles, functional design, natural light, hygge aesthetic",
        "negative_prompt": "ornate, dark colors, heavy drapes, cluttered"
    },
    {
        "name": "Industrial Chic",
        "prompt": "Industrial loft bedroom with exposed brick walls, metal accents, open space, modern lighting fixtures, urban chic design",
        "negative_prompt": "traditional, floral patterns, rustic, country style"
    }
]

# Allowed dimensions for SDXL
ALLOWED_DIMENSIONS = [
    (1024, 1024), (1152, 896), (1216, 832), (1344, 768), (1536, 640),
    (640, 1536), (768, 1344), (832, 1216), (896, 1152)
]

def resize_to_allowed_dimensions(image_path):
    """Resize image to nearest allowed dimensions while maintaining aspect ratio"""
    with Image.open(image_path) as img:
        width, height = img.size
        aspect = width / height
        
        closest = min(ALLOWED_DIMENSIONS, 
                     key=lambda dim: abs((dim[0]/dim[1]) - aspect))
        
        img = img.resize(closest, Image.LANCZOS)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG", quality=95)
        img_bytes.seek(0)
        
        return img_bytes, closest

def generate_design(image_bytes: io.BytesIO, design_config: dict):
    """Generate a single design variation"""
    payload = {
        "init_image_mode": "IMAGE_STRENGTH",
        "image_strength": 0.35,
        "text_prompts[0][text]": design_config["prompt"],
        "text_prompts[0][weight]": 1.5,
        "text_prompts[1][text]": design_config["negative_prompt"],
        "text_prompts[1][weight]": -1.0,
        "cfg_scale": 10,
        "samples": 1,
        "steps": 50,
        "seed": random.randint(0, 10000),
        "style_preset": "photographic"
    }

    response = requests.post(
        STABILITY_API_URL,
        headers=HEADERS,
        files={"init_image": ("input.png", image_bytes, "image/png")},
        data=payload,
        timeout=30
    )

    if response.status_code == 200:
        return response.json()["artifacts"][0]
    raise Exception(f"API Error: {response.text}")

@router.post("/generate-designs")
async def generate_designs(
    room_image: UploadFile = File(..., description="Room image to transform"),
    num_designs: int = Form(1, description="Number of designs to generate (1-3)", ge=1, le=3)
):
    try:
        # 1. Save and process original image
        os.makedirs("uploads", exist_ok=True)
        os.makedirs("generated", exist_ok=True)
        
        input_path = os.path.join("uploads", room_image.filename)
        with open(input_path, "wb") as f:
            shutil.copyfileobj(room_image.file, f)

        resized_img, new_size = resize_to_allowed_dimensions(input_path)
        input_hash = file_hash(input_path)

        # 2. Generate requested number of designs
        results = []
        timestamp = int(time.time())
        
        # Select random design variants (without repeating)
        selected_variants = random.sample(DESIGN_VARIANTS, num_designs)
        
        for i, variant in enumerate(selected_variants):
            # Reset file pointer for each generation
            resized_img.seek(0)
            
            # Generate design
            artifact = generate_design(resized_img, variant)
            
            # Save result
            output_filename = f"design_{timestamp}_{variant['name'].lower().replace(' ', '_')}_{i}.png"
            output_path = os.path.join("generated", output_filename)
            
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(artifact["base64"]))
            
            # Verify transformation
            output_hash = file_hash(output_path)
            
            results.append({
                "style": variant["name"],
                "image_url": f"/generated/{output_filename}",
                "transformed": (input_hash != output_hash),
                "seed": artifact["seed"]
            })

        return {
            "success": True,
            "original_size": Image.open(input_path).size,
            "processed_size": new_size,
            "designs": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Processing error: {str(e)}"
        )

def file_hash(filepath):
    """Generate MD5 hash of a file"""
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()
