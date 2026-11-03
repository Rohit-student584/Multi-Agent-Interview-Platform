from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.resumes import router as resumes_router
from app.core.database import (
    connect_to_mongodb,
    close_mongodb_connection,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_to_mongodb()
    print("Resume Service startup successful")

    yield

    close_mongodb_connection()


app = FastAPI(
    title="Resume Service",
    description="Resume management for the Multi-Agent Interview Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(resumes_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "success": True,
        "service": "resume-service",
        "status": "healthy",
    }