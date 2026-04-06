from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import jwt
import hashlib
import secrets

router = APIRouter(prefix="/auth", tags=["Authentication"])


# Простое хеширование без bcrypt
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{hash_obj.hex()}:{salt}"


def verify_password(plain: str, hashed: str) -> bool:
    stored_hash, salt = hashed.split(":")
    new_hash = hashlib.pbkdf2_hmac('sha256', plain.encode(), salt.encode(), 100000).hex()
    return new_hash == stored_hash


# Хранилище
users_db = {}


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class RegisterResponse(BaseModel):
    user_id: str
    email: str
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(request: RegisterRequest):
    if request.email in users_db:
        raise HTTPException(400, "Email already registered")

    user_id = secrets.token_hex(16)
    users_db[request.email] = {
        "user_id": user_id,
        "email": request.email,
        "password_hash": hash_password(request.password),
        "name": request.name,
        "created_at": datetime.utcnow().isoformat()
    }

    return RegisterResponse(user_id=user_id, email=request.email, message="User registered successfully")


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user = users_db.get(request.email)

    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")

    token = jwt.encode({"sub": user["user_id"], "exp": datetime.utcnow() + timedelta(hours=1)}, "secret",
                       algorithm="HS256")
    refresh = jwt.encode({"sub": user["user_id"], "exp": datetime.utcnow() + timedelta(days=7)}, "secret",
                         algorithm="HS256")

    return LoginResponse(access_token=token, refresh_token=refresh, token_type="bearer", expires_in=3600)


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh(request: RefreshTokenRequest):
    try:
        payload = jwt.decode(request.refresh_token, "secret", algorithms=["HS256"])
        new_token = jwt.encode({"sub": payload["sub"], "exp": datetime.utcnow() + timedelta(hours=1)}, "secret",
                               algorithm="HS256")
        return RefreshTokenResponse(access_token=new_token, token_type="bearer", expires_in=3600)
    except:
        raise HTTPException(401, "Invalid refresh token")


@router.post("/password/reset", status_code=202)
async def reset(request: PasswordResetRequest):
    return {"message": "If account exists, you will receive a reset link"}


@router.post("/password/reset/confirm")
async def reset_confirm(request: PasswordResetConfirmRequest):
    return {"message": "Password successfully reset"}