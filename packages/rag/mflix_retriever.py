"""Retriever for sample_mflix database."""
from typing import List, Dict, Any, Optional
from bson import ObjectId
import sys
from pathlib import Path

# Add apps/api to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "api"))

from db import get_database
import asyncio


class MflixRetriever:
    """Retriever for sample_mflix database."""
    
    def __init__(self, collection_name: str = "movies", db_name: str = "sample_mflix"):
        self.collection_name = collection_name
        self.db_name = db_name
    
    async def search_movies(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search movies by title, plot, or genres."""
        database = await get_database()
        client = database.client
        mflix_db = client[self.db_name]
        collection = mflix_db[self.collection_name]
        
        # Build search query
        search_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"plot": {"$regex": query, "$options": "i"}},
                {"genres": {"$regex": query, "$options": "i"}},
                {"cast": {"$regex": query, "$options": "i"}},
            ]
        }
        
        # Execute search
        results = []
        async for doc in collection.find(search_query).limit(limit):
            results.append({
                "id": str(doc.get("_id", "")),
                "title": doc.get("title", "N/A"),
                "year": doc.get("year", "N/A"),
                "genres": doc.get("genres", []),
                "plot": doc.get("plot", ""),
                "directors": doc.get("directors", []),
                "cast": doc.get("cast", [])[:5],  # First 5 cast members
                "imdb": doc.get("imdb", {}),
                "type": doc.get("type", "movie"),
            })
        
        return results
    
    async def get_movie_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Get a specific movie by title."""
        database = await get_database()
        client = database.client
        mflix_db = client[self.db_name]
        collection = mflix_db[self.collection_name]
        
        movie = await collection.find_one({"title": {"$regex": f"^{title}$", "$options": "i"}})
        if movie:
            return {
                "id": str(movie.get("_id", "")),
                "title": movie.get("title", "N/A"),
                "year": movie.get("year", "N/A"),
                "genres": movie.get("genres", []),
                "plot": movie.get("plot", ""),
                "directors": movie.get("directors", []),
                "cast": movie.get("cast", []),
                "imdb": movie.get("imdb", {}),
                "runtime": movie.get("runtime", ""),
                "type": movie.get("type", "movie"),
            }
        return None
    
    async def get_top_movies(self, limit: int = 10, genre: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get top rated movies."""
        database = await get_database()
        client = database.client
        mflix_db = client[self.db_name]
        collection = mflix_db[self.collection_name]
        
        query = {}
        if genre:
            query["genres"] = {"$regex": genre, "$options": "i"}
        
        results = []
        async for doc in collection.find(query).sort("imdb.rating", -1).limit(limit):
            if doc.get("imdb", {}).get("rating"):
                results.append({
                    "id": str(doc.get("_id", "")),
                    "title": doc.get("title", "N/A"),
                    "year": doc.get("year", "N/A"),
                    "rating": doc.get("imdb", {}).get("rating"),
                    "genres": doc.get("genres", []),
                })
        
        return results

