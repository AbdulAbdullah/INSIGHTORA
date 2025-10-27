"""
Email Service Module - Professional email sending with HTML templates
"""

import aiosmtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from jinja2 import Template
from datetime import datetime

from .config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Professional email service with HTML templates and async SMTP
    """
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS
        self.email_from = settings.EMAIL_FROM
        self.email_from_name = settings.EMAIL_FROM_NAME
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Send email with HTML content and optional attachments
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.email_from_name} <{self.email_from}>"
            message["To"] = to_email
            
            # Add text part (fallback)
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)
            
            # Add HTML part
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    self._add_attachment(message, attachment)
            
            # Send email
            await self._send_message(message, to_email)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_registration_otp(self, email: str, name: str, otp_code: str) -> bool:
        """
        Send registration OTP verification email
        """
        subject = "Welcome to INSIGHTORA - Verify Your Account"
        
        html_content = self._get_registration_otp_template(name, otp_code)
        text_content = f"""
Welcome to INSIGHTORA, {name}!

Your verification code is: {otp_code}

Please enter this code to complete your registration.
This code will expire in 10 minutes.

If you didn't create this account, please ignore this email.

Best regards,
INSIGHTORA Team
        """.strip()
        
        return await self.send_email(email, subject, html_content, text_content)
    
    async def send_login_otp(self, email: str, name: str, otp_code: str) -> bool:
        """
        Send login OTP verification email
        """
        subject = "INSIGHTORA - Login Verification Code"
        
        html_content = self._get_login_otp_template(name, otp_code)
        text_content = f"""
Hello {name},

Your login verification code is: {otp_code}

Please enter this code to complete your login.
This code will expire in 10 minutes.

If you didn't attempt to log in, please secure your account immediately.

Best regards,
INSIGHTORA Team
        """.strip()
        
        return await self.send_email(email, subject, html_content, text_content)
    
    async def send_welcome_email(self, email: str, name: str) -> bool:
        """
        Send welcome email after successful registration
        """
        subject = "Welcome to INSIGHTORA - Your BI Journey Starts Here!"
        
        html_content = self._get_welcome_template(name)
        text_content = f"""
Welcome to INSIGHTORA, {name}!

Your account has been successfully verified and you're now ready to explore the power of AI-driven Business Intelligence.

What you can do with INSIGHTORA:
• Connect your databases and data sources
• Ask questions in natural language
• Get instant insights and visualizations
• Create interactive dashboards
• Share reports with your team

Get started by visiting your dashboard and connecting your first data source.

Need help? Our documentation and support team are here to assist you.

Best regards,
The INSIGHTORA Team
        """.strip()
        
        return await self.send_email(email, subject, html_content, text_content)
    
    def _get_registration_otp_template(self, name: str, otp_code: str) -> str:
        """
        Professional registration OTP email template
        """
        template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Your INSIGHTORA Account</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .logo { font-size: 28px; font-weight: bold; margin-bottom: 10px; }
        .content { background: white; padding: 40px 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .otp-box { background: #f8f9ff; border: 2px dashed #667eea; padding: 20px; margin: 25px 0; text-align: center; border-radius: 8px; }
        .otp-code { font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 8px; margin: 10px 0; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
        .button { display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0; }
        .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 6px; margin: 20px 0; color: #856404; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🔍 INSIGHTORA</div>
            <p>Business Intelligence Made Simple</p>
        </div>
        
        <div class="content">
            <h2 style="color: #333; margin-bottom: 20px;">Welcome, {{ name }}! 🎉</h2>
            
            <p>Thank you for signing up for INSIGHTORA! To complete your registration and start exploring AI-powered business intelligence, please verify your email address.</p>
            
            <div class="otp-box">
                <p style="margin-bottom: 10px; font-weight: bold;">Your Verification Code:</p>
                <div class="otp-code">{{ otp_code }}</div>
                <p style="margin-top: 10px; font-size: 14px; color: #666;">This code expires in 10 minutes</p>
            </div>
            
            <p>Simply enter this code in the verification form to activate your account and start your journey with intelligent data analysis.</p>
            
            <div class="warning">
                <strong>Security Notice:</strong> If you didn't create this account, please ignore this email. Your security is our priority.
            </div>
            
            <h3 style="color: #667eea; margin: 25px 0 15px 0;">What's Next?</h3>
            <ul style="padding-left: 20px; margin-bottom: 20px;">
                <li>✅ Verify your email with the code above</li>
                <li>🔗 Connect your data sources</li>
                <li>💬 Ask questions in natural language</li>
                <li>📊 Get instant visualizations</li>
                <li>🚀 Build powerful dashboards</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>© {{ current_year }} INSIGHTORA. All rights reserved.</p>
            <p>Making data insights accessible to everyone</p>
        </div>
    </div>
</body>
</html>
        """.strip())
        
        return template.render(
            name=name,
            otp_code=otp_code,
            current_year=datetime.now().year
        )
    
    def _get_login_otp_template(self, name: str, otp_code: str) -> str:
        """
        Professional login OTP email template
        """
        template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>INSIGHTORA Login Verification</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 25px; text-align: center; border-radius: 10px 10px 0 0; }
        .logo { font-size: 28px; font-weight: bold; margin-bottom: 10px; }
        .content { background: white; padding: 35px 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .otp-box { background: #f0f9ff; border: 2px solid #4facfe; padding: 20px; margin: 25px 0; text-align: center; border-radius: 8px; }
        .otp-code { font-size: 32px; font-weight: bold; color: #4facfe; letter-spacing: 8px; margin: 10px 0; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
        .security-notice { background: #fee2e2; border: 1px solid #fecaca; padding: 15px; border-radius: 6px; margin: 20px 0; color: #991b1b; }
        .info-box { background: #f0f9ff; border-left: 4px solid #4facfe; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🔍 INSIGHTORA</div>
            <p>Secure Login Verification</p>
        </div>
        
        <div class="content">
            <h2 style="color: #333; margin-bottom: 20px;">Login Verification Required</h2>
            
            <p>Hello <strong>{{ name }}</strong>,</p>
            <p>Someone is attempting to log into your INSIGHTORA account. For your security, please enter the verification code below:</p>
            
            <div class="otp-box">
                <p style="margin-bottom: 10px; font-weight: bold;">Your Login Code:</p>
                <div class="otp-code">{{ otp_code }}</div>
                <p style="margin-top: 10px; font-size: 14px; color: #666;">Valid for 10 minutes only</p>
            </div>
            
            <div class="info-box">
                <p><strong>Login Details:</strong></p>
                <p>🕐 Time: {{ current_time }}</p>
                <p>📅 Date: {{ current_date }}</p>
            </div>
            
            <div class="security-notice">
                <strong>⚠️ Security Alert:</strong> If you didn't attempt to log in, please contact our support team immediately and consider changing your password.
            </div>
            
            <p>After entering this code, you'll have full access to your INSIGHTORA dashboard and all your business intelligence tools.</p>
        </div>
        
        <div class="footer">
            <p>© {{ current_year }} INSIGHTORA. All rights reserved.</p>
            <p>Need help? Contact our support team</p>
        </div>
    </div>
</body>
</html>
        """.strip())
        
        now = datetime.now()
        return template.render(
            name=name,
            otp_code=otp_code,
            current_time=now.strftime("%I:%M %p"),
            current_date=now.strftime("%B %d, %Y"),
            current_year=now.year
        )
    
    def _get_welcome_template(self, name: str) -> str:
        """
        Professional welcome email template
        """
        template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to INSIGHTORA</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333; padding: 40px; text-align: center; border-radius: 10px 10px 0 0; }
        .logo { font-size: 32px; font-weight: bold; margin-bottom: 15px; }
        .content { background: white; padding: 40px 30px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .feature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; }
        .feature-box { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .feature-icon { font-size: 32px; margin-bottom: 10px; }
        .cta-button { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 25px 0; font-weight: bold; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
        .tips { background: #fff9e6; border-left: 4px solid #ffd700; padding: 20px; margin: 25px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🎉 Welcome to INSIGHTORA!</div>
            <p style="font-size: 18px; margin-top: 10px;">Your AI-Powered Business Intelligence Platform</p>
        </div>
        
        <div class="content">
            <h2 style="color: #333; margin-bottom: 20px;">Hello {{ name }}, Welcome Aboard! 🚀</h2>
            
            <p>Congratulations! Your INSIGHTORA account is now active and ready to transform how you interact with your business data.</p>
            
            <div class="feature-grid">
                <div class="feature-box">
                    <div class="feature-icon">🔗</div>
                    <h4>Connect Data</h4>
                    <p>Link databases, upload files, and integrate APIs</p>
                </div>
                <div class="feature-box">
                    <div class="feature-icon">💬</div>
                    <h4>Ask Questions</h4>
                    <p>Use natural language to query your data</p>
                </div>
                <div class="feature-box">
                    <div class="feature-icon">📊</div>
                    <h4>Get Insights</h4>
                    <p>Receive instant visualizations and analytics</p>
                </div>
                <div class="feature-box">
                    <div class="feature-icon">🎯</div>
                    <h4>Build Dashboards</h4>
                    <p>Create interactive reports and share with your team</p>
                </div>
            </div>
            
            <div class="tips">
                <h3 style="color: #b8860b; margin-bottom: 15px;">💡 Quick Start Tips:</h3>
                <ul style="padding-left: 20px;">
                    <li><strong>Start Small:</strong> Upload a CSV file to get familiar with the platform</li>
                    <li><strong>Ask Simple Questions:</strong> Try "Show me sales by month" or "What are my top products?"</li>
                    <li><strong>Explore Templates:</strong> Use our pre-built dashboard templates</li>
                    <li><strong>Join the Community:</strong> Connect with other users for tips and best practices</li>
                </ul>
            </div>
            
            <div style="text-align: center;">
                <a href="#" class="cta-button">Get Started with Your First Dashboard 🎯</a>
            </div>
            
            <h3 style="color: #667eea; margin: 30px 0 15px 0;">What Makes INSIGHTORA Special?</h3>
            <ul style="padding-left: 20px; margin-bottom: 25px;">
                <li>🤖 <strong>AI-Powered:</strong> Natural language queries with advanced LLM technology</li>
                <li>⚡ <strong>Real-Time:</strong> Live data updates and instant visualizations</li>
                <li>🔒 <strong>Secure:</strong> Enterprise-grade security with role-based access</li>
                <li>📱 <strong>Mobile-Ready:</strong> Access your dashboards anywhere, anytime</li>
                <li>🔧 <strong>Customizable:</strong> Build exactly what your business needs</li>
            </ul>
            
            <p>We're excited to see what insights you'll discover! If you have any questions, our support team is here to help.</p>
        </div>
        
        <div class="footer">
            <p>© {{ current_year }} INSIGHTORA. All rights reserved.</p>
            <p>Making data insights accessible to everyone 📈</p>
            <p style="margin-top: 10px;">
                <a href="#" style="color: #667eea; text-decoration: none;">Documentation</a> | 
                <a href="#" style="color: #667eea; text-decoration: none;">Support</a> | 
                <a href="#" style="color: #667eea; text-decoration: none;">Community</a>
            </p>
        </div>
    </div>
</body>
</html>
        """.strip())
        
        return template.render(
            name=name,
            current_year=datetime.now().year
        )
    
    async def _send_message(self, message: MIMEMultipart, to_email: str):
        """
        Send email message via SMTP
        """
        try:
            # Create SMTP connection with correct TLS settings for Gmail
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,  # Use STARTTLS instead of use_tls
                validate_certs=False  # For development, can be True in production
            )
            
            # Connect and authenticate
            await smtp.connect()
            if self.smtp_user and self.smtp_password:
                await smtp.login(self.smtp_user, self.smtp_password)
            
            # Send message
            await smtp.send_message(message)
            
            # Close connection
            await smtp.quit()
            
        except Exception as e:
            logger.error(f"SMTP error sending to {to_email}: {str(e)}")
            raise
    
    def _add_attachment(self, message: MIMEMultipart, attachment: Dict[str, Any]):
        """
        Add attachment to email message
        """
        try:
            with open(attachment["path"], "rb") as file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {attachment['filename']}"
                )
                message.attach(part)
        except Exception as e:
            logger.error(f"Failed to add attachment {attachment.get('filename', 'unknown')}: {str(e)}")


# Global email service instance
email_service = EmailService()