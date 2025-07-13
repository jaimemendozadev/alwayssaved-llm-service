from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from server.utils.clerk import authenticate_clerk_user
from server.utils.llm.mistral import query_llm
from server.utils.mongodb import create_mongodb_instance
from server.utils.qdrant import query_qdrant_with_message


class ConvoPostRequestBody(BaseModel):
    conversation_id: str
    user_id: str
    sender_type: str
    message: str


convos_router = APIRouter(
    prefix="/convos", dependencies=[Depends(authenticate_clerk_user)]
)


@convos_router.post("/{convo_id}")
async def handle_incoming_user_message(body: ConvoPostRequestBody, convo_id: str):
    print(f"convo_id: {convo_id}")
    print(f"body: {body}")
    try:
        message = body.message

        mongo_client = create_mongodb_instance()

        # mongo_client.get_database("alwayssaved").get_collection("users").find_one({"clerk_id": clerk_id})

        qdrant_hits = query_qdrant_with_message(message)

        if len(qdrant_hits) > 0:
            query_llm(qdrant_hits, message)

        return {"status": 200, "message": "IT WORKS! 🚀"}
    except RequestValidationError as e:
        print("Validation error:", e.errors())

    except Exception as e:
        print("Other error:", str(e))

    return {"status": 200, "message": "IT WORKS! 🚀"}
