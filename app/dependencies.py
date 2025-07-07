# File: app/dependencies.py

from fastapi import Request, HTTPException, status

# Define our size limit in bytes. 15 MB = 15 * 1024 * 1024 bytes
MAX_REQUEST_SIZE = 15 * 1024 * 1024 

async def limit_content_length(request: Request):
    """
    A dependency that rejects requests if the Content-Length header
    exceeds a predefined maximum size.
    """
    content_length = request.headers.get("content-length")

    # If the header is not present, we can't check.
    # We will let the request proceed and rely on other checks.
    if not content_length:
        return

    try:
        size = int(content_length)
        if size > MAX_REQUEST_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request payload is too large. Limit is {MAX_REQUEST_SIZE / (1024*1024):.2f} MB."
            )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Content-Length header."
        )