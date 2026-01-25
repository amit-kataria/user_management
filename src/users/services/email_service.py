import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from users.config.logging_config import get_logger
from users.config.config import config

log = get_logger(__name__)


async def send_email(
    to_email: str, subject: str, html_body: str, text_body: str = None
):
    """
    Send an email using SMTP configuration from settings.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML content of the email
        text_body: Plain text content (optional, falls back to HTML)
    """
    try:
        log.info(f"Sending email to {to_email} with subject: {subject}")
        # Create message
        msg = MIMEMultipart("alternative")
        msg["From"] = config.SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject

        # Add plain text part
        if text_body:
            part1 = MIMEText(text_body, "plain")
            msg.attach(part1)

        # Add HTML part
        part2 = MIMEText(html_body, "html")
        msg.attach(part2)

        # Connect to SMTP server and send email
        log.info(f"Connecting to SMTP server: {config.SMTP_HOST}:{config.SMTP_PORT}")
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            log.info(f"Connected to SMTP server: {config.SMTP_HOST}:{config.SMTP_PORT}")
            server.starttls()  # Secure the connection
            log.info(f"Secure connection established")
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            log.info(f"Logged in to SMTP server as {config.SMTP_USER}")
            server.send_message(msg)
            log.info(f"Email sent successfully to {to_email} with subject: {subject}")
        return True

    except Exception as e:
        log.error(f"Failed to send email to {to_email}: {str(e)}", exc_info=True)
        # Don't raise exception - we don't want email failures to break the flow
        # In production, you might want to queue failed emails for retry
        return False


async def send_otp_email(to_email: str, otp: str):
    """
    Send OTP verification email to user.

    Args:
        to_email: Recipient email address
        otp: One-time password to send
    """
    subject = "Your OTP for Account Verification"

    # HTML email template
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .otp-code {{
                font-size: 32px;
                font-weight: bold;
                color: #4CAF50;
                text-align: center;
                padding: 20px;
                background-color: #f0f0f0;
                border-radius: 5px;
                margin: 20px 0;
                letter-spacing: 5px;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Account Verification</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>Thank you for registering with us. Please use the following One-Time Password (OTP) to verify your account:</p>
                <div class="otp-code">{otp}</div>
                <p>This OTP is valid for 10 minutes. Please do not share this code with anyone.</p>
                <p>If you did not request this verification, please ignore this email.</p>
                <p>Best regards,<br>User Management Team</p>
            </div>
            <div class="footer">
                <p>This is an automated email. Please do not reply to this message.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Plain text fallback
    text_body = f"""
    Account Verification
    
    Hello,
    
    Thank you for registering with us. Please use the following One-Time Password (OTP) to verify your account:
    
    OTP: {otp}
    
    This OTP is valid for 10 minutes. Please do not share this code with anyone.
    
    If you did not request this verification, please ignore this email.
    
    Best regards,
    User Management Team
    
    ---
    This is an automated email. Please do not reply to this message.
    """

    log.info(f"Sending OTP email to {to_email}")
    return await send_email(to_email, subject, html_body, text_body)


async def send_invite_email(to_email: str, invite_link: str):
    """
    Send invitation email to a new user.

    Args:
        to_email: Recipient email address
        invite_link: Link for the user to complete registration
    """
    subject = "You're Invited to Join Our Platform"

    # HTML email template
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #2196F3;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .button {{
                display: inline-block;
                padding: 15px 30px;
                background-color: #2196F3;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
                font-weight: bold;
            }}
            .button:hover {{
                background-color: #1976D2;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
            .link {{
                word-break: break-all;
                color: #2196F3;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome!</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>You have been invited to join our platform. We're excited to have you on board!</p>
                <p>To complete your registration and set up your account, please click the button below:</p>
                <div style="text-align: center;">
                    <a href="{invite_link}" class="button">Accept Invitation</a>
                </div>
                <p>Or copy and paste this link into your browser:</p>
                <p class="link">{invite_link}</p>
                <p>This invitation link will expire in 7 days.</p>
                <p>If you did not expect this invitation, please ignore this email.</p>
                <p>Best regards,<br>User Management Team</p>
            </div>
            <div class="footer">
                <p>This is an automated email. Please do not reply to this message.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Plain text fallback
    text_body = f"""
    Welcome!
    
    Hello,
    
    You have been invited to join our platform. We're excited to have you on board!
    
    To complete your registration and set up your account, please visit the following link:
    
    {invite_link}
    
    This invitation link will expire in 7 days.
    
    If you did not expect this invitation, please ignore this email.
    
    Best regards,
    User Management Team
    
    ---
    This is an automated email. Please do not reply to this message.
    """

    log.info(f"Sending invitation email to {to_email}")
    return await send_email(to_email, subject, html_body, text_body)
