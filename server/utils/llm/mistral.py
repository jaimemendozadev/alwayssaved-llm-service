import os
from typing import List

from mistralai import Mistral
from qdrant_client.http.models.models import ScoredPoint

from server.utils.aws.ssm import get_secret

QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "alwayssaved_user_files")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "open-mistral-7b")
MISTRAL_API_KEY = get_secret("/alwayssaved/MISTRAL_API_KEY")

mistral_client = Mistral(api_key=MISTRAL_API_KEY)

BASE_LLM_NO_RESPONSE = (
    "I'm sorry, but we can't generate an answer. 😔 Please try asking in another way."
)


def generate_prompt(qdrant_results: List[ScoredPoint], message: str) -> str:
    user_input = ""

    for result in qdrant_results:
        payload = result.payload
        original_text = payload.get("original_chunk_text", "")
        user_input += " " + original_text

    prompt = f"""
    Context information is below.
    ---------------------
    {user_input.strip()}
    ---------------------
    Given the context information and not prior knowledge, answer the query.
    Query: {message}
    Answer:
    """

    print(f"prompt in generate_prompt: {prompt}")

    return prompt


def query_llm(qdrant_hits: List[ScoredPoint], message: str) -> str:
    try:
        prompt = generate_prompt(qdrant_hits, message)
        messages = [{"role": "user", "content": prompt}]

        chat_response = mistral_client.chat.complete(
            model=MISTRAL_MODEL, messages=messages
        )

        # Safety check for empty choices
        if not chat_response.choices:
            print("Warning: Mistral response has no choices.")
            return BASE_LLM_NO_RESPONSE

        # Extract assistant's message
        assistant_message = chat_response.choices[0].message.content.strip()
        return assistant_message

    except Exception as e:
        # Log and return fallback error message
        print(f"Error during LLM query: {e}")
        return BASE_LLM_NO_RESPONSE
