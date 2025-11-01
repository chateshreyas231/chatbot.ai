"""Text chunking utilities."""
from typing import List, Dict
import tiktoken


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50, encoding_name: str = "cl100k_base") -> List[Dict[str, str]]:
    """Chunk text into smaller pieces with overlap."""
    encoding = tiktoken.get_encoding(encoding_name)
    
    # Split by paragraphs first
    paragraphs = text.split("\n\n")
    
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = len(encoding.encode(para))
        
        # If paragraph alone is too large, split it
        if para_tokens > chunk_size:
            # Save current chunk if exists
            if current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "tokens": current_tokens
                })
                current_chunk = ""
                current_tokens = 0
            
            # Split large paragraph by sentences
            sentences = para.split(". ")
            for sent in sentences:
                sent_tokens = len(encoding.encode(sent))
                if current_tokens + sent_tokens > chunk_size:
                    if current_chunk:
                        chunks.append({
                            "text": current_chunk.strip(),
                            "tokens": current_tokens
                        })
                    current_chunk = sent + ". "
                    current_tokens = sent_tokens
                else:
                    current_chunk += sent + ". "
                    current_tokens += sent_tokens
        else:
            # Check if adding this paragraph exceeds chunk size
            if current_tokens + para_tokens > chunk_size and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "tokens": current_tokens
                })
                # Start new chunk with overlap
                overlap_text = get_overlap_text(current_chunk, chunk_overlap)
                current_chunk = overlap_text + "\n\n" + para
                current_tokens = len(encoding.encode(current_chunk))
            else:
                current_chunk += "\n\n" + para if current_chunk else para
                current_tokens += para_tokens
    
    # Add final chunk
    if current_chunk:
        chunks.append({
            "text": current_chunk.strip(),
            "tokens": current_tokens
        })
    
    return chunks


def chunk_by_headers(text: str, headers: List[str] = None) -> List[Dict[str, str]]:
    """Chunk text by markdown headers."""
    if headers is None:
        headers = ["# ", "## ", "### "]
    
    lines = text.split("\n")
    chunks = []
    current_chunk = ""
    current_header = ""
    
    for line in lines:
        is_header = any(line.startswith(h) for h in headers)
        
        if is_header:
            # Save previous chunk
            if current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "header": current_header
                })
            
            current_header = line.strip()
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"
    
    # Add final chunk
    if current_chunk:
        chunks.append({
            "text": current_chunk.strip(),
            "header": current_header
        })
    
    return chunks


def get_overlap_text(text: str, overlap_size: int) -> str:
    """Get overlap text from end of chunk."""
    words = text.split()
    if len(words) <= overlap_size:
        return text
    return " ".join(words[-overlap_size:])

