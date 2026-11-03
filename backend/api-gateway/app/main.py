from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.gateway import router as gateway_router


app = FastAPI(
    title="Multi-Agent Interview Platform API Gateway",
    description="Central API Gateway for the Multi-Agent Interview Platform",
    version="1.0.0",
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gateway_router)


@app.get("/health")
def health_check():
    return {
        "success": True,
        "service": "api-gateway",
        "status": "healthy",
    }