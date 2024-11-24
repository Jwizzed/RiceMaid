from fastapi import APIRouter

from app.api import api_messages
from app.api.endpoints import auth, iot, line_user, line_webhook, users, carbon_credit

# Create the auth router
auth_router = APIRouter()
auth_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Create the main API router with common responses
api_router = APIRouter(
    responses={
        401: {
            "description": "No `Authorization` access token header, token is invalid or user removed",
            "content": {
                "application/json": {
                    "examples": {
                        "not authenticated": {
                            "summary": "No authorization token header",
                            "value": {"detail": "Not authenticated"},
                        },
                        "invalid token": {
                            "summary": "Token validation failed, decode failed, it may be expired or malformed",
                            "value": {"detail": "Token invalid: {detailed error msg}"},
                        },
                        "removed user": {
                            "summary": api_messages.JWT_ERROR_USER_REMOVED,
                            "value": {"detail": api_messages.JWT_ERROR_USER_REMOVED},
                        },
                    }
                }
            },
        },
        422: {
            "description": "Validation error for prediction inputs",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_file": {
                            "summary": "Invalid file format or missing file",
                            "value": {"detail": "Invalid file format or file not found"},
                        },
                        "invalid_model": {
                            "summary": "Model weights file not found or invalid",
                            "value": {"detail": "Model weights file not found or invalid"},
                        },
                    }
                }
            },
        },
    }
)

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(line_webhook.router, prefix="/line", tags=["line"])
api_router.include_router(iot.router, prefix="/iot", tags=["iot"])
api_router.include_router(carbon_credit.router, prefix="/carbon-credit", tags=["carbon_credit"])
api_router.include_router(line_user.router, prefix="/line-user", tags=["line_user"])
