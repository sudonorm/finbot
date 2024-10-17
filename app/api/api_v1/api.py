from fastapi import APIRouter
from app.api.api_v1.endpoints import chat, swagger_docs, health

api_router = APIRouter()

api_router.include_router(swagger_docs.router, prefix="/docs", tags=["docs"])

api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
