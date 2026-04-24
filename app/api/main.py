from fastapi import FastAPI

from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.emotions import router as emotions_router
from app.api.v1.users import router as users_router
from app.api.v1.notifications import router as notifications_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# TODO What does it do?
@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}

app.include_router(admin_router, prefix=settings.API_V1_PREFIX, tags=["Admin"])
app.include_router(auth_router, prefix=settings.API_V1_PREFIX, tags=["Auth"])
app.include_router(users_router, prefix=settings.API_V1_PREFIX, tags=["Users"])
app.include_router(emotions_router, prefix=settings.API_V1_PREFIX, tags=["Emotions"])
app.include_router(notifications_router, prefix=settings.API_V1_PREFIX, tags=["Notifications"])
