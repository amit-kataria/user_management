from users.config.logging_config import get_logger

log = get_logger(__name__)


async def send_otp_email(to_email: str, otp: str):
    # In a real app, use SMTP or an email provider API
    log.info(f"EMAIL SENT to {to_email}: Your OTP is {otp}")


async def send_invite_email(to_email: str, invite_link: str):
    log.info(f"EMAIL SENT to {to_email}: You are invited. Click {invite_link}")
