
from contextlib import asynccontextmanager
from app.api.feedback import router as feedback_router
from fastapi import FastAPI
from app.api.roadmaps import router as roadmaps_router
from app.api.resumes import router as resumes_router
from app.api.interviews import router as interviews_router

from app.core.database import (
    connect_to_mongodb,
    close_mongodb_connection,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_to_mongodb()
    print("AI Service startup successful")

    yield

    close_mongodb_connection()


app = FastAPI(
    title="AI Service",
    description="AI agents for the Multi-Agent Interview Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Register AI routers
app.include_router(resumes_router)
app.include_router(interviews_router)
app.include_router(feedback_router)
app.include_router(roadmaps_router)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "success": True,
        "service": "ai-service",
        "status": "healthy",
    }
