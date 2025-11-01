"""KB ingestion pipeline."""
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "api"))

from db import get_database
from db.models import KBDoc, KBChunk
from .loaders import load_file
from .chunkers import chunk_text, chunk_by_headers
from .embeddings import get_embeddings
import asyncio


async def ingest_document(file_path: str, tags: list = None, chunk_size: int = 500, chunk_overlap: int = 50) -> str:
    """Ingest a single document into the KB."""
    database = await get_database()
    
    # Load file
    doc_data = await load_file(file_path)
    
    # Create KBDoc
    kb_doc = KBDoc(
        source=doc_data["source"],
        title=doc_data["title"],
        rawText=doc_data["rawText"],
        tags=tags or []
    )
    
    # Insert document
    doc_dict = kb_doc.model_dump(by_alias=True, exclude={"id"})
    result = await database.kb_docs.insert_one(doc_dict)
    doc_id = result.inserted_id
    
    # Chunk text
    chunks = chunk_text(doc_data["rawText"], chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    # Process in batches for embeddings
    batch_size = 10
    all_chunks_data = []
    
    for i, chunk_data in enumerate(chunks):
        all_chunks_data.append({
            "docId": doc_id,
            "chunkIndex": i,
            "text": chunk_data["text"],
            "tokens": chunk_data.get("tokens", 0),
            "metadata": {}
        })
    
    # Get embeddings in batches
    texts = [c["text"] for c in all_chunks_data]
    
    print(f"Getting embeddings for {len(texts)} chunks...")
    embeddings_list = await get_embeddings(texts)
    
    # Create KBChunk documents
    kb_chunks = []
    for chunk_data, embedding in zip(all_chunks_data, embeddings_list):
        chunk_data["embedding"] = embedding
        kb_chunks.append(chunk_data)
    
    # Insert chunks
    if kb_chunks:
        await database.kb_chunks.insert_many(kb_chunks)
        print(f"Inserted {len(kb_chunks)} chunks for document {doc_id}")
    
    return str(doc_id)


async def ingest_directory(directory: str, **kwargs) -> List[str]:
    """Ingest all documents in a directory."""
    path = Path(directory)
    doc_ids = []
    
    for file_path in path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in [".pdf", ".html", ".htm", ".md", ".txt"]:
            try:
                print(f"Ingesting {file_path}...")
                doc_id = await ingest_document(str(file_path), **kwargs)
                doc_ids.append(doc_id)
            except Exception as e:
                print(f"Error ingesting {file_path}: {e}")
    
    return doc_ids


if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ingestion.py <file_or_directory>")
        sys.exit(1)
    
    path = sys.argv[1]
    asyncio.run(ingest_directory(path) if Path(path).is_dir() else ingest_document(path))

