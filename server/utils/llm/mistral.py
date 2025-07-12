from mistralai import Mistral
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from server.utils.embedding import get_embedd_model
from server.utils.aws.ssm import get_secret

MISTRAL_API_KEY = get_secret("/alwayssaved/MISTRAL_API_KEY")

client = Mistral(api_key=MISTRAL_API_KEY)


def query_llm(message: str) -> str:
    embedding_model: SentenceTransformer = get_embedd_model()
    qdrant_client: QdrantClient = get_qdrant_client()
