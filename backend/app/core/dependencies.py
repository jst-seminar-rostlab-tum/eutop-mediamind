import os

from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sentry_sdk.integrations import httpx

from app.core.logger import get_logger

security = HTTPBearer()
logger = get_logger(__name__)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        # Authenticate request using Clerk SDK
        sdk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))

        # Manually construct an httpx.Request from FastAPI request data
        clerk_request = httpx.Request(
            method=request.method,
            url=str(request.url),
            headers={
                **request.headers,
                "Authorization": f"Bearer {credentials.credentials}",
            },
        )

        request_state = sdk.authenticate_request(
            clerk_request,
            AuthenticateRequestOptions(
                authorized_parties=["https://example.com"]
            ),
        )

        if not request_state.is_signed_in:
            logger.debug("Invalid authentication credentials (not signed in)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        return request_state.to_dict()

    except Exception as e:
        logger.debug(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        )
