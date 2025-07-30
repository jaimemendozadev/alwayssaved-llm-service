import os
from typing import Any, List, Optional, Union

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from pymongo.errors import ServerSelectionTimeoutError

from server.utils.clerk import authenticate_clerk_user
from server.utils.llm.mistral import BASE_LLM_NO_RESPONSE, query_llm
from server.utils.mongodb import create_mongodb_instance, deep_serialize_mongo
from server.utils.qdrant import query_qdrant_with_message


class ConvoPostRequestBody(BaseModel):
    conversation_id: str
    user_id: str
    sender_type: str
    message: str
    file_ids_list: List[str]
    note_id: str


class BackendResponse(BaseModel):
    status: int
    payload: Optional[Union[Any, list[Any]]] = None
    message: Optional[str] = None


convos_router = APIRouter(
    prefix="/convos", dependencies=[Depends(authenticate_clerk_user)]
)

LLM_COMPANY = os.getenv("LLM_COMPANY", "Unknown")
LLM_MODEL = os.getenv("LLM_MODEL", "Unknown")


@convos_router.post("/{convo_id}", response_model=BackendResponse)
async def handle_incoming_user_message(body: ConvoPostRequestBody, convo_id: str):

    user_id = body.user_id
    conversation_id = body.conversation_id
    user_id = body.user_id
    file_ids_list = body.file_ids_list
    note_id = body.note_id
    try:
        message = body.message

        mongo_client = create_mongodb_instance()
        if mongo_client is None:
            raise RuntimeError("Failed to connect to MongoDB")

        convo_msg_collection = mongo_client.get_database("alwayssaved").get_collection(
            "convomessages"
        )

        user_msg = await convo_msg_collection.insert_one(
            {
                "conversation_id": ObjectId(conversation_id),
                "user_id": ObjectId(user_id),
                "sender_type": "user",
                "message": message,
            }
        )

        user_msg_id = str(user_msg.inserted_id)

        qdrant_hits = query_qdrant_with_message(
            message, user_id, note_id, file_ids_list
        )

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

            inserted_doc = await convo_msg_collection.find_one(
                {"_id": llm_message.inserted_id}
            )
            sanitized_doc = deep_serialize_mongo(inserted_doc)
            return BackendResponse(
                status=200,
                payload={"user_msg_id": user_msg_id, "llm_response": sanitized_doc},
            )

        llm_error_message = await convo_msg_collection.insert_one(
            {
                "conversation_id": ObjectId(conversation_id),
                "user_id": ObjectId(user_id),
                "sender_type": "llm",
                "message": BASE_LLM_NO_RESPONSE,
                "llm_info": {"llm_company": LLM_COMPANY, "llm_model": LLM_MODEL},
            }
        )

        inserted_doc = await convo_msg_collection.find_one(
            {"_id": llm_error_message.inserted_id}
        )
        sanitized_doc = deep_serialize_mongo(inserted_doc)

        return BackendResponse(
            status=200,
            payload={"user_msg_id": user_msg_id, "llm_response": sanitized_doc},
        )

    except RequestValidationError as e:
        print(f"RequestValidationError for Convo {convo_id}: ", e.errors())
        raise HTTPException(
            status_code=422,
            detail={"status": 422, "error": "Validation Error", "message": str(e)},
        )

    except ServerSelectionTimeoutError:
        print("MongoDB connection timed out.")
        raise HTTPException(
            status_code=503, detail={"status": 503, "message": "Database unavailable"}
        )

    except Exception as e:
        print(f"Unhandled error for Convo {convo_id}: ", str(e))
        raise HTTPException(
            status_code=500, detail={"status": 500, "message": "Internal server error"}
        )
