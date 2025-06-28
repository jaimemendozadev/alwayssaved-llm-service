from typing import List

from fastapi import APIRouter, Depends
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from server.utils.clerk import clerk_authenticate_get_user_details


class LLMRequestBody(BaseModel):
    file_ids: List[str]
    message: str


llm_router = APIRouter(
    prefix="/notes", dependencies=[Depends(clerk_authenticate_get_user_details)]
)


@llm_router.post("/{note_id}")
async def query_llm(body: LLMRequestBody, note_id: str):
    print(f"note_id: {note_id}")
    print(f"body: {body}")
    try:
        print(f"note_id: {note_id}")
        print(f"body: {body}")
        print(f"file_ids: {body.file_ids}")
        print(f"message: {body.message}")
        return {"status": 200, "message": "IT WORKS! 🚀"}
    except RequestValidationError as e:
        print("Validation error:", e.errors())

    except Exception as e:
        print("Other error:", str(e))

    return {"status": 200, "message": "IT WORKS! 🚀"}


"""
POST /notes/{noteID}

  {
    file_ids: [fileID, fileID],
    message: String
  }

"""
