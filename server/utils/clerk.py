import os
from typing import TypedDict

from clerk_backend_api import AuthenticateRequestOptions, Clerk
from fastapi import HTTPException, Request

from server.utils.mongodb import create_mongodb_instance


class ClerkResult(TypedDict):
    clerk_id: str


# TODO: Use ssm to get Clerk secrets
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_JWT_KEY = os.getenv("CLERK_JWT_KEY")
APP_DOMAIN = os.getenv("APP_DOMAIN")
clerk_sdk = Clerk(bearer_auth=CLERK_SECRET_KEY)

mongo_client = create_mongodb_instance()


async def clerk_authenticate_get_user_details(request: Request) -> ClerkResult:
    print(f"request in clerk_authenticate {request}")
    try:
        if mongo_client is None:
            raise ValueError("Missing MongoDB connection, can't verify user in app.")

        request_state = clerk_sdk.authenticate_request(
            request,
            AuthenticateRequestOptions(
                authorized_parties=[APP_DOMAIN], jwt_key=CLERK_JWT_KEY
            ),
        )

        if not request_state.is_signed_in:
            raise HTTPException(
                status_code=401,
                detail="User does not have valid authentication credentials.",
            )

        clerk_id = request_state.payload.get("sub")

        print(f"clerk_id in clerk auth: {clerk_id}")

        found_user = (
            await mongo_client.get_database("alwayssaved")
            .get_collection("users")
            .find_one({"clerk_id": "blargh123"})
        )

        if found_user is None:
            raise ValueError(
                f"Can't find a user with clerk_id {clerk_id} in the database."
            )

        print(f"found_user in clerk_auth: {found_user}")

        return {"clerk_id": clerk_id}

    except ValueError as e:
        print(f"❌ Exception in clerk_authenticate_get_user_details: {e}")
        raise HTTPException(
            status_code=401, detail="User is unauthorized to use the app."
        )
