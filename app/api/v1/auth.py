from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import (
    TokenResponse, UserLogin, UserRegister, PasswordResetResponse,
    TokenRefreshResponse, TokenRefreshRequest, PasswordResetRequest, PasswordResetConfirm
)
from app.services.auth_service import AuthService
from app.api.dependencies import get_db
from app.core.exceptions import InvalidCredentialsException

router = APIRouter(prefix="/auth")


def get_auth_service(
        db: Annotated[Session, Depends(get_db)],
) -> AuthService:
    """Dependency provider for AuthService bound to current DB session."""
    return AuthService(db)


@router.post("/register", response_model=TokenResponse)
async def register(
    payload: UserRegister,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        return auth_service.register(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        return auth_service.login(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except InvalidCredentialsException as e:
        raise e



@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh(
    payload: TokenRefreshRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        return auth_service.refresh_token(payload.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/password/reset", response_model=PasswordResetResponse)
async def password_reset(
    payload: PasswordResetRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        reset_token = auth_service.request_password_reset(payload)
        if reset_token:
            message = "If the email exists, a reset token was generated."
        else:
            message = "If the email exists, reset instructions were sent."
        return PasswordResetResponse(message=message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/password/reset/confirm", response_model=PasswordResetResponse)
async def password_reset_confirm(
    payload: PasswordResetConfirm,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    try:
        message = auth_service.reset_password(payload)
        return PasswordResetResponse(message=message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
