#!/usr/bin/env python3
"""
Knowledge Base Ingestion Script

Usage:
    python ingest_kb.py [directory]

If no directory is provided, defaults to ../../seeds/kb
"""
import sys
import asyncio
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages"))

from packages.rag.ingestion import ingest_directory, ingest_document


async def main():
    """Main ingestion function."""
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        # Default to seeds/kb
        directory = str(Path(__file__).parent.parent.parent / "seeds" / "kb")
    
    path = Path(directory)
    
    if path.is_file():
        # Single file
        print(f"Ingesting file: {path}")
        try:
            doc_id = await ingest_document(str(path))
            print(f"✅ Successfully ingested: {doc_id}")
        except Exception as e:
            print(f"❌ Error ingesting {path}: {e}")
            sys.exit(1)
    elif path.is_dir():
        # Directory
        print(f"Ingesting directory: {directory}")
        try:
            doc_ids = await ingest_directory(directory)
            print(f"✅ Successfully ingested {len(doc_ids)} documents")
            print(f"Document IDs: {doc_ids}")
        except Exception as e:
            print(f"❌ Error ingesting directory: {e}")
            sys.exit(1)
    else:
        print(f"❌ Error: {directory} is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

