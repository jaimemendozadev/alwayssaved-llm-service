import os

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from pymongo.errors import ServerSelectionTimeoutError

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

LLM_COMPANY = os.getenv("LLM_COMPANY", "Unknown")
LLM_MODEL = os.getenv("LLM_MODEL", "Unknown")


@convos_router.post("/{convo_id}")
async def handle_incoming_user_message(body: ConvoPostRequestBody, convo_id: str):
    print(f"convo_id: {convo_id}")
    print(f"body: {body}")

    user_id = body.user_id
    conversation_id = body.conversation_id
    user_id = body.user_id
    try:
        message = body.message

        mongo_client = create_mongodb_instance()
        if mongo_client is None:
            raise RuntimeError("Failed to connect to MongoDB")

        convo_msg_collection = mongo_client.get_database("alwayssaved").get_collection(
            "convomessages"
        )

        await convo_msg_collection.insert_one(
            {
                "conversation_id": ObjectId(conversation_id),
                "user_id": ObjectId(user_id),
                "sender_type": "user",
                "message": message,
            }
        )

        qdrant_hits = query_qdrant_with_message(message, user_id, conversation_id)

        if len(qdrant_hits) > 0:
            llm_response = query_llm(qdrant_hits, message, user_id, conversation_id)

            llm_message = await convo_msg_collection.insert_one(
                {
                    "conversation_id": ObjectId(conversation_id),
                    "user_id": ObjectId(user_id),
                    "sender_type": "llm",
                    "message": llm_response,
                    "llm_info": {"llm_company": LLM_COMPANY, "llm_model": LLM_MODEL},
                }
            )
            return {"status": 200, "payload": llm_message}

        llm_error_message = await convo_msg_collection.insert_one(
            {
                "conversation_id": ObjectId(conversation_id),
                "user_id": ObjectId(user_id),
                "sender_type": "llm",
                "message": BASE_LLM_NO_RESPONSE,
                "llm_info": {"llm_company": LLM_COMPANY, "llm_model": LLM_MODEL},
            }
        )

        return {"status": 200, "payload": llm_error_message}

    except RuntimeError:
        print("MongoDB connection timed out.")
        return {"status": 503, "message": "Database unavailable"}

    except ServerSelectionTimeoutError:
        print("MongoDB connection timed out.")
        return {"status": 503, "message": "Database unavailable"}

    except RequestValidationError as e:
        print(f"RequestValidationError for Convo {convo_id}: ", e.errors())

    except Exception as e:
        print(f"Other error for Convo {convo_id}: ", str(e))

    return {"status": 500, "message": BASE_LLM_NO_RESPONSE}
