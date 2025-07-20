import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from datetime import datetime, timedelta
from cachetools import TTLCache
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailHelper:
    def __init__(self):
        """
        Initialize email helper with SMTP credentials and cache settings
        Environment variables for SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, and SMTP_PASSWORD handle in docker-compose.yaml file
        """
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        
        # Cache with 5 minute TTL (time-to-live)
        self.otp_cache = TTLCache(maxsize=1000, ttl=300)    # 5 minutes
        
        # Email template
        self.email_template = """
        <html>
            <body>
                <h2>Your One-Time Password (OTP)</h2>
                <p>Your verification code is: <strong>{otp}</strong></p>
                <p>This code will expire in 5 minutes.</p>
            </body>
        </html>
        """
    
    def _generate_otp(self, length: int = 6) -> str:
        """Generate a random numeric OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_otp(self, recipient_email: str) -> bool:
        """
        Send OTP to the specified email and store it in cache
        
        Args:
            recipient_email: Email address to send OTP to
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            logger.info(f"Request to send OTPsssssssssss: {recipient_email}") 
            logger.info(f"self.username: {self.username}") 
            logger.info(f"self.SMTP_PASSWORD: {self.password}")
            # Generate OTP
            otp = self._generate_otp()
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = recipient_email
            msg['Subject'] = "Your Verification Code to SafeCheck"
            
            # Add HTML body
            body = self.email_template.format(otp=otp)
            msg.attach(MIMEText(body, 'html'))
            
            # Store OTP in cache
            self.otp_cache[recipient_email] = {
                'otp': otp,
                'generated_at': datetime.now()
            }
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"OTP sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send OTP to {recipient_email}: {e}")
            return False
    
    def verify_otp(self, email: str, user_provided_otp: str) -> bool:
        """
        Verify if the provided OTP matches the one in cache
        
        Args:
            email: Email address to verify
            user_provided_otp: OTP provided by user
            
        Returns:
            bool: True if OTP is valid, False otherwise
        """
        try:
            cached_data = self.otp_cache.get(email)
            
            if not cached_data:
                logger.warning(f"No OTP found in cache for {email}")
                return False
                
            logger.info(f"Found cached OTP for {email}. Generated at: {cached_data['generated_at']}")
            logger.info(f"Type check - cached OTP: {type(cached_data['otp'])}, user OTP: {type(user_provided_otp)}")
            if int(cached_data['otp']) == user_provided_otp:
                self.otp_cache.pop(email, None)
                logger.info(f"OTP verified successfully for {email}")
                return True
                
            logger.warning(f"Invalid OTP for {email}. Expected: {cached_data['otp']}, Received: {user_provided_otp}")
            return False
            
        except Exception as e:
            logger.error(f"Error verifying OTP for {email}: {str(e)}", exc_info=True)
            return False