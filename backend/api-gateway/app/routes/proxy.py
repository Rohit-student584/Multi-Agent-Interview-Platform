import httpx
from fastapi import Request, Response
from fastapi.responses import JSONResponse


HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


async def forward_request(
    request: Request,
    target_url: str,
    path: str = "",
) -> Response:
    """
    Forward an incoming API Gateway request to a microservice.
    """

    target = f"{target_url.rstrip('/')}/{path.lstrip('/')}"

    # Preserve query parameters
    if request.url.query:
        target = f"{target}?{request.url.query}"

    # Forward request headers except hop-by-hop headers
    request_headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
        and key.lower() not in {"host", "content-length"}
    }

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            upstream = await client.request(
                method=request.method,
                url=target,
                headers=request_headers,
                content=await request.body(),
            )

    except httpx.RequestError:
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "message": "The requested service is currently unavailable.",
            },
        )

    # Forward the upstream response to the client
    response_headers = {
        key: value
        for key, value in upstream.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
        and key.lower() not in {"content-length", "content-encoding"}
    }

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
    )