from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from appln.models import UserData
from asgiref.sync import sync_to_async
from django.contrib.auth.hashers import make_password
import os
from typing import Optional

router = APIRouter()

@router.post("/update_profile")
async def update_profile(
    email: Optional[str] = Form(None),
    userid: Optional[str] = Form(None),
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    new_password: str = Form(""),
    confirm_password: str = Form(""),
    profile_pic: UploadFile = File(None)
):
    # 1. Find user by email or userid
    try:
        if email:
            user = await sync_to_async(UserData.objects.get)(email=email)
        elif userid:
            user = await sync_to_async(UserData.objects.get)(userid=userid)
        else:
            raise HTTPException(status_code=400, detail="Email or User ID required")
    except UserData.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Update profile fields if provided
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if phone_number:
        user.phone_number = phone_number
    if location:
        user.location = location

    # 3. Optional password update
    if new_password and confirm_password:
        if new_password == confirm_password:
            user.password = make_password(new_password)
        else:
            return JSONResponse(status_code=400, content={"error": "Passwords do not match"})

    # 4. Optional profile picture update
    if profile_pic:
        try:
            id_part = email or userid
            filename = f"{id_part.replace('@', '_')}_pic.png"
            media_folder = "fastapi_app/media/profile_pics"
            os.makedirs(media_folder, exist_ok=True)
            filepath = os.path.join(media_folder, filename)
            with open(filepath, "wb") as f:
                f.write(await profile_pic.read())
            user.profile_pic = f"/media/profile_pics/{filename}"
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Profile picture upload failed: {str(e)}"})

    await sync_to_async(user.save)()
    return {"message": "Profile updated successfully"}
