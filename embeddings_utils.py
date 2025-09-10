# embeddings_utils.py
import re
from openai import OpenAI
import cohere
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

client_openai = OpenAI(api_key=OPENAI_API_KEY)
co = cohere.Client(COHERE_API_KEY)

EMBEDDING_MODEL = "text-embedding-3-large"

def normalize_text(text: str) -> str:
    """Limpa e normaliza o texto"""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text

def create_embedding(text: str) -> list:
    """Cria embedding próprio usando OpenAI"""
    response = client_openai.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding

def re_rank_with_cohere(query: str, docs: list) -> list:
    """
    Reordena documentos usando Cohere Rerank
    docs: [{'text':..., 'metadata':...}]
    """
    if not docs:
        return []

    response = co.rerank(
        model="rerank-v3.5",
        query=query,
        documents=[d["text"] for d in docs],
        top_n=len(docs)
    )
    return [docs[item.index] for item in response.results]
