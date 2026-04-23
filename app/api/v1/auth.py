from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import (
    TokenResponse, UserLogin, UserRegister, PasswordResetResponse,
    TokenRefreshResponse, TokenRefreshRequest, PasswordResetRequest, PasswordResetConfirm
)
from app.services.auth_service import AuthService
from app.api.dependencies import get_db
from pydantic import EmailStr

router = APIRouter(prefix="/auth", tags=["auth"])

db = get_db()
auth_service = AuthService(db)

@router.post("/register", response_model=TokenResponse)
async def register(email: EmailStr, password: str, timezone: str):
    try:
        user_reg = UserRegister(email=email,
                            password=password,
                            timezone=timezone)
        token_response = auth_service.register(user_reg)
        return token_response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(email: EmailStr, password: str):
    try:
        user_login = UserLogin(email=email, password=password)
        return auth_service.login(user_login)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh(refresh_token: str):
    try:
        token_req = TokenRefreshRequest(refresh_token=refresh_token)
        token_data = ... # TokenRefreshResponse
        return token_data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/password/reset", response_model=PasswordResetResponse)
async def password_reset(email: EmailStr):
    try:
        password_reset_req = PasswordResetRequest(email=email)
        password_reset_resp = auth_service.request_password_reset(password_reset_req)
        return password_reset_resp
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/password/reset/confirm", response_model=str)
async def password_reset_confirm(token: str, new_password: str):
    try:
        password_reset_req = PasswordResetConfirm(token=token, new_password=new_password)
        message = auth_service.reset_password(password_reset_req)
        return message
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
