"""
helpers.py - Utility functions used across the project.

Contains text cleaning, validation, formatting, and other shared utilities.
"""

import re
import os
from typing import List, Optional, Dict, Any


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text.
    
    Removes extra whitespace, special characters, and normalizes line breaks
    while preserving meaningful structure.
    """
    if not text:
        return ""
    
    # Replace multiple newlines with double newline (paragraph break)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Remove non-printable characters except newlines
    text = re.sub(r'[^\S\n]+', ' ', text)
    
    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()


def extract_email(text: str) -> Optional[str]:
    """Extract the first email address from text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extract the first phone number from text."""
    patterns = [
        r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'(?:\+\d{1,3}[-.\s]?)?\d{10,12}',
        r'(?:\+\d{1,3}[-.\s]?)?\d{3}[-.\s]\d{3}[-.\s]\d{4}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip()
    return None


def extract_links(text: str) -> List[str]:
    """Extract URLs and links from text."""
    pattern = r'https?://[^\s<>\"\']+|www\.[^\s<>\"\']+|(?:linkedin|github)\.com/[^\s<>\"\']+'
    links = re.findall(pattern, text, re.IGNORECASE)
    return list(set(links))


def extract_name(text: str) -> Optional[str]:
    """
    Extract candidate name from the resume text.
    
    Heuristic: The name is typically the first non-empty line that doesn't
    look like an email, phone, URL, or section header.
    """
    lines = text.strip().split('\n')
    
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if not line or len(line) < 2:
            continue
        
        # Skip lines that look like contact info
        if '@' in line or 'http' in line.lower() or 'www.' in line.lower():
            continue
        if re.search(r'\d{3}[-.\s]\d{3}', line):  # Phone number
            continue
        
        # Skip common section headers
        header_words = ['resume', 'curriculum', 'vitae', 'cv', 'objective', 'summary', 'experience']
        if line.lower().strip() in header_words:
            continue
        
        # A name is usually 2-5 words, all alphabetic
        words = line.split()
        if 1 <= len(words) <= 5 and all(re.match(r'^[a-zA-Z.\'-]+$', w) for w in words):
            return line
    
    return None


def validate_file(file_obj) -> Dict[str, Any]:
    """
    Validate an uploaded file for size and type.
    
    Returns a dict with 'valid' (bool) and 'error' (str or None).
    """
    from utils.constants import MAX_FILE_SIZE_BYTES, ALLOWED_EXTENSIONS
    
    result = {"valid": True, "error": None}
    
    if file_obj is None:
        result["valid"] = False
        result["error"] = "No file uploaded."
        return result
    
    # Check file size
    file_obj.seek(0, 2)  # Seek to end
    file_size = file_obj.tell()
    file_obj.seek(0)  # Reset position
    
    if file_size > MAX_FILE_SIZE_BYTES:
        result["valid"] = False
        result["error"] = f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
        return result
    
    if file_size == 0:
        result["valid"] = False
        result["error"] = "File is empty."
        return result
    
    # Check extension
    filename = getattr(file_obj, 'name', '')
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        result["valid"] = False
        result["error"] = f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        return result
    
    return result


def normalize_skill(skill: str) -> str:
    """Normalize a skill name for comparison."""
    skill = skill.lower().strip()
    skill = re.sub(r'[^a-z0-9\s.+#]', '', skill)
    skill = re.sub(r'\s+', ' ', skill)
    return skill


def calculate_percentage(value: float, total: float) -> float:
    """Calculate percentage safely."""
    if total == 0:
        return 0.0
    return round((value / total) * 100, 1)


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max_length, adding ellipsis if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_score(score: float) -> str:
    """Format a score as a percentage string."""
    return f"{score:.1f}%"


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection.
    
    Removes potential prompt injection patterns while keeping
    the meaningful content intact.
    """
    if not text:
        return ""
    
    # Remove potential system prompt overrides
    dangerous_patterns = [
        r'(?i)ignore\s+(all\s+)?previous\s+instructions',
        r'(?i)you\s+are\s+now\s+',
        r'(?i)system\s*:\s*',
        r'(?i)assistant\s*:\s*',
        r'(?i)forget\s+(everything|all)',
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '[FILTERED]', text)
    
    return text.strip()


def get_file_extension(filename: str) -> str:
    """Get lowercase file extension."""
    return os.path.splitext(filename)[1].lower()


def deduplicate_list(items: List[str], case_insensitive: bool = True) -> List[str]:
    """Remove duplicates from a list while preserving order."""
    seen = set()
    result = []
    for item in items:
        key = item.lower() if case_insensitive else item
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result
