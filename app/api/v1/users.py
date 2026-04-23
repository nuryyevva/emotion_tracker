from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)) -> UserResponse:
    user = db.scalar(select(User).where(User.id == str(user_id)))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)



from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from uuid import uuid4

router = APIRouter(tags=["Users"])


class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    timezone: str
    created_at: datetime


class UserProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    timezone: Optional[str] = None


class UserSettingsResponse(BaseModel):
    notification_preferences: dict
    privacy_settings: dict
    hobbies: List[dict]
    coping_methods: List[dict]


class HobbyCreateRequest(BaseModel):
    name: str
    category: Optional[str] = None


class HobbyResponse(BaseModel):
    id: str
    name: str
    category: Optional[str]
    created_at: datetime


class CopingMethodCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


class CopingMethodResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime


@router.put("/users/me", response_model=UserProfileResponse)
async def put_users_me(request: UserProfileUpdateRequest):
    return UserProfileResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        email="user@example.com",
        name=request.name or "User",
        timezone=request.timezone or "UTC",
        created_at=datetime.now()
    )


@router.get("/users/me", response_model=UserProfileResponse)
async def get_users_me():
    return UserProfileResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        email="user@example.com",
        name="John Doe",
        timezone="Europe/Moscow",
        created_at=datetime.now()
    )


@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users_me():
    return None


@router.get("/users/me/settings", response_model=UserSettingsResponse)
async def get_users_me_settings():
    return UserSettingsResponse(
        notification_preferences={"email": True, "telegram": False},
        privacy_settings={"share_analytics": False},
        hobbies=[{"id": "1", "name": "Reading", "category": "relaxation"}],
        coping_methods=[{"id": "1", "name": "Meditation", "description": "10 min breathing"}]
    )


@router.put("/users/me/settings", response_model=UserSettingsResponse)
async def put_users_me_settings():
    return UserSettingsResponse(
        notification_preferences={"email": True, "telegram": False},
        privacy_settings={"share_analytics": False},
        hobbies=[],
        coping_methods=[]
    )


@router.post("/users/me/settings/hobbies", response_model=HobbyResponse, status_code=status.HTTP_201_CREATED)
async def post_users_me_settings_hobbies(request: HobbyCreateRequest):
    return HobbyResponse(
        id=str(uuid4()),
        name=request.name,
        category=request.category,
        created_at=datetime.now()
    )


@router.delete("/users/me/settings/hobbies/{hobby_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users_me_settings_hobbies_hobby_id(hobby_id: str):
    return None


@router.post("/users/me/settings/coping-methods", response_model=CopingMethodResponse, status_code=status.HTTP_201_CREATED)
async def post_users_me_settings_coping_methods(request: CopingMethodCreateRequest):
    return CopingMethodResponse(
        id=str(uuid4()),
        name=request.name,
        description=request.description,
        created_at=datetime.now()
    )


@router.delete("/users/me/settings/coping-methods/{method_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users_me_settings_coping_methods_method_id(method_id: str):
    return None