import hashlib
import secrets
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["auth"])

# ===== ХРАНИЛИЩА (временные, для тестов) =====
users_db = {}           # email -> user data
refresh_tokens_db = {}  # refresh_token -> token data


# ===== МОДЕЛИ =====
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    message: str
    user_id: str


# ===== ФУНКЦИИ ХЕШИРОВАНИЯ =====
def hash_password(password: str) -> str:
    """Хеширует пароль с солью (SHA-256)"""
    salt = secrets.token_hex(16)
    hash_value = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hash_value}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль против хеша"""
    salt, hash_value = hashed_password.split(":")
    computed_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
    return computed_hash == hash_value


# ===== ФУНКЦИИ ГЕНЕРАЦИИ ТОКЕНОВ =====
def generate_access_token() -> str:
    """Генерирует простой access-токен (UUID)"""
    return str(uuid4())


def generate_refresh_token() -> str:
    """Генерирует простой refresh-токен (UUID)"""
    return str(uuid4())


# ===== ЭНДПОИНТЫ =====
@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    if request.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    user_id = str(uuid4())
    users_db[request.email] = {
        "user_id": user_id,
        "email": request.email,
        "name": request.name,
        "password_hash": hash_password(request.password),
        "created_at": datetime.utcnow()
    }

    return RegisterResponse(message="User registered successfully", user_id=user_id)


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user = users_db.get(request.email)

    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = generate_access_token()
    refresh_token = generate_refresh_token()

    refresh_tokens_db[refresh_token] = {
        "user_id": user["user_id"],
        "email": user["email"],
        "expires_at": datetime.utcnow() + timedelta(days=7)
    }

    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
async def refresh(request: RefreshRequest):
    token_data = refresh_tokens_db.get(request.refresh_token)

    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if token_data["expires_at"] < datetime.utcnow():
        del refresh_tokens_db[request.refresh_token]
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # Генерируем новые токены
    new_access_token = generate_access_token()
    new_refresh_token = generate_refresh_token()

    # Удаляем старый и сохраняем новый
    del refresh_tokens_db[request.refresh_token]
    refresh_tokens_db[new_refresh_token] = {
        "user_id": token_data["user_id"],
        "email": token_data["email"],
        "expires_at": datetime.utcnow() + timedelta(days=7)
    }

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(request: RefreshRequest):
    if request.refresh_token in refresh_tokens_db:
        del refresh_tokens_db[request.refresh_token]
    return {"message": "Logged out successfully"}