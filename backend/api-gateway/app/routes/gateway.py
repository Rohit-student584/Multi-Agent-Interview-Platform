from fastapi import APIRouter, HTTPException, Request

from app.core.config import (
    AUTH_SERVICE_URL,
    USER_SERVICE_URL,
    RESUME_SERVICE_URL,
    INTERVIEW_SERVICE_URL,
    AI_SERVICE_URL,
)
from app.routes.proxy import forward_request


router = APIRouter()

# Map API prefixes to their respective microservices
SERVICE_URLS = {
    "auth": AUTH_SERVICE_URL,
    "users": USER_SERVICE_URL,
    "resume": RESUME_SERVICE_URL,
    "interview": INTERVIEW_SERVICE_URL,
    "ai": AI_SERVICE_URL,
}

HTTP_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
    "HEAD",
]


@router.api_route(
    "/api/{service}/{path:path}",
    methods=HTTP_METHODS,
)
async def route_to_service(
    request: Request,
    service: str,
    path: str,
):
    target_url = SERVICE_URLS.get(service)

    if not target_url:
        raise HTTPException(
            status_code=404,
            detail="Microservice not found",
        )

    return await forward_request(
        request=request,
        target_url=target_url,
        path=path,
    )