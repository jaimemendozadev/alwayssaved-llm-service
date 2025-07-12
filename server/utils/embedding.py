import os

import torch
from sentence_transformers import SentenceTransformer


def get_embedd_model() -> SentenceTransformer:
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"✅ Using device for embedd model: {device}")

    model_name = os.getenv("EMBEDDING_MODEL", "multi-qa-MiniLM-L6-cos-v1")

    embedding_model = SentenceTransformer(model_name_or_path=model_name, device=device)

    return embedding_model


def chunk_text(text, chunk_size=1000, overlap=100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks
