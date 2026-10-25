"""
Production-oriented authentication starter for MarketPilot.

This module is intentionally separate from the current demo auth.py so it can be
integrated after testing. It uses Argon2 password hashing and JWT access tokens.

For production:
- store users/sessions in PostgreSQL
- use HTTPS
- use secure, HttpOnly cookies for browser sessions where appropriate
- add email/SMS provider
- add rate limiting and audit logging
- rotate refresh tokens
"""

from datetime import datetime, timedelta, timezone
import os
import secrets

import jwt
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field
from pwdlib import PasswordHash

router = APIRouter(prefix="/auth-v2", tags=["Authentication V2"])
password_hash = PasswordHash.recommended()

ALGORITHM = "HS256"
SECRET = os.getenv("APP_SECRET_KEY", "CHANGE-ME-IN-PRODUCTION")
ACCESS_MINUTES = 30
REFRESH_DAYS = 30

# DEVELOPMENT PLACEHOLDER ONLY.
# Replace with a database repository before production.
_USERS = {}
_RESET_CODES = {}


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=20)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    identifier: str
    password: str
    remember_me: bool = True


class ForgotPasswordRequest(BaseModel):
    identifier: str


class ResetPasswordRequest(BaseModel):
    identifier: str
    otp: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    identifier: str
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


def _token(subject: str, days: int = 0):
    now = datetime.now(timezone.utc)
    expires = now + (timedelta(days=days) if days else timedelta(minutes=ACCESS_MINUTES))
    return jwt.encode(
        {"sub": subject, "iat": now, "exp": expires},
        SECRET,
        algorithm=ALGORITHM,
    )


@router.post("/signup")
def signup(payload: SignupRequest):
    key = payload.email.lower()
    if key in _USERS:
        raise HTTPException(status_code=409, detail="An account already exists.")

    _USERS[key] = {
        "name": payload.name,
        "email": key,
        "phone": payload.phone,
        "password_hash": password_hash.hash(payload.password),
        "verified": False,
    }

    return {
        "message": "Account created. Verify your email or phone before production login.",
        "email": key,
    }


@router.post("/login")
def login(payload: LoginRequest):
    identifier = payload.identifier.strip().lower()
    user = _USERS.get(identifier)

    if not user or not password_hash.verify(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid login credentials.")

    return {
        "message": "Login successful.",
        "access_token": _token(identifier),
        "refresh_token": _token(identifier, REFRESH_DAYS) if payload.remember_me else None,
        "token_type": "bearer",
    }


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest):
    identifier = payload.identifier.strip().lower()
    if identifier not in _USERS:
        # Do not reveal whether an account exists in production.
        return {"message": "If the account exists, an OTP has been sent."}

    otp = f"{secrets.randbelow(1_000_000):06d}"
    _RESET_CODES[identifier] = {
        "otp": otp,
        "expires": datetime.now(timezone.utc) + timedelta(minutes=10),
    }

    # DEVELOPMENT ONLY. Replace with real email/SMS provider.
    print(f"[DEV PASSWORD RESET OTP] {identifier}: {otp}")

    return {"message": "If the account exists, an OTP has been sent."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest):
    identifier = payload.identifier.strip().lower()
    item = _RESET_CODES.get(identifier)

    if not item or item["otp"] != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")

    if datetime.now(timezone.utc) > item["expires"]:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")

    if identifier not in _USERS:
        raise HTTPException(status_code=400, detail="Invalid reset request.")

    _USERS[identifier]["password_hash"] = password_hash.hash(payload.new_password)
    del _RESET_CODES[identifier]

    return {"message": "Password changed successfully."}


@router.post("/change-password")
def change_password(payload: ChangePasswordRequest):
    identifier = payload.identifier.strip().lower()
    user = _USERS.get(identifier)

    if not user or not password_hash.verify(payload.current_password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Current password is incorrect.")

    _USERS[identifier]["password_hash"] = password_hash.hash(payload.new_password)
    return {"message": "Password changed successfully."}
