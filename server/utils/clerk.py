import os
from typing import TypedDict

from clerk_backend_api import AuthenticateRequestOptions, Clerk
from fastapi import HTTPException, Request

from server.utils.aws.ssm import get_secret
from server.utils.mongodb import create_mongodb_instance

PYTHON_MODE = os.getenv("PYTHON_MODE", "DEVELOPMENT")

APP_DOMAIN = (
    get_secret("/alwayssaved/FASTAPI_PRODUCTION_APP_DOMAIN")
    if PYTHON_MODE == "PRODUCTION"
    else os.getenv("FASTAPI_DEVELOPMENT_APP_DOMAIN", "http://localhost:3000")
)


class ClerkResult(TypedDict):
    clerk_id: str


async def authenticate_clerk_user(request: Request) -> ClerkResult:

    try:
        LLM_SERVICE_CLERK_SECRET_KEY = get_secret(
            "/alwayssaved/LLM_SERVICE_CLERK_SECRET_KEY"
        )
        LLM_SERVICE_CLERK_JWT_KEY = get_secret("/alwayssaved/LLM_SERVICE_CLERK_JWT_KEY")
        clerk_sdk = Clerk(bearer_auth=LLM_SERVICE_CLERK_SECRET_KEY)
        mongo_client = create_mongodb_instance()

        if (
            mongo_client is None
            or LLM_SERVICE_CLERK_JWT_KEY is None
            or LLM_SERVICE_CLERK_SECRET_KEY is None
            or clerk_sdk is None
        ):
            raise ValueError(
                "Missing MongoDB connection, Clerk SDK, or Clerk Secret Keys. Can't verify user in app."
            )

        request_state = clerk_sdk.authenticate_request(
            request,
            AuthenticateRequestOptions(
                authorized_parties=[APP_DOMAIN], jwt_key=LLM_SERVICE_CLERK_JWT_KEY
            ),
        )

        # Log request_state for CloudWatch and potential debugging issues.
        print(f"request_state in authenticate_clerk_user: {request_state}")

        if not request_state.is_signed_in:
            raise HTTPException(
                status_code=401,
                detail="User does not have valid authentication credentials.",
            )

        clerk_id = request_state.payload.get("sub")

        found_user = (
            await mongo_client.get_database("alwayssaved")
            .get_collection("users")
            .find_one({"clerk_id": clerk_id})
        )

        if found_user is None:
            raise ValueError(
                f"Can't find a user with clerk_id {clerk_id} in the database."
            )

        return {"clerk_id": clerk_id}

    except ValueError as e:
        print(f"❌ Exception in authenticate_clerk_user: {e}")
        raise HTTPException(
            status_code=401, detail="User is unauthorized to use the app."
        )
