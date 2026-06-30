"""
chunking.py - Text chunking module for RAG pipeline.

Splits resume text into semantically meaningful chunks with metadata
for storage in the vector database. Uses RecursiveCharacterTextSplitter
from LangChain for intelligent text splitting.
"""

from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.constants import CHUNK_SIZE, CHUNK_OVERLAP


def create_chunks(
    text: str,
    metadata: Dict[str, Any] = None,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    Split text into chunks with metadata.
    
    Uses RecursiveCharacterTextSplitter which tries to split on natural
    boundaries (paragraphs, sentences, words) before falling back to
    character-level splitting.
    
    Args:
        text: The full resume text to chunk.
        metadata: Base metadata to attach to each chunk (e.g., resume name, page).
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of overlapping characters between chunks.
    
    Returns:
        List of chunk dictionaries with 'text', 'metadata', and 'chunk_id'.
    """
    if not text or not text.strip():
        return []
    
    if metadata is None:
        metadata = {}
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", ", ", " ", ""],
    )
    
    documents = splitter.create_documents(
        texts=[text],
        metadatas=[metadata],
    )
    
    chunks = []
    for idx, doc in enumerate(documents):
        chunk_metadata = {**doc.metadata, "chunk_id": idx}
        chunks.append({
            "text": doc.page_content,
            "metadata": chunk_metadata,
            "chunk_id": idx,
        })
    
    return chunks


def create_section_chunks(
    sections: Dict[str, str],
    resume_name: str = "resume",
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    Create chunks from detected resume sections with section-aware metadata.
    
    This preserves section context in metadata so the retriever can
    filter by section type (e.g., only retrieve from 'experience' section).
    
    Args:
        sections: Dictionary mapping section names to their content.
        resume_name: Name of the resume file for metadata.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between chunks.
    
    Returns:
        List of chunk dictionaries with section metadata.
    """
    all_chunks = []
    global_idx = 0
    
    for section_name, section_text in sections.items():
        if not section_text.strip():
            continue
        
        metadata = {
            "section": section_name,
            "resume_name": resume_name,
        }
        
        section_chunks = create_chunks(
            text=section_text,
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        
        # Update chunk IDs to be globally unique
        for chunk in section_chunks:
            chunk["chunk_id"] = global_idx
            chunk["metadata"]["chunk_id"] = global_idx
            global_idx += 1
        
        all_chunks.extend(section_chunks)
    
    return all_chunks


def create_resume_chunks(
    parsed_resume: Dict[str, Any],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    Create chunks from a fully parsed resume.
    
    Prefers section-based chunking when sections are detected,
    falls back to full-text chunking otherwise.
    
    Args:
        parsed_resume: Output from parser.parse_resume().
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between chunks.
    
    Returns:
        List of chunk dictionaries ready for embedding.
    """
    filename = parsed_resume.get("filename", "resume")
    sections = parsed_resume.get("sections", {})
    
    # Use section-based chunking if sections were detected
    if sections and len(sections) > 1:
        chunks = create_section_chunks(
            sections=sections,
            resume_name=filename,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    else:
        # Fall back to full text chunking
        metadata = {
            "resume_name": filename,
            "section": "full_text",
        }
        chunks = create_chunks(
            text=parsed_resume.get("text", ""),
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    
    # Add page number metadata where possible
    pages = parsed_resume.get("pages", [])
    if pages:
        _assign_page_numbers(chunks, pages)
    
    return chunks


def _assign_page_numbers(chunks: List[Dict], pages: List[Dict]) -> None:
    """
    Assign page numbers to chunks by matching chunk text to page content.
    
    This is a best-effort assignment — if a chunk spans pages, it gets
    the page number where it first appears.
    """
    for chunk in chunks:
        chunk_text = chunk["text"][:100]  # Use first 100 chars for matching
        
        for page in pages:
            if chunk_text in page.get("text", ""):
                chunk["metadata"]["page_number"] = page["page_number"]
                break
        else:
            # Default to page 1 if no match found
            chunk["metadata"]["page_number"] = 1
