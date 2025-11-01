"""Embedding utilities using OpenAI."""
from typing import List
import openai
import sys
from pathlib import Path

# Add apps/api to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "api"))

from config import settings

openai.api_key = settings.openai_api_key


async def get_embeddings(texts: List[str], model: str = None) -> List[List[float]]:
    """Get embeddings for a list of texts."""
    model = model or settings.embedding_model
    
    # Use OpenAI client
    client = openai.OpenAI(api_key=settings.openai_api_key)
    
    response = client.embeddings.create(
        model=model,
        input=texts
    )
    
    return [item.embedding for item in response.data]


async def embed_query(query: str, model: str = None) -> List[float]:
    """Get embedding for a single query."""
    model = model or settings.embedding_model
    
    client = openai.OpenAI(api_key=settings.openai_api_key)
    
    response = client.embeddings.create(
        model=model,
        input=[query]
    )
    
    return response.data[0].embedding

