import logging
import smtplib

from email.message import EmailMessage
from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(recipient : str, subject : str, body : str,) -> None:
    
    message = EmailMessage()
    
    message["Subject"] = subject
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = recipient
    
    message.set_content(body)
    
    try:
        with smtplib.SMTP(settings.SMTP_HOST,
                          settings.SMTP_PORT,
                          timeout=15,) as server:
            
            server.starttls()
            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
            )
            
            server.send_message(message)
            
    except (OSError, smtplib.SMTPException):
        logger.exception("Failed to send email")
        
        raise