from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from server.utils.clerk import authenticate_clerk_user
from server.utils.llm.mistral import BASE_LLM_NO_RESPONSE, query_llm
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

    user_id = body.user_id
    conversation_id = body.conversation_id
    try:
        message = body.message

        mongo_client = create_mongodb_instance()

        qdrant_hits = query_qdrant_with_message(
            message, message, user_id, conversation_id
        )

        if len(qdrant_hits) > 0:
            llm_response = query_llm(qdrant_hits, message, user_id, conversation_id)
            return {"status": 200, "message": llm_response}

        mongo_client.get_database("alwayssaved").get_collection("users").find_one(
            {"clerk_id": clerk_id}
        )

        return {"status": 200, "message": BASE_LLM_NO_RESPONSE}
    except RequestValidationError as e:
        print(f"RequestValidationError for Convo {convo_id}: ", e.errors())

    except Exception as e:
        print(f"Other error for Convo {convo_id}: ", str(e))

    return {"status": 500, "message": BASE_LLM_NO_RESPONSE}
