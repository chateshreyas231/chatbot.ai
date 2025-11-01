"""Document loaders for KB ingestion."""
import os
from typing import List, Dict
from pathlib import Path
import PyPDF2
from bs4 import BeautifulSoup
import markdown
from db.models import KBDoc


async def load_file(file_path: str) -> Dict:
    """Load and extract text from a file."""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    ext = path.suffix.lower()
    
    if ext == ".pdf":
        return await load_pdf(file_path)
    elif ext in [".html", ".htm"]:
        return await load_html(file_path)
    elif ext in [".md", ".markdown"]:
        return await load_markdown(file_path)
    elif ext == ".txt":
        return await load_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


async def load_pdf(file_path: str) -> Dict:
    """Load PDF file."""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    
    return {
        "rawText": text,
        "title": Path(file_path).stem,
        "source": file_path
    }


async def load_html(file_path: str) -> Dict:
    """Load HTML file."""
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        title = soup.title.string if soup.title else Path(file_path).stem
    
    return {
        "rawText": text,
        "title": title,
        "source": file_path
    }


async def load_markdown(file_path: str) -> Dict:
    """Load Markdown file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
        # Extract title from first H1
        lines = content.split("\n")
        title = Path(file_path).stem
        for line in lines[:10]:  # Check first 10 lines
            if line.startswith("# "):
                title = line[2:].strip()
                break
        
        # Convert to text (basic)
        text = content
    
    return {
        "rawText": text,
        "title": title,
        "source": file_path
    }


async def load_text(file_path: str) -> Dict:
    """Load plain text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return {
        "rawText": content,
        "title": Path(file_path).stem,
        "source": file_path
    }

