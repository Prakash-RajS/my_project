import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import secrets
import logging
from typing import Dict
from fastapi_app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('otp.log'),  # Log to file
        logging.StreamHandler()          # Log to console
    ]
)

otp_storage: Dict[str, dict] = {}

#google 
"""class OTPManager:
    @staticmethod
    def send_otp_email(email: str, otp: str) -> bool:
       # Send OTP using Gmail or Mailtrap based on settings
        try:
            msg = MIMEText(
                f"Hi,\n\nYour OTP is: {otp}\nValid for {settings.OTP_EXPIRE_MINUTES} minutes.\n\n- Team"
            )
            msg['Subject'] = '🔐 Password Reset OTP'
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = email

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()  # Needed for Gmail, harmless for Mailtrap
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(msg)

            logging.info(f"OTP sent to {email}")
            return True

        except Exception as e:
            logging.error(f"Failed to send OTP email to {email}: {str(e)}")
            return False"""

class OTPManager:
    @staticmethod
    def _send_via_mailtrap(email: str, otp: str) -> bool:
        """Send OTP using Mailtrap's SMTP"""
        try:
            msg = MIMEText(
                f"Your OTP is: {otp}\nValid for {settings.OTP_EXPIRE_MINUTES} minutes."
            )
            msg['Subject'] = 'Password Reset Code'
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = email

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(msg)
            
            logging.info(f"OTP sent to {email} via Mailtrap")
            return True
            
        except Exception as e:
            logging.error(f"Mailtrap send failed: {str(e)}")
            return False

    @staticmethod
    def generate_otp(email: str) -> str:
        """Core OTP generation with real-time delivery"""
        # Clear previous OTPs
        if email in otp_storage:
            del otp_storage[email]

        otp = str(secrets.randbelow(10**6)).zfill(6)
        expires_at = datetime.now() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        
        otp_storage[email] = {
            'otp': otp,
            'expires_at': expires_at,
            'is_used': False
        }

        # Attempt Mailtrap delivery
        if not OTPManager._send_via_mailtrap(email, otp):
            # Fallback to console if Mailtrap fails
            logging.warning(f"OTP for {email}: {otp} (Fallback to console)")
            print(f"\n⚠️ OTP for {email}: {otp}\n")

        return otp

    @staticmethod
    def verify_otp(email: str, otp: str) -> bool:
        """Verify OTP with strict checks"""
        record = otp_storage.get(email)
        if not record:
            logging.warning(f"No OTP found for {email}")
            return False
            
        return (
            record['otp'] == otp
            and not record['is_used']
            and datetime.now() < record['expires_at']
        )

    @staticmethod
    def mark_used(email: str):
        """Invalidate OTP after successful reset"""
        if email in otp_storage:
            otp_storage[email]['is_used'] = True
            logging.info(f"Marked OTP used for {email}")