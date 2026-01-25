from fastapi import APIRouter, Depends, HTTPException, Body
from users.models.domain import User
from users.services.user_service import user_service
from users.services.otp_service import generate_otp, verify_otp
from users.services.email_service import send_otp_email
from users.repositories.user_repository import user_repo
from users.utils.security import get_current_user
from typing import Dict
from users.config.logging_config import get_logger

log = get_logger(__name__)

router = APIRouter()


@router.post("/user/register")
async def register(payload: Dict = Body(...)):
    return await user_service.register_user_self(
        email=payload["email"],
        password=payload["password"],
        first_name=payload.get("firstName", ""),
        last_name=payload.get("lastName", ""),
        tenant=payload.get("tenantId", "default"),
    )


@router.put("/user/confirm")
async def confirm(payload: Dict = Body(...)):
    email = payload.get("email")
    otp = payload.get("otp")
    if not email or not otp:
        raise HTTPException(400, "Email and OTP required")
    await user_service.confirm_user(email, otp)
    return {"message": "User confirmed"}


@router.put("/user/password")
async def change_password_self(
    payload: Dict = Body(...), token_data=Depends(get_current_user)
):
    sub = token_data.get("sub")
    if not sub:
        raise HTTPException(401, "Invalid token")

    new_pass = payload.get("password")
    if not new_pass:
        raise HTTPException(400, "Password required")
    await user_service.change_password(sub, new_pass, sub)
    return {"message": "Password updated"}


@router.post("/user/forget")
async def forgot_password(payload: Dict = Body(...)):
    email = payload.get("email")
    if not email:
        raise HTTPException(400, "Email required")

    user = await user_repo.get_by_email(email)
    if user:
        otp = await otp_service.generate_otp(email)
        await email_service.send_otp_email(email, otp)

    return {"message": "If email exists, OTP sent"}


@router.post("/user/reset")
async def reset_password(payload: Dict = Body(...)):
    email = payload.get("email")
    otp = payload.get("otp")
    new_pass = payload.get("password")

    if not all([email, otp, new_pass]):
        raise HTTPException(400, "Missing fields")

    valid = await otp_service.verify_otp(email, otp)
    if not valid:
        raise HTTPException(400, "Invalid OTP")

    user = await user_repo.get_by_email(email)
    if not user:
        raise HTTPException(400, "User not found")

    await user_service.change_password(user.id, new_pass, "SELF_RESET")

    return {"message": "Password reset successfully"}
