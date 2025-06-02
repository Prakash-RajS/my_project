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
from pathlib import Path



load_dotenv()

app = FastAPI()
BASE_DIR = Path(__file__).parent.parent  # Goes up one level from fastapi_app/

# Define paths
uploads_path = BASE_DIR / "fastapi_app" / "uploads"
generated_path = BASE_DIR / "fastapi_app" / "generated"

# Create folders if they don't exist
uploads_path.mkdir(parents=True, exist_ok=True)
generated_path.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static_uploads", StaticFiles(directory=uploads_path), name="static_uploads")
app.mount("/static_generated", StaticFiles(directory=generated_path), name="static_generated")


router = APIRouter()
app.include_router(router)

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
    building_type: str = Form(...),
    room_type: str = Form(...),
    design_style: str = Form(...),
    ai_strength: str = Form("medium"),
    num_designs: int = Form(1, ge=1, le=6)
):
    try:
        # Use the same paths defined globally
        from pathlib import Path

        BASE_DIR = Path(__file__).parent.parent
        uploads_dir = BASE_DIR / "fastapi_app" / "uploads"
        generated_dir = BASE_DIR / "fastapi_app" / "generated"

        # Save original file
        file_ext = os.path.splitext(image.filename)[1]
        original_filename = f"original_{uuid.uuid4().hex}{file_ext}"
        original_path = uploads_dir / original_filename

        with open(original_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        # Resize/process image
        image_bytes, _ = await resize_to_allowed_dimensions(str(original_path))

        design_config = {
            "style": design_style,
            "room_type": room_type,
            "building_type": building_type
        }

        tasks = [
            generate_design_variation(
                image_bytes,
                design_config,
                ai_strength
            ) for _ in range(num_designs)
        ]

        results = await asyncio.gather(*tasks)

        # Save results
        generated_urls = []
        for result in results:
            filename = f"generated_{uuid.uuid4().hex}.png"
            filepath = generated_dir / filename
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(result["base64"]))
            generated_urls.append(f"/static_generated/{filename}")
            print("Generated Path:", generated_path)


        return {
            
            "success": True,
            "original_image": f"/static_uploads/{original_filename}",
            "designs": generated_urls,
            "message": "Designs generated successfully"
            
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    
# 1) House Angle: only Front, Back
#exterior 
class HouseAngle(str, Enum):
    FRONT = "Front side"
    BACK = "Back side"
    LEFT = "Left side"
    RIGHT = "Right side"

class ExteriorDesignStyle(str, Enum):
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

EXTERIOR_STYLE_CONFIGS = {
    "classic": {
        "prompt": "Classic {angle} view of house with symmetrical design, columns, traditional details, professional architectural rendering, ultra-detailed, 8K",
        "negative_prompt": "modern, futuristic, industrial, asymmetrical, blurry, low quality, cropped"
    },
    "modern": {
        "prompt": "Modern {angle} view of house with clean lines, large windows, minimalist design, professional architectural rendering, ultra-detailed, 8K",
        "negative_prompt": "traditional, ornate, rustic, vintage, blurry, low quality, cropped"
    },
    "bohemian": {
        "prompt": "Bohemian {angle} view of house with eclectic design, colorful elements, mixed patterns, professional architectural rendering, ultra-detailed, 8K",
        "negative_prompt": "minimalist, sterile, uniform, blurry, low quality, cropped"
    },
    "coastal": {
        "prompt": "Coastal {angle} view of house with light colors, beachy vibe, large windows, professional architectural rendering, ultra-detailed, 8K",
        "negative_prompt": "dark, heavy, urban, industrial, blurry, low quality, cropped"
    },
    "international": {
        "prompt": "International style {angle} view of house with geometric forms, flat roofs, open interior spaces, professional architectural rendering, ultra-detailed, 8K",
        "negative_prompt": "traditional, ornate, rustic, blurry, low quality, cropped"
    },
    "elephant": {
        "prompt": "Luxury {angle} view of large modern house with expansive glass, clean lines, premium materials, professional architectural rendering, ultra-detailed, 8K",
        "negative_prompt": "small, cramped, cheap materials, blurry, low quality, cropped"
    },
    "stone clad": {
        "prompt": "Stone-clad {angle} view of house with natural stone exterior, rustic yet modern design, professional architectural rendering, ultra-detailed, 8K",
        "negative_prompt": "smooth, plain, industrial, blurry, low quality, cropped"
    },
    "glass house": {
        "prompt": "Glass house {angle} view with extensive glass walls, modern design, connection to nature, professional architectural rendering, ultra-detailed, 8K",
        "negative_prompt": "opaque, traditional, small windows, blurry, low quality, cropped"
    },
    "red brick": {
        "prompt": "Red brick {angle} view of house with traditional brick exterior, classic design, professional architectural rendering, ultra-detailed, 8K",
        "negative_prompt": "modern, smooth, industrial, blurry, low quality, cropped"
    },
    "painted brick": {
        "prompt": "Painted brick {angle} view of house with colorful brick exterior, modern twist on traditional, professional architectural rendering, ultra-detailed, 8K",
        "negative_prompt": "unpainted, industrial, plain, blurry, low quality, cropped"
    },
    "wood accents": {
        "prompt": "{angle} view of house with natural wood accents, warm modern design, professional architectural rendering, ultra-detailed, 8K",
        "negative_prompt": "cold, industrial, no wood, blurry, low quality, cropped"
    },
    "industrial": {
        "prompt": "Industrial {angle} view of house with exposed materials, metal accents, urban style, professional architectural rendering, ultra-detailed, 8K",
        "negative_prompt": "traditional, rustic, ornate, blurry, low quality, cropped"
    }
}

EXTERIOR_STRENGTH_CONFIG = {
    "very low": {"image_strength": 0.40, "steps": 35, "cfg_scale": 4},
    "low": {"image_strength": 0.35, "steps": 40, "cfg_scale": 5},
    "medium": {"image_strength": 0.30, "steps": 45, "cfg_scale": 6},
    "high": {"image_strength": 0.25, "steps": 50, "cfg_scale": 7}
}

"""EXTERIOR_STRENGTH_CONFIGS = {
    "very low": {"image_strength": 0.08, "steps": 20, "cfg_scale": 4},
    "low": {"image_strength": 0.10, "steps": 25, "cfg_scale": 5},
    "medium": {"image_strength": 0.13, "steps": 28, "cfg_scale": 6},
    "high": {"image_strength": 0.16, "steps": 30, "cfg_scale": 7}
}"""


async def generate_exterior_design_variation(
    image_bytes: bytes,
    design_config: dict,
    strength_level: str
):
    """Generate exterior design variation with proper aiohttp file upload"""
    try:
        # Validate strength level
        if strength_level.lower() not in EXTERIOR_STRENGTH_CONFIG:
            raise ValueError(f"Invalid strength level: {strength_level}")

        params = EXTERIOR_STRENGTH_CONFIG[strength_level.lower()]
        
        # Validate design style
        style = design_config["style"].lower()
        if style not in EXTERIOR_STYLE_CONFIGS:
            raise ValueError(f"Invalid design style: {style}")

        style_config = EXTERIOR_STYLE_CONFIGS[style]
        
        # Format prompt
        try:
            prompt = style_config["prompt"].format(
                angle=design_config["angle"],
                style=style
            )
        except KeyError as e:
            raise ValueError(f"Missing key in prompt formatting: {str(e)}")

        # Add random modifier
        modifiers = [
            "perfect lighting", "architectural digest quality", 
            "hyper-realistic", "highly detailed textures",
            "magazine cover quality", "award-winning design",
            "golden hour lighting", "professional 3D rendering",
            "ultra HD", "8K resolution"
        ]
        prompt += ", " + random.choice(modifiers)

        # Prepare multipart form data
        data = aiohttp.FormData()
        data.add_field('init_image', 
                     image_bytes, 
                     filename='input.png',
                     content_type='image/png')
        data.add_field('init_image_mode', 'IMAGE_STRENGTH')
        data.add_field('image_strength', str(params["image_strength"]))
        data.add_field('text_prompts[0][text]', prompt)
        data.add_field('text_prompts[0][weight]', '1.2')
        data.add_field('text_prompts[1][text]', style_config["negative_prompt"])
        data.add_field('text_prompts[1][weight]', '-1.0')
        data.add_field('cfg_scale', str(params["cfg_scale"]))
        data.add_field('samples', '1')
        data.add_field('steps', str(params["steps"]))
        data.add_field('seed', str(random.randint(0, 100000)))
        data.add_field('style_preset', 'photographic')

        # Make API request with timeout
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    STABILITY_API_URL,
                    headers=HEADERS,
                    data=data,
                    timeout=60
                ) as response:
                    if response.status != 200:
                        error_detail = await response.text()
                        raise ValueError(
                            f"API returned status {response.status}: {error_detail}"
                        )
                    
                    result = await response.json()
                    
                    if not result.get("artifacts"):
                        raise ValueError("No artifacts in API response")
                    
                    return result["artifacts"][0]
                    
        except asyncio.TimeoutError:
            raise ValueError("API request timed out")
        except aiohttp.ClientError as e:
            raise ValueError(f"Network error: {str(e)}")

    except Exception as e:
        raise ValueError(f"Generation failed: {str(e)}")

@router.post("/generate-exterior-design/")
async def generate_exterior_design(
    image: UploadFile = File(...),
    house_angle: HouseAngle = Form(...),
    design_style: ExteriorDesignStyle = Form(...),
    ai_strength: AIStylingStrength = Form("medium"),
    num_designs: int = Form(1, ge=1, le=12)
):
    try:
        from pathlib import Path

        BASE_DIR = Path(__file__).parent.parent
        uploads_dir = BASE_DIR / "fastapi_app" / "uploads"
        generated_dir = BASE_DIR / "fastapi_app" / "generated"

        # Save original file
        file_ext = os.path.splitext(image.filename)[1]
        original_filename = f"original_{uuid.uuid4().hex}{file_ext}"
        original_path = uploads_dir / original_filename

        with open(original_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        # Resize/process image
        image_bytes, _ = await resize_to_allowed_dimensions(str(original_path))

        design_config = {
            "style": design_style.value,
            "angle": house_angle.value,
        }

        tasks = [
            generate_exterior_design_variation(
                image_bytes,
                design_config,
                ai_strength.value
            ) for _ in range(num_designs)
        ]

        results = await asyncio.gather(*tasks)

        # Save results
        generated_urls = []
        for result in results:
            filename = f"generated_{uuid.uuid4().hex}.png"
            filepath = generated_dir / filename
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(result["base64"]))
            generated_urls.append(f"/static_generated/{filename}")

        return {
            "success": True,
            "original_image": f"/static_uploads/{original_filename}",
            "designs": generated_urls,
            "message": "Designs generated successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

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
        # Use consistent base directory paths
        from pathlib import Path
        import uuid, os, shutil, base64, time

        BASE_DIR = Path(__file__).parent.parent
        uploads_dir = BASE_DIR / "fastapi_app" / "uploads"
        generated_dir = BASE_DIR / "fastapi_app" / "generated"

        # Save original uploaded file
        file_ext = os.path.splitext(image.filename)[1]
        original_filename = f"original_{uuid.uuid4().hex}{file_ext}"
        original_path = uploads_dir / original_filename

        with open(original_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        # Resize/process image
        image_bytes, _ = await resize_to_allowed_dimensions(str(original_path))

        # Prepare config for outdoor design
        design_config = {
            "style": design_style.value,
            "space_type": space_type.value,
        }

        # Generate design variations
        tasks = [
            generate_outdoor_design_variation(
                image_bytes,
                design_config,
                ai_strength.value
            ) for _ in range(num_designs)
        ]

        results = await asyncio.gather(*tasks)

        # Save generated images and build URLs
        generated_urls = []
        for result in results:
            filename = f"generated_{uuid.uuid4().hex}.png"
            filepath = generated_dir / filename
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(result["base64"]))
            generated_urls.append(f"/static_generated/{filename}")

        return {
            "success": True,
            "original_image": f"/static_uploads/{original_filename}",
            "designs": generated_urls,
            "metadata": {
                "space_type": space_type.value,
                "design_style": design_style.value,
                "num_designs": num_designs,
                "styling_strength": ai_strength.value
            },
            "message": "Outdoor designs generated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
