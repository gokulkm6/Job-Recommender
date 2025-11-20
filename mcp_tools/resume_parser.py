import os
import re
from typing import Dict, Any

from PyPDF2 import PdfReader
import spacy

_SPACY_MODEL = os.getenv("SPACY_MODEL", "en_core_web_sm")
nlp = spacy.load(_SPACY_MODEL)

DEFAULT_SKILLS_DB = [
    "python", "java", "excel", "data analysis", "sql",
    "machine learning", "c++", "javascript", "react", "django",
    "fastapi", "docker", "kubernetes", "aws", "azure"
]

def _extract_text_from_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        reader = PdfReader(file_path)
        texts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                texts.append(page_text)
        return "\n".join(texts)
    elif ext in (".txt",):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def _extract_emails(text: str):
    return re.findall(r"\b\S+@\S+\b", text)

def _extract_phones(text: str):
    return re.findall(r"\+?\d[\d\s\-]{7,}\d", text)

def _extract_skills(text: str, skills_db=None):
    if skills_db is None:
        skills_db = DEFAULT_SKILLS_DB
    text_lower = text.lower()
    matched = []
    for skill in skills_db:
        if skill.lower() in text_lower:
            matched.append(skill)
    return sorted(set(matched))

def parse_resume(file_path: str) -> Dict[str, Any]:
    raw_text = _extract_text_from_file(file_path)
    doc = nlp(raw_text)  

    emails = _extract_emails(raw_text)
    phones = _extract_phones(raw_text)
    skills = _extract_skills(raw_text)

    result: Dict[str, Any] = {
        "file_path": file_path,
        "emails": emails,
        "phones": phones,
        "skills": skills,
        "summary": {
            "num_chars": len(raw_text),
            "num_tokens": len(list(doc)),
        },
        "raw_text": raw_text,
    }
    return result