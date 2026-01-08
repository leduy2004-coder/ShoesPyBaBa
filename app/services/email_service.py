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
        subject = (
            "OTP Verification"
            if otp_type == "REGISTER"
            else "Password Reset OTP"
        )

        body = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            </head>
            <body style="
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #f3f4f6;
            padding: 24px;
            ">

            <div style="
                max-width: 480px;
                margin: auto;
                background: #ffffff;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            ">

                <!-- HEADER -->
                <div style="
                background: linear-gradient(135deg, #2563eb, #3b82f6);
                color: #ffffff;
                padding: 20px;
                text-align: center;
                ">
                <h2 style="margin:0;">{subject}</h2>
                <p style="margin:4px 0 0; font-size:13px;">
                    Secure verification code
                </p>
                </div>

                <!-- CONTENT -->
                <div style="padding: 24px; color: #333;">

                <p>Hello,</p>

                <p>
                    We received a request to proceed with your action.
                    Please use the following One-Time Password (OTP):
                </p>

                <!-- OTP BOX -->
                <div style="text-align:center; margin: 32px 0;">
                    <span style="
                    display: inline-block;
                    font-size: 32px;
                    letter-spacing: 6px;
                    font-weight: 700;
                    color: #2563eb;
                    background: #eef2ff;
                    padding: 14px 28px;
                    border-radius: 10px;
                    ">
                    {otp}
                    </span>
                </div>

                <p style="text-align:center;">
                    ⏳ This code will expire in <strong>10 minutes</strong>.
                </p>

                <p style="font-size: 13px; color: #6b7280; margin-top: 24px;">
                    For security reasons, do not share this OTP with anyone.
                    If you did not request this, please ignore this email.
                </p>

                </div>

                <!-- FOOTER -->
                <div style="
                background: #f9fafb;
                text-align: center;
                padding: 14px;
                font-size: 12px;
                color: #9ca3af;
                ">
                © {datetime.now().year} ShoesPyBaBa. All rights reserved.
                </div>

            </div>

            </body>
            </html>
            """



        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=body,
            subtype="html",
        )

        await self.fastmail.send_message(message)


    @staticmethod
    def generate_otp():
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    def get_otp_expiry():
        return datetime.now() + timedelta(minutes=3)