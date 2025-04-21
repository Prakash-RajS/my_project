from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from appln.models import UserData
from asgiref.sync import sync_to_async
from django.contrib.auth.hashers import make_password
import os

router = APIRouter()

@router.post("/update_profile")
async def update_profile(
    email: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: str = Form(...),
    location: str = Form(...),
    new_password: str = Form(""),
    confirm_password: str = Form(""),
    profile_pic: UploadFile = File(None)
):
    try:
        user = await sync_to_async(UserData.objects.get)(email=email)
    except UserData.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

    user.first_name = first_name
    user.last_name = last_name
    user.phone_number = phone_number
    user.location = location

    # Optional password update
    if new_password and confirm_password:
        if new_password == confirm_password:
            user.password = make_password(new_password)
        else:
            return JSONResponse(status_code=400, content={"error": "Passwords do not match"})

    # Profile picture
    if profile_pic:
        try:
            filename = f"{email.replace('@', '_')}_pic.png"
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
