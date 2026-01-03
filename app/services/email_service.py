from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
import random
import string
from datetime import datetime, timedelta

class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.EMAIL_USERNAME,
            MAIL_PASSWORD=settings.EMAIL_PASSWORD,
            MAIL_FROM=settings.EMAIL_FROM,
            MAIL_PORT=settings.EMAIL_PORT,
            MAIL_SERVER=settings.EMAIL_HOST,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
        )
        self.fastmail = FastMail(self.conf)

    async def send_otp_email(self, email: str, otp: str, otp_type: str):
        subject = "OTP Verification" if otp_type == "REGISTER" else "Password Reset OTP"
        body = f"""
        <html>
        <body>
            <h2>{subject}</h2>
            <p>Your OTP code is: <strong>{otp}</strong></p>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
        </html>
        """
        
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=body,
            subtype="html"
        )
        
        await self.fastmail.send_message(message)

    @staticmethod
    def generate_otp():
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    def get_otp_expiry():
        return datetime.now() + timedelta(minutes=10)