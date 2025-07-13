import os
from typing import List

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.conversions.common_types import CollectionInfo
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models.models import ScoredPoint
from sentence_transformers import SentenceTransformer

from server.utils.aws.ssm import get_secret
from server.utils.embedding import chunk_text, get_embedd_model

QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "alwayssaved_user_files")


def get_qdrant_client() -> QdrantClient | None:

    try:
        qdrant_url = get_secret("/alwayssaved/QDRANT_URL")
        qdrant_api_key = get_secret("/alwayssaved/QDRANT_API_KEY")

        if qdrant_url is None or qdrant_api_key is None:
            raise ValueError(
                "QDRANT_URL or QDRANT_API_KEY environment variables are not set."
            )
        # Connect to Qdrant
        qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        return qdrant

    except ValueError as e:
        print(f"❌ Value Error in get_qdrant_client: {e}")
        return None


def get_qdrant_collection(q_client: QdrantClient) -> CollectionInfo | None:

    try:
        return q_client.get_collection(collection_name=QDRANT_COLLECTION_NAME)

    except UnexpectedResponse as e:
        print(f"❌ QdrantClient UnexpectedResponse Error in get_qdrant_collection: {e}")

    return None


def query_qdrant_with_message(
    message: str, user_id: str, convo_id: str
) -> List[ScoredPoint]:
    embedding_model: SentenceTransformer = get_embedd_model()
    qdrant_client: QdrantClient = get_qdrant_client()

    if not qdrant_client:
        print(
            f"❌ Qdrant client could not be initialized for User {user_id} Convo {convo_id}."
        )
        return []

    if not message:
        print(f"⚠️ Message is empty or None User {user_id} Convo {convo_id}.")
        return []

    try:
        chunks = chunk_text(message)
        if not chunks:
            print(
                f"⚠️ No chunks generated from the input message for User {user_id} Convo {convo_id}."
            )
            return []

        vectors = embedding_model.encode(chunks, normalize_embeddings=True)
        if not vectors.any():
            print(
                f"⚠️ Failed to generate vectors from the message for User {user_id} Convo {convo_id}."
            )
            return []

        query_vector = np.mean(vectors, axis=0)

        hits = qdrant_client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_vector.tolist(),
            limit=5,
        )

        if not hits:
            print(
                f"ℹ️ No results found for the query for User {user_id} Convo {convo_id}."
            )
            return []

        return hits

    except UnexpectedResponse as e:
        print(
            f"❌ Unexpected response from Qdrant for User {user_id} Convo {convo_id}: {e}"
        )
    except Exception as e:
        print(
            f"❌ General error during Qdrant query for User {user_id} Convo {convo_id}: {e}"
        )

    return []
