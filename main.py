from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List
import logging

from models import (
    ErrorResponse
)
from services import JagritiService
from config import Config
from app.api.routers.metadata import router as metadata_router
from app.api.routers.cases import router as cases_router
from app.deps import get_jagriti_service
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=Config.API_TITLE,
    version=Config.API_VERSION,
    description=Config.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
        return response


app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error="Bad Request",
            message=str(exc),
            status_code=400
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message="An unexpected error occurred",
            status_code=500
        ).dict()
    )

# Health check endpoint


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Lexi Jagriti API"}

# Metadata endpoints


app.include_router(metadata_router)
app.include_router(cases_router, prefix="/cases")

# Case search endpoints


@app.on_event("startup")
async def on_startup():
    app.state.jagriti_service = JagritiService()

# Shutdown event


@app.on_event("shutdown")
async def shutdown_event():
    await app.state.jagriti_service.close()


@app.get("/documents/{document_id}")
async def get_document(document_id: str, service: JagritiService = Depends(get_jagriti_service)):
    data = service.get_document_bytes(document_id)
    if not data:
        raise HTTPException(status_code=404, detail="Document not found")
    return StreamingResponse(iter([data]), media_type="application/pdf")


# Removed document streaming endpoint per requirement; links are direct absolute URLs for clients

if __name__ == "__main__":
    import uvicorn
    if Config.DEBUG:
        uvicorn.run("main:app", host=Config.HOST,
                    port=Config.PORT, reload=True)
    else:
        uvicorn.run(app, host=Config.HOST, port=Config.PORT)
