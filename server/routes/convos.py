from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from server.utils.clerk import clerk_authenticate_get_user_details


class LLMRequestBody(BaseModel):
    conversation_id: str
    user_id: str
    sender_type: str
    message: str


convos_router = APIRouter(
    prefix="/convos", dependencies=[Depends(clerk_authenticate_get_user_details)]
)


@convos_router.post("/{convo_id}")
async def query_llm(body: LLMRequestBody, convo_id: str):
    print(f"convo_id: {convo_id}")
    print(f"body: {body}")
    try:
        print(f"conversation_id: {body.conversation_id}")
        print(f"user_id: {body.user_id}")
        print(f"sender_type: {body.sender_type}")
        print(f"message: {body.message}")

        return {"status": 200, "message": "IT WORKS! 🚀"}
    except RequestValidationError as e:
        print("Validation error:", e.errors())

    except Exception as e:
        print("Other error:", str(e))

    return {"status": 200, "message": "IT WORKS! 🚀"}
