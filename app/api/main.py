from fastapi import APIRouter, FastAPI
from datetime import datetime

router = APIRouter(tags=["Health"])
app = FastAPI()

@router.get("/health")
async def get_health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": "healthy",
            "api": "healthy"
        }
    }
