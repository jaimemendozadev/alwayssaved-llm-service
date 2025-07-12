import os

from mistralai import Mistral
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from server.utils.aws.ssm import get_secret
from server.utils.embedding import chunk_text, get_embedd_model
from server.utils.qdrant import get_qdrant_client

QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "alwayssaved_user_files")

MISTRAL_API_KEY = get_secret("/alwayssaved/MISTRAL_API_KEY")

mistral_client = Mistral(api_key=MISTRAL_API_KEY)


def query_llm(message: str) -> str:
    embedding_model: SentenceTransformer = get_embedd_model()
    qdrant_client: QdrantClient = get_qdrant_client()

    # Chunk & vectorize incoming message
    chunks = chunk_text(message)

    vectors = embedding_model.encode(chunks, normalize_embeddings=True)

    # Search Qdrant Database for similar vectors with user message
    hits = qdrant_client.query_points(
        collection_name="my_collection",
        query=vectors,
        limit=5,  # Return 5 closest points
    )

    print(f"hits in query_llm: {hits}")

    return "Success"
