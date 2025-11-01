"""Vector retrieval using MongoDB Atlas Vector Search."""
from typing import List, Dict, Any, Optional
from bson import ObjectId
import sys
from pathlib import Path

# Add apps/api to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "api"))

from db import get_database
from .embeddings import embed_query
import config


class VectorRetriever:
    """Retriever for MongoDB Atlas Vector Search."""
    
    def __init__(self, collection_name: str = "kb_chunks", index_name: str = "kb_chunks_vec"):
        self.collection_name = collection_name
        self.index_name = index_name
    
    async def retrieve(self, query: str, k: int = 6, filter_dict: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Retrieve top-k chunks for a query."""
        database = await get_database()
        collection = database[self.collection_name]
        
        # Get query embedding
        query_vector = await embed_query(query)
        
        # Build aggregation pipeline for vector search
        pipeline = [
            {
                "$vectorSearch": {
                    "index": self.index_name,
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": min(200, k * 20),
                    "limit": k,
                    "filter": filter_dict or {}
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "docId": 1,
                    "chunkIndex": 1,
                    "text": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        # Try vector search first, fallback to simple similarity if not available
        try:
            results = []
            async for doc in collection.aggregate(pipeline):
                results.append({
                    "id": str(doc["_id"]),
                    "docId": str(doc["docId"]),
                    "chunkIndex": doc.get("chunkIndex", 0),
                    "text": doc["text"],
                    "metadata": doc.get("metadata", {}),
                    "score": doc.get("score", 0.0)
                })
            return results
        except Exception as e:
            # Fallback: simple cosine similarity on client side
            # This is less efficient but works if Vector Search isn't enabled
            print(f"Vector search failed: {e}, using fallback")
            return await self._fallback_retrieve(query_vector, k, filter_dict)
    
    async def _fallback_retrieve(self, query_vector: List[float], k: int, filter_dict: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Fallback retrieval using cosine similarity."""
        import numpy as np
        from db import get_database
        
        database = await get_database()
        collection = database[self.collection_name]
        
        # Fetch all chunks (or filtered subset)
        query = filter_dict or {}
        chunks = []
        
        async for doc in collection.find(query):
            chunks.append({
                "id": str(doc["_id"]),
                "docId": str(doc["docId"]),
                "chunkIndex": doc.get("chunkIndex", 0),
                "text": doc["text"],
                "metadata": doc.get("metadata", {}),
                "embedding": doc.get("embedding", [])
            })
        
        # Compute cosine similarity
        query_vec = np.array(query_vector)
        similarities = []
        
        for chunk in chunks:
            if not chunk["embedding"]:
                continue
            chunk_vec = np.array(chunk["embedding"])
            similarity = np.dot(query_vec, chunk_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(chunk_vec))
            similarities.append((chunk, similarity))
        
        # Sort by similarity and return top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {
                **chunk,
                "score": float(score),
                "embedding": []  # Remove embedding from response
            }
            for chunk, score in similarities[:k]
        ]


# Global retriever instance
_retriever = None


async def retrieve_kb(query: str, k: int = 6) -> List[Dict[str, Any]]:
    """Convenience function to retrieve KB chunks."""
    global _retriever
    try:
        if _retriever is None:
            _retriever = VectorRetriever()
        
        return await _retriever.retrieve(query, k)
    except Exception as e:
        print(f"Error in retrieve_kb: {e}")
        import traceback
        traceback.print_exc()
        # Return empty list to trigger LLM fallback
        return []

