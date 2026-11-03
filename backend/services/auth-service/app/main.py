from fastapi import FastAPI

app = FastAPI(
    title="Authentication Service",
    description="Authentication service for the Multi-Agent Interview Platform",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {
        "success": True,
        "service": "auth-service",
        "status": "healthy",
    }