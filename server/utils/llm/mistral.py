import os
from typing import List

import numpy as np
from mistralai import Mistral
from qdrant_client import QdrantClient
from qdrant_client.http.models.models import ScoredPoint
from sentence_transformers import SentenceTransformer

from server.utils.aws.ssm import get_secret
from server.utils.embedding import chunk_text, get_embedd_model
from server.utils.qdrant import get_qdrant_client

QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "alwayssaved_user_files")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-7b-instruct-v0.1")
MISTRAL_API_KEY = get_secret("/alwayssaved/MISTRAL_API_KEY")

mistral_client = Mistral(api_key=MISTRAL_API_KEY)


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


def query_llm(message: str) -> str:
    embedding_model: SentenceTransformer = get_embedd_model()
    qdrant_client: QdrantClient = get_qdrant_client()

    # Chunk & vectorize incoming message
    chunks = chunk_text(message)

    vectors = embedding_model.encode(chunks, normalize_embeddings=True)

    query_vector = np.mean(vectors, axis=0)

    # Search Qdrant Database for similar vectors with user message
    hits = qdrant_client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_vector.tolist(),
        limit=5,  # Return 5 closest points
    )

    # print(f"hits in query_llm: {hits}")

    if len(hits) > 0:
        prompt = generate_prompt(hits, message)
        # messages = [
        #     {"role": "user", "content": prompt}
        #     ]
        # chat_response = mistral_client.chat.complete(
        #     model=MISTRAL_MODEL,
        #     messages=messages
        #     )
        # print(f"chat_response: {chat_response}")
    else:
        return "Error"
