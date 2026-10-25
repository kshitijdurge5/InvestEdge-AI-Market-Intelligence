from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import secrets
import sqlite3

import jwt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from pwdlib import PasswordHash


# ============================================================
# INVESTEDGE - PRODUCTION-STYLE AUTHENTICATION
# Persistent SQLite development database
# ============================================================

router = APIRouter(prefix="/auth-v2", tags=["Authentication V2"])

password_hash = PasswordHash.recommended()

JWT_SECRET = os.getenv(
    "INVESTEDGE_JWT_SECRET",
    "CHANGE_THIS_DEVELOPMENT_SECRET_BEFORE_PRODUCTION"
)

JWT_ALGORITHM = "HS256"
ACCESS_MINUTES = 60
REMEMBER_DAYS = 30


# ============================================================
# DATABASE
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "investedge.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT NOT NULL,
            otp TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


init_database()


# ============================================================
# REQUEST MODELS
# ============================================================

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


# ============================================================
# HELPERS
# ============================================================

def normalize_identifier(identifier: str) -> str:
    return identifier.strip().lower()


def create_token(identifier: str, remember_me: bool = True):
    now = datetime.now(timezone.utc)

    if remember_me:
        expires = now + timedelta(days=REMEMBER_DAYS)
    else:
        expires = now + timedelta(minutes=ACCESS_MINUTES)

    payload = {
        "sub": identifier,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def get_user(identifier: str):
    identifier = normalize_identifier(identifier)

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (identifier,),
    ).fetchone()

    connection.close()

    return row


# ============================================================
# SIGN UP
# ============================================================

@router.post("/signup")
def signup(payload: SignupRequest):

    email = normalize_identifier(payload.email)

    existing_user = get_user(email)

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="An account already exists.",
        )

    now = datetime.now(timezone.utc).isoformat()

    hashed_password = password_hash.hash(payload.password)

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO users (
                name,
                email,
                phone,
                password_hash,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.name.strip(),
                email,
                payload.phone.strip(),
                hashed_password,
                now,
                now,
            ),
        )

        connection.commit()

    except sqlite3.IntegrityError:
        connection.close()

        raise HTTPException(
            status_code=409,
            detail="An account already exists.",
        )

    connection.close()

    return {
        "message": "Account created successfully.",
        "email": email,
    }


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
def login(payload: LoginRequest):

    identifier = normalize_identifier(payload.identifier)

    user = get_user(identifier)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials.",
        )

    try:
        password_valid = password_hash.verify(
            payload.password,
            user["password_hash"],
        )
    except Exception:
        password_valid = False

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials.",
        )

    token = create_token(
        identifier,
        payload.remember_me,
    )

    return {
        "message": "Login successful.",
        "access_token": token,
        "token_type": "bearer",
        "expires_in_minutes": (
            REMEMBER_DAYS * 24 * 60
            if payload.remember_me
            else ACCESS_MINUTES
        ),
        "user": {
            "name": user["name"],
            "email": user["email"],
            "phone": user["phone"],
        },
    }


# ============================================================
# FORGOT PASSWORD
# ============================================================

@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest):

    identifier = normalize_identifier(payload.identifier)

    user = get_user(identifier)

    # Always return the same general message.
    # This prevents revealing whether an account exists.
    if not user:
        return {
            "message": "If the account exists, an OTP has been sent."
        }

    otp = f"{secrets.randbelow(1_000_000):06d}"

    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=10)

    connection = get_connection()

    connection.execute(
        """
        DELETE FROM password_resets
        WHERE identifier = ?
        """,
        (identifier,),
    )

    connection.execute(
        """
        INSERT INTO password_resets (
            identifier,
            otp,
            expires_at,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            identifier,
            otp,
            expires.isoformat(),
            now.isoformat(),
        ),
    )

    connection.commit()
    connection.close()

    # DEVELOPMENT ONLY.
    # Later this will be sent through email/SMS.
    return {
        "message": "If the account exists, an OTP has been sent.",
        "dev_otp": otp,
    }


# ============================================================
# RESET PASSWORD
# ============================================================

@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest):

    identifier = normalize_identifier(payload.identifier)

    connection = get_connection()

    reset_record = connection.execute(
        """
        SELECT *
        FROM password_resets
        WHERE identifier = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (identifier,),
    ).fetchone()

    if not reset_record:
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP.",
        )

    try:
        expires_at = datetime.fromisoformat(
            reset_record["expires_at"]
        )
    except ValueError:
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP.",
        )

    if datetime.now(timezone.utc) > expires_at:
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP.",
        )

    if reset_record["otp"] != payload.otp:
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP.",
        )

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (identifier,),
    ).fetchone()

    if not user:
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP.",
        )

    new_hash = password_hash.hash(payload.new_password)

    connection.execute(
        """
        UPDATE users
        SET password_hash = ?,
            updated_at = ?
        WHERE email = ?
        """,
        (
            new_hash,
            datetime.now(timezone.utc).isoformat(),
            identifier,
        ),
    )

    connection.execute(
        """
        DELETE FROM password_resets
        WHERE identifier = ?
        """,
        (identifier,),
    )

    connection.commit()
    connection.close()

    return {
        "message": "Password reset successfully."
    }


# ============================================================
# CHANGE PASSWORD
# ============================================================

@router.post("/change-password")
def change_password(payload: ChangePasswordRequest):

    identifier = normalize_identifier(payload.identifier)

    user = get_user(identifier)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Current password is incorrect.",
        )

    try:
        password_valid = password_hash.verify(
            payload.current_password,
            user["password_hash"],
        )
    except Exception:
        password_valid = False

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Current password is incorrect.",
        )

    new_hash = password_hash.hash(
        payload.new_password
    )

    connection = get_connection()

    connection.execute(
        """
        UPDATE users
        SET password_hash = ?,
            updated_at = ?
        WHERE email = ?
        """,
        (
            new_hash,
            datetime.now(timezone.utc).isoformat(),
            identifier,
        ),
    )

    connection.commit()
    connection.close()

    return {
        "message": "Password changed successfully."
    }