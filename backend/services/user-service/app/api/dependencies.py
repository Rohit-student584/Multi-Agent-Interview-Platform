from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError

from app.core.firebase import verify_firebase_token


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    """Verify the Firebase ID token and return authenticated user claims."""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        decoded_token = verify_firebase_token(credentials.credentials)

    except (
        auth.InvalidIdTokenError,
        auth.ExpiredIdTokenError,
        auth.RevokedIdTokenError,
        auth.UserDisabledError,
        ValueError,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except FirebaseError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication verification is temporarily unavailable.",
        )

    return decoded_token