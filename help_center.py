# fastapi_app/help_center.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from fastapi_app.django_setup import django_setup
from appln.models import ContactUs
import smtplib
from email.message import EmailMessage
from fastapi_app.config import settings

router = APIRouter()
django_setup()

class HelpCenterForm(BaseModel):
    email: EmailStr

@router.post("/help-center")
def help_center(data: HelpCenterForm):
    # Save only email to DB
    try:
        ContactUs.objects.create(
            email=data.email,
            first_name="",  # optional fields left empty
            last_name="",
            contact_number="",
            subject="Help Center",
            message="Help Center Inquiry"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save email")

    # Send Thank You email
    try:
        msg = EmailMessage()
        msg['Subject'] = "We've received your Help Center request"
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = data.email
        msg.set_content(
            f"Hi,\n\nThank you for contacting our Stackly.Ai!-Help Center.\nOne of our team members will get back to you shortly!\n\nRegards,\nThe Stackly.Ai Team"
        )

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send confirmation email")

    return {"message": "Help Center form submitted successfully"}
