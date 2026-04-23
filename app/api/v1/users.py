from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUserContext, get_current_user, get_db
from app.schemas.user import (
    CopingMethodCreate,
    CopingMethodResponse,
    HobbyCreate,
    HobbyResponse,
    MessageResponse,
    UserResponse,
    UserSettingsResponse,
    UserSettingsUpdate,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter(tags=["Users"])


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    return UserService(db)


@router.get("/users/me", response_model=UserResponse)
def get_users_me(
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    return service.get_profile(user.user_id)


@router.put("/users/me", response_model=UserResponse)
def put_users_me(
    payload: UserUpdate,
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    updated = service.update_profile(user.user_id, payload.model_dump(exclude_none=True))
    service.db.commit()
    return updated


@router.delete("/users/me", response_model=MessageResponse)
def delete_users_me(
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> MessageResponse:
    service.soft_delete_profile(user.user_id)
    service.db.commit()
    return MessageResponse(message="User deleted successfully.")


@router.get("/users/me/settings", response_model=UserSettingsResponse)
def get_users_me_settings(
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserSettingsResponse:
    return service.get_settings(user.user_id)


@router.put("/users/me/settings", response_model=UserSettingsResponse)
def put_users_me_settings(
    payload: UserSettingsUpdate,
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserSettingsResponse:
    updated = service.update_settings(user.user_id, payload.model_dump(exclude_none=True))
    service.db.commit()
    return updated


@router.post("/users/me/settings/hobbies", response_model=HobbyResponse, status_code=status.HTTP_201_CREATED)
def post_users_me_settings_hobbies(
    payload: HobbyCreate,
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> HobbyResponse:
    hobby = service.add_hobby(user.user_id, payload.hobby)
    service.db.commit()
    return hobby


@router.delete("/users/me/settings/hobbies/{hobby}", status_code=status.HTTP_204_NO_CONTENT)
def delete_users_me_settings_hobbies_hobby(
    hobby: str,
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> Response:
    deleted = service.remove_hobby(user.user_id, hobby)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/users/me/settings/coping-methods", response_model=CopingMethodResponse, status_code=status.HTTP_201_CREATED)
def post_users_me_settings_coping_methods(
    payload: CopingMethodCreate,
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> CopingMethodResponse:
    method = service.add_coping_method(user.user_id, payload.method)
    service.db.commit()
    return method


@router.delete("/users/me/settings/coping-methods/{method}", status_code=status.HTTP_204_NO_CONTENT)
def delete_users_me_settings_coping_methods_method(
    method: str,
    user: Annotated[CurrentUserContext, Depends(get_current_user)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> Response:
    deleted = service.remove_coping_method(user.user_id, method)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coping method not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
