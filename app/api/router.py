from fastapi import APIRouter

from app.api.v1.endpoints.default import default_router
from app.api.v1.endpoints.rate_limit import rate_limit

api_router = APIRouter()

api_router.include_router(default_router)
api_router.include_router(rate_limit)

