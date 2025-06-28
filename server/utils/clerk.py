import os

from clerk_backend_api import AuthenticateRequestOptions, Clerk
from fastapi import HTTPException, Request

CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
CLERK_JWT_KEY = os.getenv("CLERK_JWT_KEY")
APP_DOMAIN = os.getenv("APP_DOMAIN")
clerk_sdk = Clerk(bearer_auth=CLERK_SECRET_KEY)


# TODO: Add MongoDB access to check for user_info in DB.
def clerk_authenticate_get_user_details(request: Request):
    print(f"request in clerk_authenticate {request}")
    try:
        request_state = clerk_sdk.authenticate_request(
            request,
            AuthenticateRequestOptions(
                authorized_parties=[APP_DOMAIN], jwt_key=CLERK_JWT_KEY
            ),
        )

        print(f"request_state: {request_state}")

        if not request_state.is_signed_in:
            raise HTTPException(
                status_code=401,
                detail="User does not have valid authentication credentials.",
            )

        user_id = request_state.payload.get("sub")

        print(f"user_id in clerk auth: {user_id}")

        # Only for Dev to test response on FE, DELETE ASAP
        raise HTTPException(status_code=500, detail="Internal auth error")

        # TODO: Need to make MongoDB API call to verify user exists.
        return {"user_id": user_id}

    except HTTPException as e:
        print(f"❌ HTTPException in clerk_authenticate_get_user_details: {e}")
        raise e

    except Exception as e:
        print(f"❌ Exception in clerk_authenticate_get_user_details: {e}")
        raise HTTPException(status_code=500, detail="Internal auth error")
