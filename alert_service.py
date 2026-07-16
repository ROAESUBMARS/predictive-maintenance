import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def send_email_alert(to_email: str, subject: str, body: str) -> bool:
    """
    Send an email alert. Uses SMTP if credentials are provided in env vars,
    otherwise defaults to a mock print statement.
    """
    if not to_email:
        return False
        
    smtp_server = os.environ.get("SMTP_SERVER", "")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    from_email = os.environ.get("SMTP_FROM", smtp_user or "alerts@predictivemaintenance.local")
    
    if not (smtp_server and smtp_user and smtp_pass):
        logger.info(f"[MOCK EMAIL ALERT] To: {to_email} | Subject: {subject}")
        logger.info(f"[MOCK EMAIL BODY]\n{body}")
        return True
        
    try:
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server.login(smtp_user, smtp_pass)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            
        server.send_message(msg)
        server.quit()
        logger.info(f"Email alert sent to {to_email}")
        return True
    except Exception as e:
        logger.exception(f"Failed to send email alert: {e}")
        return False

def send_sms_alert(to_phone: str, message: str) -> bool:
    """
    Send an SMS alert using Twilio if configured, otherwise falls back to a mock print statement.
    """
    if not to_phone:
        return False
        
    twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    twilio_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    twilio_from = os.environ.get("TWILIO_FROM_NUMBER", "")
    
    if not (twilio_sid and twilio_token and twilio_from):
        logger.info(f"[MOCK SMS ALERT] To: {to_phone} | Message: {message}")
        return True
        
    try:
        # Import inside to avoid hard dependency if user doesn't install twilio
        from twilio.rest import Client
        client = Client(twilio_sid, twilio_token)
        msg = client.messages.create(
            body=message,
            from_=twilio_from,
            to=to_phone
        )
        logger.info(f"SMS alert sent to {to_phone}. SID: {msg.sid}")
        return True
    except ImportError:
        logger.info(f"[MOCK SMS ALERT] (Twilio not installed) To: {to_phone} | Message: {message}")
        return True
    except Exception as e:
        logger.exception(f"Failed to send SMS alert: {e}")
        return False

def trigger_fault_alerts(fault_name: str, severity: str, recommendations: str, to_email: str = None, to_phone: str = None):
    """
    Helper function to format and trigger both email and SMS alerts.
    """
    subject = f"[{severity.upper()}] Predictive Maintenance Alert: {fault_name}"
    
    body = f"URGENT ALERT: A {severity.upper()} fault '{fault_name}' has been detected.\n\n"
    body += f"Recommended Actions:\n{recommendations}\n\n"
    body += "Please inspect the equipment immediately."
    
    sms_body = f"{severity.upper()} Alert: {fault_name}. Action needed: {recommendations[:100]}..."
    
    email_success = False
    sms_success = False
    
    if to_email:
        email_success = send_email_alert(to_email, subject, body)
    if to_phone:
        sms_success = send_sms_alert(to_phone, sms_body)
        
    return email_success, sms_success
