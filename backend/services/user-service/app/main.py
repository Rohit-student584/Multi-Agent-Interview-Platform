from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.users import router as users_router
from app.core.database import (
    connect_to_mongodb,
    close_mongodb_connection,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_to_mongodb()
    print("User Service startup successful")

    yield

    close_mongodb_connection()
    print("MongoDB connection closed")


app = FastAPI(
    title="User Service",
    description="User profile management for the Multi-Agent Interview Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Register user profile APIs
app.include_router(users_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "success": True,
        "service": "user-service",
        "status": "healthy",
    }