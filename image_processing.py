"""import os
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
        return hashlib.md5(f.read()).hexdigest()"""

"""import os
import shutil
import requests
import base64
import random
import time
import asyncio
import uuid
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
import io
import hashlib
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import math


load_dotenv()

app = FastAPI()
router = APIRouter(tags=["AI Design Transformation"])

# Create necessary directories on startup
os.makedirs("uploads", exist_ok=True)
os.makedirs("generated", exist_ok=True)

# Mount static files
app.mount("/generated", StaticFiles(directory="generated"), name="generated")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
if not STABILITY_API_KEY:
    raise RuntimeError("STABILITY_API_KEY environment variable not set")

STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image"

HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {STABILITY_API_KEY}",
}

# Enums for frontend options
class BuildingType(str, Enum):
    COMMERCIAL = "commercial"
    RESIDENTIAL = "residential"

class RoomType(str, Enum):
    LIVING_ROOM = "living room"
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    HOME_OFFICE = "home office"
    DINING_ROOM = "dining room"
    STUDY_ROOM = "study room"
    FAMILY_ROOM = "family room"
    KID_ROOM = "kid room"
    BALCONY = "balcony"

class DesignStyle(str, Enum):
    CLASSIC = "classic"
    MODERN = "modern"
    MINIMAL = "minimal"
    SCANDINAVIAN = "scandinavian"
    CONTEMPORARY = "contemporary"
    INDUSTRIAL = "industrial"
    JAPANDI = "japandi"
    BOHEMIAN = "bohemian"
    COASTAL = "coastal"
    MODERN_LUXURY = "modern luxury"
    TROPICAL_RESORT = "tropical resort"
    JAPANESE_ZEN = "japanese zen"

class AIStylingStrength(str, Enum):
    VERY_LOW = "very low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"



# Style configurations for interior
STYLE_CONFIGS = {
    "classic": {
        "prompt": "Classic {room_type} in a {building_type} with traditional furniture, ornate details, rich fabrics, elegant lighting, {style} style",
        "negative_prompt": "modern, minimalist, industrial, futuristic"
    },
    "modern": {
        "prompt": "Modern {room_type} in a {building_type} with clean lines, contemporary furniture, neutral palette, designer lighting, {style} style",
        "negative_prompt": "traditional, ornate, rustic, vintage"
    },
    "minimal": {
        "prompt": "Minimalist {room_type} in a {building_type} with clean lines, functional furniture, monochromatic palette, open space, {style} style",
        "negative_prompt": "cluttered, ornate, traditional, heavy"
    },
    "scandinavian": {
        "prompt": "Scandinavian {room_type} in a {building_type} with light wood, clean lines, functional furniture, natural light, hygge aesthetic, {style} style",
        "negative_prompt": "ornate, dark, heavy, cluttered"
    },
    "contemporary": {
        "prompt": "Contemporary {room_type} in a {building_type} with clean lines, mixed materials, neutral colors, designer lighting, {style} style",
        "negative_prompt": "traditional, rustic, vintage, ornate"
    },
    "industrial": {
        "prompt": "Industrial {room_type} in a {building_type} with exposed brick, metal accents, open space, modern lighting, urban style, {style} style",
        "negative_prompt": "traditional, floral, rustic, country"
    },
    "japandi": {
        "prompt": "Japandi {room_type} in a {building_type} with minimal decor, natural materials, neutral colors, zen atmosphere, {style} style",
        "negative_prompt": "cluttered, ornate, bright colors, western"
    },
    "bohemian": {
        "prompt": "Bohemian {room_type} in a {building_type} with eclectic mix of patterns, textures, plants, warm lighting, {style} style",
        "negative_prompt": "minimalist, sterile, modern"
    },
    "coastal": {
        "prompt": "Coastal {room_type} in a {building_type} with light colors, natural textures, nautical elements, airy atmosphere, {style} style",
        "negative_prompt": "dark, heavy, urban, industrial"
    },
    "modern luxury": {
        "prompt": "Luxury modern {room_type} in a {building_type} with designer furniture, premium materials, elegant lighting, 8K professional interior, {style} style",
        "negative_prompt": "cheap, cluttered, outdated, poor lighting"
    },
    "tropical resort": {
        "prompt": "Tropical {room_type} in a {building_type} with canopy bed, natural materials, lush greenery, resort-style luxury, {style} style",
        "negative_prompt": "urban, industrial, minimalist"
    },
    "japanese zen": {
        "prompt": "Japanese zen {room_type} in a {building_type} with tatami mats, shoji screens, minimal decor, peaceful atmosphere, {style} style",
        "negative_prompt": "western, cluttered, bright colors"
    }
}


# Optimized strength configuration
STRENGTH_CONFIG = {
    "very low": {"image_strength": 0.4, "steps": 20, "cfg_scale": 6},
    "low": {"image_strength": 0.3, "steps": 25, "cfg_scale": 7},
    "medium": {"image_strength": 0.2, "steps": 30, "cfg_scale": 8},
    "high": {"image_strength": 0.1, "steps": 35, "cfg_scale": 9}
}

ALLOWED_DIMENSIONS = [
    (1024, 1024), (1152, 896), (1216, 832), (1344, 768),
    (640, 1536), (768, 1344), (832, 1216), (896, 1152)
]

executor = ThreadPoolExecutor(max_workers=8)

async def resize_to_allowed_dimensions(image_path):
    """Optimized image resizing that preserves the original file"""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            aspect = width / height
            closest = min(ALLOWED_DIMENSIONS, 
                         key=lambda dim: abs((dim[0]/dim[1]) - aspect))
            
            if abs(width - closest[0]) < 100 and abs(height - closest[1]) < 100:
                with open(image_path, "rb") as f:
                    return f.read(), (width, height)
                    
            img = img.resize(closest, Image.LANCZOS)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG", optimize=True, quality=90)
            return img_bytes.getvalue(), closest
    except Exception as e:
        raise HTTPException(400, f"Image processing error: {str(e)}")

async def generate_design_variation(
    image_bytes: bytes,
    design_config: dict,
    strength_level: str
):
    """Optimized design generation with timeout"""
    async def _generate():
        try:
            params = STRENGTH_CONFIG[strength_level]
            style_config = STYLE_CONFIGS[design_config["style"]]
            
            prompt = style_config["prompt"].format(
                room_type=design_config["room_type"],
                building_type=design_config["building_type"],
                style=design_config["style"]
            )
            
            modifiers = ["professional design", "high quality", "detailed"]
            prompt += ", " + random.choice(modifiers)
            
            files = {
                "init_image": ("input.png", BytesIO(image_bytes), "image/png"),
            }
            
            data = {
                "init_image_mode": "IMAGE_STRENGTH",
                "image_strength": str(params["image_strength"]),
                "text_prompts[0][text]": prompt,
                "text_prompts[0][weight]": "1.2",
                "text_prompts[1][text]": style_config["negative_prompt"],
                "text_prompts[1][weight]": "-1.0",
                "cfg_scale": str(params["cfg_scale"]),
                "samples": "1",
                "steps": str(params["steps"]),
                "seed": str(random.randint(0, 100000)),
                "style_preset": "photographic"
            }

            try:
                response = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: requests.post(
                            STABILITY_API_URL,
                            headers=HEADERS,
                            files=files,
                            data=data,
                            timeout=45
                        )
                    ),
                    timeout=60
                )
            except asyncio.TimeoutError:
                raise HTTPException(504, "API request timed out")

            if response.status_code != 200:
                raise HTTPException(502, f"API Error: {response.status_code}")

            result = response.json()
            return result["artifacts"][0]
            
        except Exception as e:
            raise HTTPException(500, f"Generation error: {str(e)}")

    return await _generate()

@router.post("/generate-interior-design/")
async def generate_design(
    image: UploadFile = File(...),
    building_type: BuildingType = Form(...),
    room_type: RoomType = Form(...),
    design_style: DesignStyle = Form(...),
    ai_strength: AIStylingStrength = Form("medium"),
    num_designs: int = Form(1, ge=1, le=6)
    
):
    try:
        start_time = time.time()
        
        if num_designs < 1 or num_designs > 6:
            raise HTTPException(400, "Number of designs must be 1-6")
            
        # Save original uploaded file
        original_filename = f"original_{uuid.uuid4().hex}{os.path.splitext(image.filename)[1]}"
        original_path = os.path.join("uploads", original_filename)
        
        with open(original_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        
        # Process image
        image_bytes, _ = await resize_to_allowed_dimensions(original_path)
        
        # Prepare config
        design_config = {
            "style": design_style.value.lower(),
            "room_type": room_type.value,
            "building_type": building_type.value,
            
        }
        
        # Generate designs
        tasks = [
            generate_design_variation(
                image_bytes,
                design_config,
                ai_strength.value.lower()
            )
            for _ in range(num_designs)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Save results
        generated_files = []
        for result in results:
            filename = f"generated/{uuid.uuid4().hex}.png"
            with open(filename, "wb") as f:
                f.write(base64.b64decode(result["base64"]))
            generated_files.append(filename)
        
        return JSONResponse({
            "success": True,
            "time_elapsed": round(time.time() - start_time, 2),
            "original_image": f"/uploads/{original_filename}",
            "designs": [f"/generated/{os.path.basename(f)}" for f in generated_files]
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Unexpected error: {str(e)}")
    
# 1) House Angle: only Front, Back
class HouseAngle(str, Enum):
    FRONT = "front"
    BACK = "back"

# 2) Exterior Style choices as per your list
class ExteriorStyle(str, Enum):
    CLASSIC = "classic"
    MODERN = "modern"
    BOHEMIAN = "bohemian"
    COASTAL = "coastal"
    INTERNATIONAL = "international"
    ELEPHANT = "elephant"
    STONE_CLAD = "stone clad"
    GLASS_HOUSE = "glass house"
    RED_BRICK = "red brick"
    PAINTED_BRICK = "painted brick"
    WOOD_ACCENTS = "wood accents"
    INDUSTRIAL = "industrial"



# Prompt templates as provided (updated keys to match Enum names)
EXTERIOR_CONFIGS = {
    style: {
        "prompt": config["prompt"] + ", professional architectural rendering, ultra-detailed, 8K",
        "negative_prompt": config["negative_prompt"] + ", blurry, low quality, cropped"
    }
    for style, config in {
        "classic": {
            "prompt": "Classic {angle} view of house with symmetrical design, columns, traditional details",
            "negative_prompt": "modern, futuristic, industrial, asymmetrical"
        },
        "modern": {
            "prompt": "Modern {angle} view of house with clean lines, large windows, minimalist design",
            "negative_prompt": "traditional, ornate, rustic, vintage"
        },
        "bohemian": {
            "prompt": "Bohemian {angle} view of house with eclectic design, colorful elements, mixed patterns",
            "negative_prompt": "minimalist, sterile, uniform"
        },
        "coastal": {
            "prompt": "Coastal {angle} view of house with light colors, beachy vibe, large windows",
            "negative_prompt": "dark, heavy, urban, industrial"
        },
        "international": {
            "prompt": "International style {angle} view of house with geometric forms, flat roofs, open interior spaces",
            "negative_prompt": "traditional, ornate, rustic"
        },
        "elephant": {
            "prompt": "Luxury {angle} view of large modern house with expansive glass, clean lines, premium materials",
            "negative_prompt": "small, cramped, cheap materials"
        },
        "stone clad": {
            "prompt": "Stone-clad {angle} view of house with natural stone exterior, rustic yet modern design",
            "negative_prompt": "smooth, plain, industrial"
        },
        "glass house": {
            "prompt": "Glass house {angle} view with extensive glass walls, modern design, connection to nature",
            "negative_prompt": "opaque, traditional, small windows"
        },
        "red brick": {
            "prompt": "Red brick {angle} view of house with traditional brick exterior, classic design",
            "negative_prompt": "modern, smooth, industrial"
        },
        "painted brick": {
            "prompt": "Painted brick {angle} view of house with colorful brick exterior, modern twist on traditional",
            "negative_prompt": "unpainted, industrial, plain"
        },
        "wood accents": {
            "prompt": "{angle} view of house with natural wood accents, warm modern design",
            "negative_prompt": "cold, industrial, no wood"
        },
        "industrial": {
            "prompt": "Industrial {angle} view of house with exposed materials, metal accents, urban style",
            "negative_prompt": "traditional, rustic, ornate"
        }
    }.items()
}




EXTERIOR_STRENGTH_CONFIGS = {
    "very low": {"image_strength": 0.10, "steps": 20, "cfg_scale": 5},
    "low": {"image_strength": 0.11, "steps": 25, "cfg_scale": 6},
    "medium": {"image_strength": 0.12, "steps": 30, "cfg_scale": 7},
    "high": {"image_strength": 0.13, "steps": 35, "cfg_scale": 8}
}
def closest_allowed_size(width, height):
    return min(ALLOWED_DIMENSIONS, key=lambda size: abs(size[0] - width) + abs(size[1] - height))

async def process_uploaded_image(file: UploadFile):
    try:
        # Read and convert to RGB
        with Image.open(BytesIO(await file.read())) as img:
            img = img.convert("RGB")

            # Get original size
            original_width, original_height = img.size
            aspect_ratio = original_width / original_height

            # Start with 1024 width
            target_width = 1024
            target_height = int(target_width / aspect_ratio)

            # Find closest valid size from Stability AI's list
            target_width, target_height = closest_allowed_size(target_width, target_height)

            # Resize
            img = img.resize((target_width, target_height), Image.LANCZOS)

            # Save to buffer
            buffer = BytesIO()
            img.save(buffer, format="PNG", quality=95)
            return buffer.getvalue(), f"upload_{uuid.uuid4().hex}.png"

    except Exception as e:
        raise HTTPException(400, f"Image processing failed: {str(e)}")

async def generate_variation(image_bytes: bytes, prompt: str, negative_prompt: str, params: dict):
    try:
        image = Image.open(BytesIO(image_bytes))
        width, height = image.size
        
        # Use the exact dimensions from the processed image
        buf = BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)

        files = {"init_image": ("input.png", buf, "image/png")}
        data = {
            "init_image_mode": "IMAGE_STRENGTH",
            "image_strength": params["image_strength"],
            "text_prompts[0][text]": prompt,
            "text_prompts[0][weight]": 1.3,  # Increased for better adherence
            "text_prompts[1][text]": negative_prompt,
            "text_prompts[1][weight]": -1.1,
            "cfg_scale": params["cfg_scale"],
            "steps": params["steps"],
            "seed": random.randint(0, 999999),
            "style_preset": "enhance",
            
        }

        response = await asyncio.to_thread(
            requests.post,
            STABILITY_API_URL,
            headers=HEADERS,
            files=files,
            data=data,
            timeout=45  # Increased timeout
        )

        if response.status_code != 200:
            error_msg = response.json().get("message", response.text)
            raise HTTPException(502, f"AI API Error: {error_msg}")

        return response.json()["artifacts"][0]

    except Exception as e:
        raise HTTPException(500, f"Variation generation failed: {str(e)}")

def build_prompt(style_key: str, angle: str):
    style_config = EXTERIOR_CONFIGS[style_key]
    prompt = style_config["prompt"].format(angle=angle)
    negative_prompt = style_config["negative_prompt"]
    return prompt, negative_prompt

def round_to_multiple_of_64(x):
    return int(math.floor(x / 64) * 64)



@router.post("/generate/exterior", response_class=JSONResponse)
async def generate_exterior_design(
    image: UploadFile = File(..., description="High-quality photo of building"),
    angle: HouseAngle = Form(...),
    style: ExteriorStyle = Form(...),
    num_designs: int = Form(..., ge=1, le=12),
    ai_styling_strength: AIStylingStrength = Form(...)
):
    start_time = time.time()
    image_bytes, original_filename = await process_uploaded_image(image)

    style_key = style.value.lower()
    if style_key not in EXTERIOR_CONFIGS:
        raise HTTPException(400, f"Invalid style: {style_key}. Valid options are: {list(EXTERIOR_CONFIGS.keys())}")

    prompt, negative_prompt = build_prompt(style_key, angle.value)

    params = EXTERIOR_STRENGTH_CONFIGS[ai_styling_strength.value]

    results = await asyncio.gather(*[
        generate_variation(image_bytes, prompt, negative_prompt, params)
        for _ in range(num_designs)
    ])

    generated_files = []
    os.makedirs("generated", exist_ok=True)
    for result in results:
        if isinstance(result, Exception):
            continue
        filename = f"generated/{uuid.uuid4().hex}.png"
        with open(filename, "wb") as f:
            f.write(base64.b64decode(result["base64"]))
        generated_files.append(filename)

    if not generated_files:
        raise HTTPException(500, "All generation attempts failed")

    return {
        "status": "success",
        "time_elapsed": round(time.time() - start_time, 1),
        "original_image_url": f"/uploads/{original_filename}",
        "generated_designs": [f"/generated/{os.path.basename(f)}" for f in generated_files],
        "config": {
            "angle": angle.value,
            "style": style.value,
            "num_designs": num_designs,
            "ai_styling_strength": ai_styling_strength.value
        }
    }
app.include_router(router)"""

import os
import shutil
import requests
import base64
import random
import time
import asyncio
import uuid
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
import io
import hashlib
import aiohttp
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import math


load_dotenv()

app = FastAPI()
router = APIRouter()
app.include_router(router)

# Create necessary directories on startup
os.makedirs("uploads", exist_ok=True)
os.makedirs("generated", exist_ok=True)

# Mount static files
app.mount("/generated", StaticFiles(directory="generated"), name="generated")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
if not STABILITY_API_KEY:
    raise RuntimeError("STABILITY_API_KEY environment variable not set")

STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image"

HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {STABILITY_API_KEY}",
}

# Enums for frontend options
class BuildingType(str, Enum):
    COMMERCIAL = "commercial"
    RESIDENTIAL = "residential"

class RoomType(str, Enum):
    LIVING_ROOM = "living room"
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    HOME_OFFICE = "home office"
    DINING_ROOM = "dining room"
    STUDY_ROOM = "study room"
    FAMILY_ROOM = "family room"
    KID_ROOM = "kid room"
    BALCONY = "balcony"

class DesignStyle(str, Enum):
    CLASSIC = "classic"
    MODERN = "modern"
    MINIMAL = "minimal"
    SCANDINAVIAN = "scandinavian"
    CONTEMPORARY = "contemporary"
    INDUSTRIAL = "industrial"
    JAPANDI = "japandi"
    BOHEMIAN = "bohemian"
    COASTAL = "coastal"
    MODERN_LUXURY = "modern luxury"
    TROPICAL_RESORT = "tropical resort"
    JAPANESE_ZEN = "japanese zen"

class AIStylingStrength(str, Enum):
    VERY_LOW = "very low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"



# Style configurations for interior
STYLE_CONFIGS = {
    "classic": {
        "prompt": "Classic {room_type} in a {building_type} with traditional furniture, ornate details, rich fabrics, elegant lighting, {style} style",
        "negative_prompt": "modern, minimalist, industrial, futuristic"
    },
    "modern": {
        "prompt": "Modern {room_type} in a {building_type} with clean lines, contemporary furniture, neutral palette, designer lighting, {style} style",
        "negative_prompt": "traditional, ornate, rustic, vintage"
    },
    "minimal": {
        "prompt": "Minimalist {room_type} in a {building_type} with clean lines, functional furniture, monochromatic palette, open space, {style} style",
        "negative_prompt": "cluttered, ornate, traditional, heavy"
    },
    "scandinavian": {
        "prompt": "Scandinavian {room_type} in a {building_type} with light wood, clean lines, functional furniture, natural light, hygge aesthetic, {style} style",
        "negative_prompt": "ornate, dark, heavy, cluttered"
    },
    "contemporary": {
        "prompt": "Contemporary {room_type} in a {building_type} with clean lines, mixed materials, neutral colors, designer lighting, {style} style",
        "negative_prompt": "traditional, rustic, vintage, ornate"
    },
    "industrial": {
        "prompt": "Industrial {room_type} in a {building_type} with exposed brick, metal accents, open space, modern lighting, urban style, {style} style",
        "negative_prompt": "traditional, floral, rustic, country"
    },
    "japandi": {
        "prompt": "Japandi {room_type} in a {building_type} with minimal decor, natural materials, neutral colors, zen atmosphere, {style} style",
        "negative_prompt": "cluttered, ornate, bright colors, western"
    },
    "bohemian": {
        "prompt": "Bohemian {room_type} in a {building_type} with eclectic mix of patterns, textures, plants, warm lighting, {style} style",
        "negative_prompt": "minimalist, sterile, modern"
    },
    "coastal": {
        "prompt": "Coastal {room_type} in a {building_type} with light colors, natural textures, nautical elements, airy atmosphere, {style} style",
        "negative_prompt": "dark, heavy, urban, industrial"
    },
    "modern luxury": {
        "prompt": "Luxury modern {room_type} in a {building_type} with designer furniture, premium materials, elegant lighting, 8K professional interior, {style} style",
        "negative_prompt": "cheap, cluttered, outdated, poor lighting"
    },
    "tropical resort": {
        "prompt": "Tropical {room_type} in a {building_type} with canopy bed, natural materials, lush greenery, resort-style luxury, {style} style",
        "negative_prompt": "urban, industrial, minimalist"
    },
    "japanese zen": {
        "prompt": "Japanese zen {room_type} in a {building_type} with tatami mats, shoji screens, minimal decor, peaceful atmosphere, {style} style",
        "negative_prompt": "western, cluttered, bright colors"
    }
}


# Optimized strength configuration
STRENGTH_CONFIG = {
    "very low": {"image_strength": 0.4, "steps": 20, "cfg_scale": 6},
    "low": {"image_strength": 0.3, "steps": 25, "cfg_scale": 7},
    "medium": {"image_strength": 0.2, "steps": 30, "cfg_scale": 8},
    "high": {"image_strength": 0.1, "steps": 35, "cfg_scale": 9}
}

ALLOWED_DIMENSIONS = [
    (1024, 1024), (1152, 896), (1216, 832), (1344, 768),
    (640, 1536), (768, 1344), (832, 1216), (896, 1152)
]

executor = ThreadPoolExecutor(max_workers=8)

async def resize_to_allowed_dimensions(image_path):
    """Optimized image resizing that preserves the original file"""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            aspect = width / height
            closest = min(ALLOWED_DIMENSIONS, 
                         key=lambda dim: abs((dim[0]/dim[1]) - aspect))
            
            if abs(width - closest[0]) < 100 and abs(height - closest[1]) < 100:
                with open(image_path, "rb") as f:
                    return f.read(), (width, height)
                    
            img = img.resize(closest, Image.LANCZOS)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG", optimize=True, quality=90)
            return img_bytes.getvalue(), closest
    except Exception as e:
        raise HTTPException(400, f"Image processing error: {str(e)}")

async def generate_design_variation(
    image_bytes: bytes,
    design_config: dict,
    strength_level: str
):
    """Optimized design generation with timeout"""
    async def _generate():
        try:
            params = STRENGTH_CONFIG[strength_level]
            style_config = STYLE_CONFIGS[design_config["style"]]
            
            prompt = style_config["prompt"].format(
                room_type=design_config["room_type"],
                building_type=design_config["building_type"],
                style=design_config["style"]
            )
            
            modifiers = ["professional design", "high quality", "detailed"]
            prompt += ", " + random.choice(modifiers)
            
            files = {
                "init_image": ("input.png", BytesIO(image_bytes), "image/png"),
            }
            
            data = {
                "init_image_mode": "IMAGE_STRENGTH",
                "image_strength": str(params["image_strength"]),
                "text_prompts[0][text]": prompt,
                "text_prompts[0][weight]": "1.2",
                "text_prompts[1][text]": style_config["negative_prompt"],
                "text_prompts[1][weight]": "-1.0",
                "cfg_scale": str(params["cfg_scale"]),
                "samples": "1",
                "steps": str(params["steps"]),
                "seed": str(random.randint(0, 100000)),
                "style_preset": "photographic"
            }

            try:
                response = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: requests.post(
                            STABILITY_API_URL,
                            headers=HEADERS,
                            files=files,
                            data=data,
                            timeout=45
                        )
                    ),
                    timeout=60
                )
            except asyncio.TimeoutError:
                raise HTTPException(504, "API request timed out")

            if response.status_code != 200:
                raise HTTPException(502, f"API Error: {response.status_code}")

            result = response.json()
            return result["artifacts"][0]
            
        except Exception as e:
            raise HTTPException(500, f"Generation error: {str(e)}")

    return await _generate()

@router.post("/generate-interior-design/")
async def generate_design(
    image: UploadFile = File(...),
    building_type: BuildingType = Form(...),
    room_type: RoomType = Form(...),
    design_style: DesignStyle = Form(...),
    ai_strength: AIStylingStrength = Form("medium"),
    num_designs: int = Form(1, ge=1, le=6)
    
):
    try:
        start_time = time.time()
        
        if num_designs < 1 or num_designs > 6:
            raise HTTPException(400, "Number of designs must be 1-6")
            
        # Save original uploaded file
        original_filename = f"original_{uuid.uuid4().hex}{os.path.splitext(image.filename)[1]}"
        original_path = os.path.join("uploads", original_filename)
        
        with open(original_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        
        # Process image
        image_bytes, _ = await resize_to_allowed_dimensions(original_path)
        
        # Prepare config
        design_config = {
            "style": design_style.value.lower(),
            "room_type": room_type.value,
            "building_type": building_type.value,
            
        }
        
        # Generate designs
        tasks = [
            generate_design_variation(
                image_bytes,
                design_config,
                ai_strength.value.lower()
            )
            for _ in range(num_designs)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Save results
        generated_files = []
        for result in results:
            filename = f"generated/{uuid.uuid4().hex}.png"
            with open(filename, "wb") as f:
                f.write(base64.b64decode(result["base64"]))
            generated_files.append(filename)
        
        return JSONResponse({
            "success": True,
            "time_elapsed": round(time.time() - start_time, 2),
            "original_image": f"/uploads/{original_filename}",
            "designs": [f"/generated/{os.path.basename(f)}" for f in generated_files]
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Unexpected error: {str(e)}")
    
# 1) House Angle: only Front, Back
# 1) House Angle: only Front, Back
class HouseAngle(str, Enum):
    FRONT = "front"
    BACK = "back"
    LEFT = "Left side"
    RIGHT ="Right side"

# 2) Exterior Style choices as per your list
class ExteriorStyle(str, Enum):
    CLASSIC = "classic"
    MODERN = "modern"
    BOHEMIAN = "bohemian"
    COASTAL = "coastal"
    INTERNATIONAL = "international"
    ELEPHANT = "elephant"
    STONE_CLAD = "stone clad"
    GLASS_HOUSE = "glass house"
    RED_BRICK = "red brick"
    PAINTED_BRICK = "painted brick"
    WOOD_ACCENTS = "wood accents"
    INDUSTRIAL = "industrial"



# Prompt templates as provided (updated keys to match Enum names)
EXTERIOR_CONFIGS = {
    style: {
        "prompt": config["prompt"] + ", professional architectural rendering, ultra-detailed, 8K",
        "negative_prompt": config["negative_prompt"] + ", blurry, low quality, cropped"
    }
    for style, config in {
        "classic": {
            "prompt": "Classic {angle} view of house with symmetrical design, columns, traditional details",
            "negative_prompt": "modern, futuristic, industrial, asymmetrical"
        },
        "modern": {
            "prompt": "Modern {angle} view of house with clean lines, large windows, minimalist design",
            "negative_prompt": "traditional, ornate, rustic, vintage"
        },
        "bohemian": {
            "prompt": "Bohemian {angle} view of house with eclectic design, colorful elements, mixed patterns",
            "negative_prompt": "minimalist, sterile, uniform"
        },
        "coastal": {
            "prompt": "Coastal {angle} view of house with light colors, beachy vibe, large windows",
            "negative_prompt": "dark, heavy, urban, industrial"
        },
        "international": {
            "prompt": "International style {angle} view of house with geometric forms, flat roofs, open interior spaces",
            "negative_prompt": "traditional, ornate, rustic"
        },
        "elephant": {
            "prompt": "Luxury {angle} view of large modern house with expansive glass, clean lines, premium materials",
            "negative_prompt": "small, cramped, cheap materials"
        },
        "stone clad": {
            "prompt": "Stone-clad {angle} view of house with natural stone exterior, rustic yet modern design",
            "negative_prompt": "smooth, plain, industrial"
        },
        "glass house": {
            "prompt": "Glass house {angle} view with extensive glass walls, modern design, connection to nature",
            "negative_prompt": "opaque, traditional, small windows"
        },
        "red brick": {
            "prompt": "Red brick {angle} view of house with traditional brick exterior, classic design",
            "negative_prompt": "modern, smooth, industrial"
        },
        "painted brick": {
            "prompt": "Painted brick {angle} view of house with colorful brick exterior, modern twist on traditional",
            "negative_prompt": "unpainted, industrial, plain"
        },
        "wood accents": {
            "prompt": "{angle} view of house with natural wood accents, warm modern design",
            "negative_prompt": "cold, industrial, no wood"
        },
        "industrial": {
            "prompt": "Industrial {angle} view of house with exposed materials, metal accents, urban style",
            "negative_prompt": "traditional, rustic, ornate"
        }
    }.items()
}




"""EXTERIOR_STRENGTH_CONFIGS = {
    "very low": {"image_strength": 0.08, "steps": 20, "cfg_scale": 4},
    "low": {"image_strength": 0.10, "steps": 25, "cfg_scale": 5},
    "medium": {"image_strength": 0.13, "steps": 28, "cfg_scale": 6},
    "high": {"image_strength": 0.16, "steps": 30, "cfg_scale": 7}
}"""

EXTERIOR_STRENGTH_CONFIGS = {
    "very low": {"image_strength": 0.50, "steps": 35, "cfg_scale": 4},
    "low": {"image_strength": 0.45, "steps": 40, "cfg_scale": 5},
    "medium": {"image_strength": 0.40, "steps": 45, "cfg_scale": 6},
    "high": {"image_strength": 0.35, "steps": 50, "cfg_scale": 7}
}

def closest_allowed_size(width, height):
    return min(ALLOWED_DIMENSIONS, key=lambda size: abs(size[0] - width) + abs(size[1] - height))

async def process_uploaded_image(file: UploadFile):
    try:
        # Read and convert to RGB
        with Image.open(BytesIO(await file.read())) as img:
            img = img.convert("RGB")

            # Get original size
            original_width, original_height = img.size
            aspect_ratio = original_width / original_height

            # Start with 1024 width
            target_width = 1024
            target_height = int(target_width / aspect_ratio)

            # Find closest valid size from Stability AI's list
            target_width, target_height = closest_allowed_size(target_width, target_height)

            # Resize
            img = img.resize((target_width, target_height), Image.LANCZOS)

            # Save to buffer
            buffer = BytesIO()
            img.save(buffer, format="PNG", quality=95)
            return buffer.getvalue(), f"upload_{uuid.uuid4().hex}.png"

    except Exception as e:
        raise HTTPException(400, f"Image processing failed: {str(e)}")

async def generate_variation(image_bytes: bytes, prompt: str, negative_prompt: str, params: dict):
    try:
        image = Image.open(BytesIO(image_bytes))
        width, height = image.size

        buf = BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)

        files = {"init_image": ("input.png", buf, "image/png")}
        data = {
            "init_image_mode": "IMAGE_STRENGTH",
            "image_strength": params["image_strength"],  # Low strength = closer to original
            "text_prompts[0][text]": prompt,
            "text_prompts[0][weight]": 1.2,  # Not too strong
            "text_prompts[1][text]": negative_prompt,
            "text_prompts[1][weight]": -1.0,
            "cfg_scale": params["cfg_scale"],  # Controls prompt adherence
            "steps": params["steps"],  # Keep under 30 for realism
            "seed": random.randint(0, 999999),
            "style_preset": "photographic"  # Keeps it realistic, not too stylized
        }

        response = await asyncio.to_thread(
            requests.post,
            STABILITY_API_URL,
            headers=HEADERS,
            files=files,
            data=data,
            timeout=45
        )

        if response.status_code != 200:
            error_msg = response.json().get("message", response.text)
            raise HTTPException(502, f"AI API Error: {error_msg}")

        return response.json()["artifacts"][0]

    except Exception as e:
        raise HTTPException(500, f"Variation generation failed: {str(e)}")


def build_prompt(style_key: str, angle: str):
    style_config = EXTERIOR_CONFIGS[style_key]
    prompt = style_config["prompt"].format(angle=angle)
    negative_prompt = style_config["negative_prompt"]
    return prompt, negative_prompt

def round_to_multiple_of_64(x):
    return int(math.floor(x / 64) * 64)



@router.post("/generate/exterior", response_class=JSONResponse)
async def generate_exterior_design(
    image: UploadFile = File(..., description="High-quality photo of building"),
    angle: HouseAngle = Form(...),
    style: ExteriorStyle = Form(...),
    num_designs: int = Form(..., ge=1, le=12),
    ai_styling_strength: AIStylingStrength = Form(...)
):
    start_time = time.time()
    image_bytes, original_filename = await process_uploaded_image(image)

    style_key = style.value.lower()
    if style_key not in EXTERIOR_CONFIGS:
        raise HTTPException(400, f"Invalid style: {style_key}. Valid options are: {list(EXTERIOR_CONFIGS.keys())}")

    prompt, negative_prompt = build_prompt(style_key, angle.value)

    params = EXTERIOR_STRENGTH_CONFIGS[ai_styling_strength.value]

    results = await asyncio.gather(*[
        generate_variation(image_bytes, prompt, negative_prompt, params)
        for _ in range(num_designs)
    ])

    generated_files = []
    os.makedirs("generated", exist_ok=True)
    for result in results:
        if isinstance(result, Exception):
            continue
        filename = f"generated/{uuid.uuid4().hex}.png"
        with open(filename, "wb") as f:
            f.write(base64.b64decode(result["base64"]))
        generated_files.append(filename)

    if not generated_files:
        raise HTTPException(500, "All generation attempts failed")

    return {
        "status": "success",
        "time_elapsed": round(time.time() - start_time, 1),
        "original_image_url": f"/uploads/{original_filename}",
        "generated_designs": [f"/generated/{os.path.basename(f)}" for f in generated_files],
        "config": {
            "angle": angle.value,
            "style": style.value,
            "num_designs": num_designs,
            "ai_styling_strength": ai_styling_strength.value
        }
    }


#out door 
class OutdoorSpaceType(str, Enum):
    FRONT_YARD = "front yard"
    BACKYARD = "backyard"
    BALCONY = "balcony"
    TERRACE_ROOFTOP = "terrace rooftop"
    DRIVEWAY_PARKING = "driveway parking"
    WALKWAY_PATH = "walkway path"
    LOUNGE = "lounge"
    PORCH = "porch"
    FENCE = "fence"
    GARDEN = "garden"

class OutdoorDesignStyle(str, Enum):
    MODERN = "modern"
    CONTEMPORARY = "contemporary"
    TRADITIONAL = "traditional"
    RUSTIC = "rustic"
    SCANDINAVIAN = "scandinavian"
    CLASSIC_GARDEN = "classic garden"
    COASTAL_OUTDOOR = "coastal outdoor"
    FARMHOUSE = "farmhouse"
    COTTAGE_GARDEN = "cottage garden"
    INDUSTRIAL = "industrial"
    BEACH = "beach"

OUTDOOR_STRENGTH_CONFIG = {
    "very low": {"image_strength": 0.55, "steps": 35, "cfg_scale": 9},
    "low": {"image_strength": 0.50, "steps": 40, "cfg_scale": 10},
    "medium": {"image_strength": 0.45, "steps": 45, "cfg_scale": 11},
    "high": {"image_strength": 0.40, "steps": 50, "cfg_scale": 12}
}

# Style configurations for outdoor
OUTDOOR_STYLE_CONFIGS = {
    "modern": {
        "prompt": "Modern {space_type} with clean lines, sleek outdoor furniture, minimal landscaping, {style} style",
        "negative_prompt": "traditional, rustic, cluttered, overgrown"
    },
    "contemporary": {
        "prompt": "Contemporary {space_type} with innovative layout, stylish materials, modern lighting, {style} style",
        "negative_prompt": "vintage, outdated, chaotic, dark"
    },
    "traditional": {
        "prompt": "Traditional {space_type} with classic landscaping, balanced design, cozy seating, {style} style",
        "negative_prompt": "futuristic, industrial, minimalist"
    },
    "rustic": {
        "prompt": "Rustic {space_type} with natural wood, stone elements, vintage charm, cozy vibes, {style} style",
        "negative_prompt": "modern, polished, synthetic"
    },
    "scandinavian": {
        "prompt": "Scandinavian {space_type} with clean simplicity, light wood, minimalism, natural tones, {style} style",
        "negative_prompt": "ornate, cluttered, industrial"
    },
    "classic garden": {
        "prompt": "Classic garden {space_type} with symmetrical layout, trimmed hedges, elegant planters, {style} style",
        "negative_prompt": "wild, messy, futuristic"
    },
    "coastal outdoor": {
        "prompt": "Coastal {space_type} with ocean-inspired tones, light textures, airy seating, beachy plants, {style} style",
        "negative_prompt": "dark, urban, heavy"
    },
    "farmhouse": {
        "prompt": "Farmhouse-style {space_type} with natural wood, reclaimed elements, vintage accessories, {style} style",
        "negative_prompt": "sleek, modern, artificial"
    },
    "cottage garden": {
        "prompt": "Cottage garden {space_type} with colorful flowers, curving paths, storybook charm, {style} style",
        "negative_prompt": "structured, minimalist, modern"
    },
    "industrial": {
        "prompt": "Industrial {space_type} with exposed concrete, metal structures, bold lighting, urban design, {style} style",
        "negative_prompt": "floral, vintage, traditional"
    },
    "beach": {
        "prompt": "Beach-style {space_type} with sandy textures, driftwood decor, relaxed seating, breezy colors, {style} style",
        "negative_prompt": "formal, sharp, dark"
    }
}


async def generate_outdoor_design_variation(
    image_bytes: bytes,
    design_config: dict,
    strength_level: str
):
    """Optimized outdoor design generation with enhanced prompts and parameters"""
    async def _generate():
        try:
            params = OUTDOOR_STRENGTH_CONFIG[strength_level]
            style_config = OUTDOOR_STYLE_CONFIGS[design_config["style"]]
            
            # Enhanced prompt formatting for outdoor spaces
            prompt = style_config["prompt"].format(
                space_type=design_config["space_type"].replace("_", " "),
                style=design_config["style"].replace("_", " ").title()
            )
            
            # Outdoor-specific prompt enhancements
            outdoor_modifiers = [
                "professional landscape design",
                "high quality 3D rendering",
                "detailed garden planning",
                "realistic outdoor lighting",
                "natural materials",
                "seasonal plants"
            ]
            
            prompt += ", " + random.choice(outdoor_modifiers)
            
            # Outdoor-specific negative prompt enhancements
            negative_prompt = style_config["negative_prompt"] + ", " + \
                "distorted perspective, unnatural lighting, poor landscaping, " + \
                "unrealistic plants, bad proportions"
            
            files = {
                "init_image": ("input.png", BytesIO(image_bytes), "image/png"),
            }
            
            # Outdoor-optimized parameters
            data = {
                "init_image_mode": "IMAGE_STRENGTH",
                "image_strength": str(params["image_strength"]),
                "text_prompts[0][text]": prompt,
                "text_prompts[0][weight]": "1.2",  # Stronger focus on prompt
                "text_prompts[1][text]": negative_prompt,
                "text_prompts[1][weight]": "-1.0",
                "cfg_scale": str(params["cfg_scale"]),
                "samples": "1",
                "steps": str(params["steps"]),
                "seed": str(random.randint(0, 100000)),
                "style_preset": "photographic",  # Sharper, more realistic
                "sampler": "K_EULER_ANCESTRAL"   # Cleaner image edges (if supported)
                }

            # Outdoor-specific quality boost
            if design_config["space_type"] in ["garden", "backyard", "front yard"]:
                data["text_prompts[0][weight]"] = "1.4"
                data["steps"] = str(int(params["steps"]) + 5)

            try:
                response = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: requests.post(
                            STABILITY_API_URL,
                            headers=HEADERS,
                            files=files,
                            data=data,
                            timeout=60  # Increased timeout for complex outdoor scenes
                        )
                    ),
                    timeout=75
                )
            except asyncio.TimeoutError:
                raise HTTPException(504, "API request timed out")

            if response.status_code != 200:
                error_msg = response.text if response.text else "No error details"
                raise HTTPException(502, f"API Error: {response.status_code} - {error_msg}")

            result = response.json()
            if not result.get("artifacts"):
                raise HTTPException(502, "No artifacts returned from API")
                
            return result["artifacts"][0]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Outdoor generation error: {str(e)}")

    return await _generate()
    
@router.post("/generate-outdoor-design/")
async def generate_outdoor_design(
    image: UploadFile = File(...),
    space_type: OutdoorSpaceType = Form(...),
    design_style: OutdoorDesignStyle = Form(...),
    ai_strength: AIStylingStrength = Form("medium"),
    num_designs: int = Form(1, ge=1, le=12)
):
    try:
        start_time = time.time()
        
        if num_designs < 1 or num_designs > 12:
            raise HTTPException(400, "Number of designs must be 1-12")
            
        # Save original uploaded file
        original_filename = f"original_{uuid.uuid4().hex}{os.path.splitext(image.filename)[1]}"
        original_path = os.path.join("uploads", original_filename)
        
        with open(original_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        
        # Process image
        image_bytes, _ = await resize_to_allowed_dimensions(original_path)
        
        # Prepare config
        design_config = {
            "style": design_style.value,
            "space_type": space_type.value,
        }
        
        # Generate designs using the outdoor-specific function
        tasks = [
            generate_outdoor_design_variation(
                image_bytes,
                design_config,
                ai_strength.value
            )
            for _ in range(num_designs)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Save results
        generated_files = []
        for result in results:
            filename = f"generated/{uuid.uuid4().hex}.png"
            with open(filename, "wb") as f:
                f.write(base64.b64decode(result["base64"]))
            generated_files.append(filename)

        
        
        return JSONResponse({
            "success": True,
            "time_elapsed": round(time.time() - start_time, 2),
            "original_image": f"/uploads/{original_filename}",
            "designs": [f"/generated/{os.path.basename(f)}" for f in generated_files],
            "metadata": {
                "space_type": space_type.value,
                "design_style": design_style.value,
                "num_designs": num_designs,
                "styling_strength": ai_strength.value
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Unexpected error: {str(e)}")


    


