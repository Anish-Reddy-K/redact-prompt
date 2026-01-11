"""
redact-prompt: Redact PII from prompts before sending to LLMs.

Simple usage:
    from redact_prompt import redact, unredact
    
    result = redact("Email john@acme.com")
    send_to_llm(result.text)  # redacted + instruction included
    
    restored = unredact(llm_response)  # original values restored

result.text includes instruction to preserve placeholders.
result.redacted is just the redacted text without instruction.
"""

__version__ = "0.1.0"
__all__ = ["redact", "unredact", "clear", "Redactor", "RedactionResult", "Entity"]

import re
from dataclasses import dataclass, field
from typing import List, Optional, Set

import spacy
from spacy.cli import download as spacy_download


def _load_spacy_model(model: str):
    """Load spaCy model, downloading if needed."""
    try:
        return spacy.load(model)
    except OSError:
        # model not found, download it
        print(f"Downloading spaCy model '{model}'... (one-time setup)")
        spacy_download(model)
        return spacy.load(model)


# regex patterns for structured pii
PATTERNS = [
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", re.I)),
    ("PHONE", re.compile(r"(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)")),
    ("SSN", re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b")),
    ("CREDIT_CARD", re.compile(r"\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2}|6(?:011|5\d{2}))[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4,7}\b")),
    ("IP", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b")),
    # api keys
    ("API_KEY", re.compile(r"\bsk-[a-zA-Z0-9\-_]{16,}\b")),  # openai
    ("API_KEY", re.compile(r"\bsk-ant-[a-zA-Z0-9\-_]{16,}\b")),  # anthropic
    ("API_KEY", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),  # aws
    ("API_KEY", re.compile(r"\bgh[pousr]_[a-zA-Z0-9]{36,}\b")),  # github
    ("API_KEY", re.compile(r"\b[sr]k_(?:live|test)_[a-zA-Z0-9]{20,}\b")),  # stripe
    ("API_KEY", re.compile(r"\bxox[bpar]-[a-zA-Z0-9\-]+\b")),  # slack
    ("API_KEY", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),  # google
]

# spacy entity mapping
NER_MAP = {"PERSON": "PERSON", "ORG": "ORG", "GPE": "LOCATION", "LOC": "LOCATION"}

# common words/acronyms to ignore from ner (false positives)
NER_BLOCKLIST = {
    "SSN", "API", "IP", "URL", "HTTP", "HTTPS", "SQL", "HTML", "CSS", "JSON",
    "XML", "PDF", "CSV", "ID", "PIN", "OTP", "SMS", "MFA", "2FA", "VPN", "DNS",
    "AWS", "GCP", "CEO", "CTO", "CFO", "COO", "HR", "IT", "QA", "UI", "UX",
    "EMAIL", "PHONE", "NAME", "ADDRESS", "KEY", "TOKEN", "PASSWORD", "SECRET",
}

# instruction to preserve placeholders in llm responses
PLACEHOLDER_INSTRUCTION = (
    "IMPORTANT: This text contains placeholders like [PERSON_1], [EMAIL_1], etc. "
    "You must preserve these placeholders exactly as written in your response. "
    "Do not modify, explain, or expand them."
)


@dataclass
class Entity:
    """Detected PII entity."""
    type: str
    value: str
    placeholder: str
    start: int
    end: int


@dataclass
class RedactionResult:
    """Result of redaction."""
    original: str
    redacted: str  # raw redacted text
    entities: List[Entity] = field(default_factory=list)
    
    @property
    def text(self) -> str:
        """Redacted text with instruction (ready to send to LLM)."""
        if not self.entities:
            return self.redacted
        return f"{self.redacted}\n\n{PLACEHOLDER_INSTRUCTION}"


class Redactor:
    """Redact PII from text before sending to LLMs."""
    
    def __init__(self, model: str = "en_core_web_sm", use_ner: bool = True):
        self._store: dict[str, str] = {}  # placeholder -> value
        self._reverse: dict[str, str] = {}  # value -> placeholder
        self._counters: dict[str, int] = {}
        self._nlp = _load_spacy_model(model) if use_ner else None
    
    def _placeholder(self, entity_type: str, value: str) -> str:
        """Get or create placeholder for a value."""
        if value in self._reverse:
            return self._reverse[value]
        
        self._counters[entity_type] = self._counters.get(entity_type, 0) + 1
        n = self._counters[entity_type]
        
        # partial mask for api keys (show prefix/suffix for debugging)
        if entity_type == "API_KEY" and len(value) > 12:
            p = f"[{entity_type}_{n}:{value[:6]}***{value[-4:]}]"
        else:
            p = f"[{entity_type}_{n}]"
        
        self._store[p] = value
        self._reverse[value] = p
        return p
    
    def redact(self, text: str) -> RedactionResult:
        """Redact PII from text."""
        if not text:
            return RedactionResult(original=text, redacted=text)
        
        detections = []
        
        # regex detection
        for entity_type, pattern in PATTERNS:
            for m in pattern.finditer(text):
                detections.append((entity_type, m.group(), m.start(), m.end()))
        
        # ner detection (with blocklist filtering)
        if self._nlp:
            for ent in self._nlp(text).ents:
                if ent.label_ in NER_MAP:
                    # skip blocklisted words and very short entities
                    if ent.text.upper() in NER_BLOCKLIST or len(ent.text) < 3:
                        continue
                    detections.append((NER_MAP[ent.label_], ent.text, ent.start_char, ent.end_char))
        
        # remove overlaps (keep longer matches)
        detections.sort(key=lambda x: (x[2], -(x[3] - x[2])))
        filtered, last_end = [], -1
        for d in detections:
            if d[2] >= last_end:
                filtered.append(d)
                last_end = d[3]
        
        # replace (reverse order to preserve positions)
        result, entities = text, []
        for entity_type, value, start, end in sorted(filtered, key=lambda x: -x[2]):
            p = self._placeholder(entity_type, value)
            result = result[:start] + p + result[end:]
            entities.append(Entity(entity_type, value, p, start, end))
        
        return RedactionResult(original=text, redacted=result, entities=list(reversed(entities)))
    
    def wrap_prompt(self, redacted_text: str) -> str:
        """Wrap redacted text with instruction to preserve placeholders."""
        return f"{redacted_text}\n\n{PLACEHOLDER_INSTRUCTION}"
    
    def unredact(self, text: str) -> str:
        """Restore original values in text."""
        result = text
        for p in sorted(self._store.keys(), key=len, reverse=True):
            result = result.replace(p, self._store[p])
        return result
    
    def clear(self) -> None:
        """Clear all stored mappings."""
        self._store.clear()
        self._reverse.clear()
        self._counters.clear()


# === convenience api (module-level) ===
# for simple use cases without managing a redactor instance

_default_redactor: Optional[Redactor] = None


def _get_redactor(use_ner: bool = True) -> Redactor:
    """Get or create the default redactor instance."""
    global _default_redactor
    if _default_redactor is None:
        _default_redactor = Redactor(use_ner=use_ner)
    return _default_redactor


def redact(text: str, *, use_ner: bool = True) -> RedactionResult:
    """
    Redact PII from text.
    
    Returns RedactionResult where:
        result.text     - Redacted text + instruction (send to LLM)
        result.redacted - Just the redacted text (for debugging)
        result.entities - List of detected entities
    """
    return _get_redactor(use_ner).redact(text)


def unredact(text: str) -> str:
    """Restore original PII values in text."""
    if _default_redactor is None:
        return text
    return _default_redactor.unredact(text)


def clear() -> None:
    """Clear all stored mappings from the default redactor."""
    global _default_redactor
    if _default_redactor is not None:
        _default_redactor.clear()
