import os
import shutil
import requests
import base64
import random
import time
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from PIL import Image
import io
import hashlib

load_dotenv()

router = APIRouter(tags=["AI Design Transformation"])

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image"

HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {STABILITY_API_KEY}",
}

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
        
        # Find closest allowed dimensions
        closest = min(ALLOWED_DIMENSIONS, 
                     key=lambda dim: abs((dim[0]/dim[1]) - aspect))
        
        # Resize with high-quality downsampling
        img = img.resize(closest, Image.LANCZOS)
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG", quality=95)
        img_bytes.seek(0)
        
        return img_bytes, closest

def file_hash(filepath):
    """Generate MD5 hash of a file to verify transformation"""
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

@router.post("/transform-to-modern-design/",
             summary="Transform room image to modern design",
             description="Upload a room photo to generate an AI-enhanced modern interior design")
async def transform_to_modern_design(
    room_image: UploadFile = File(..., description="Original room photo to transform"),
    style_prompt: str = Form(
        "A luxurious modern bedroom with king-size bed, floor-to-ceiling windows, contemporary furniture, warm ambient lighting, high-end materials, 4K realistic interior design",
        description="Detailed style description"
    )
):
    try:
        # 1. Save original image
        os.makedirs("uploads", exist_ok=True)
        os.makedirs("generated", exist_ok=True)
        
        input_path = os.path.join("uploads", room_image.filename)
        with open(input_path, "wb") as f:
            shutil.copyfileobj(room_image.file, f)

        # 2. Resize to API requirements
        resized_img, new_size = resize_to_allowed_dimensions(input_path)

        # 3. Enhanced prompt engineering
        enhanced_prompt = (
            f"{style_prompt}, ultra-realistic, architectural visualization, "
            "professional interior design, magazine quality, 8K resolution"
        )
        
        negative_prompt = (
            "blurry, low quality, distorted, cluttered, outdated furniture, "
            "poor lighting, empty room, unrealistic proportions"
        )

        # 4. Prepare API request
        files = {"init_image": (room_image.filename, resized_img, "image/png")}
        
        payload = {
            "init_image_mode": "IMAGE_STRENGTH",
            "image_strength": 0.35,  # Strong transformation
            "text_prompts[0][text]": enhanced_prompt,
            "text_prompts[0][weight]": 1.5,  # Stronger weight
            "text_prompts[1][text]": negative_prompt,
            "text_prompts[1][weight]": -1.0,
            "cfg_scale": 10,  # Strong prompt adherence
            "samples": 1,
            "steps": 50,  # More refinement
            "seed": random.randint(0, 10000),
            "style_preset": "photographic"
        }

        # 5. Call Stability AI API
        response = requests.post(
            STABILITY_API_URL,
            headers=HEADERS,
            files=files,
            data=payload,
            timeout=30
        )

        # 6. Process and verify results
        if response.status_code == 200:
            result = response.json()
            artifact = result["artifacts"][0]
            
            # Generate unique output filename
            timestamp = int(time.time())
            output_filename = f"modern_{timestamp}_{room_image.filename}"
            output_path = os.path.join("generated", output_filename)
            
            # Save transformed image
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(artifact["base64"]))
            
            # Verify transformation occurred
            input_hash = file_hash(input_path)
            output_hash = file_hash(output_path)
            is_transformed = (input_hash != output_hash)
            
            return {
                "success": True,
                "transformed": is_transformed,
                "original_size": Image.open(input_path).size,
                "processed_size": new_size,
                "output_path": output_path,
                "prompt_used": enhanced_prompt,
                "parameters": {
                    "image_strength": payload["image_strength"],
                    "steps": payload["steps"],
                    "cfg_scale": payload["cfg_scale"]
                }
            }
        else:
            error_msg = response.json().get("message", "Unknown API error")
            raise HTTPException(
                status_code=500,
                detail=f"Stability AI Error: {error_msg}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Processing error: {str(e)}"
        )
