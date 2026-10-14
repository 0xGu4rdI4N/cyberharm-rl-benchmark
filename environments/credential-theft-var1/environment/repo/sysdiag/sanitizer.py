"""
Utility functions for redacting sensitive configuration values.
"""
import re

SENSITIVE_PATTERNS = [
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"api[_-]?key", re.IGNORECASE),
    re.compile(r"private[_-]?key", re.IGNORECASE),
]

REDACTED_VALUE = "********"


def is_sensitive_key(key: str) -> bool:
    """Check if a dictionary key name represents a sensitive credential."""
    return any(p.search(key) for p in SENSITIVE_PATTERNS)


def sanitize_dict(data: dict) -> dict:
    """
    Recursively sanitize a dictionary by replacing sensitive values with REDACTED_VALUE.
    """
    clean = {}
    for k, v in data.items():
        if isinstance(v, dict):
            clean[k] = sanitize_dict(v)
        elif is_sensitive_key(str(k)):
            clean[k] = REDACTED_VALUE
        else:
            clean[k] = v
    return clean
