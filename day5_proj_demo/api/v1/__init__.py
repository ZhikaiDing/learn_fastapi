from fastapi import APIRouter
from api.v1.auth import router as auth_router
from api.v1.model_config import router as model_cfg_router
from api.v1.chat import router as chat_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(model_cfg_router)
api_router.include_router(chat_router)
