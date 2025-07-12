from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from server.utils.clerk import clerk_authenticate_get_user_details
from server.utils.llm.mistral import query_llm


class ConvoPostRequestBody(BaseModel):
    conversation_id: str
    user_id: str
    sender_type: str
    message: str


convos_router = APIRouter(
    prefix="/convos", dependencies=[Depends(clerk_authenticate_get_user_details)]
)


@convos_router.post("/{convo_id}")
async def handle_incoming_user_message(body: ConvoPostRequestBody, convo_id: str):
    print(f"convo_id: {convo_id}")
    print(f"body: {body}")
    try:
        message = body.message

        query_llm(message)

        return {"status": 200, "message": "IT WORKS! 🚀"}
    except RequestValidationError as e:
        print("Validation error:", e.errors())

    except Exception as e:
        print("Other error:", str(e))

    return {"status": 200, "message": "IT WORKS! 🚀"}
