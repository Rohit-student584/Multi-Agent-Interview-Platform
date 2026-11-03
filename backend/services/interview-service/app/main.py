from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.interviews import router as interviews_router

from app.core.database import (
    connect_to_mongodb,
    close_mongodb_connection,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_to_mongodb()
    print("Interview Service startup successful")

    yield

    close_mongodb_connection()


app = FastAPI(
    title="Interview Service",
    description="Interview management for the Multi-Agent Interview Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(interviews_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "success": True,
        "service": "interview-service",
        "status": "healthy",
    }