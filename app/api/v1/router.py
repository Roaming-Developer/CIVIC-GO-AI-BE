from fastapi import APIRouter

from app.api.v1.routes import auth, documents, files, profile

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
