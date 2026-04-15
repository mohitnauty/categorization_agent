import re
from collections.abc import Mapping


REDACTED = "[REDACTED]"

SAFE_KEYS = {
    "chart_of_accounts",
}

SENSITIVE_KEYWORDS = (
    "aadhaar",
    "account",
    "address",
    "api_key",
    "apikey",
    "bank",
    "card",
    "contact",
    "cvv",
    "email",
    "gstin",
    "ifsc",
    "mobile",
    "pan",
    "password",
    "phone",
    "secret",
    "ssn",
    "tax_id",
    "token",
)

SENSITIVE_PATTERNS = (
    re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),  # Indian PAN
    re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),  # Aadhaar-like numbers
    re.compile(r"\b(?:\d[ -]*?){13,19}\b"),  # payment cards
    re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b"),  # IFSC
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"(?:(?<=\D)|^)(?:\+?91[\s-]?)?[6-9]\d{9}(?=\D|$)"),
)


def is_sensitive_key(key) -> bool:
    normalized = str(key).lower().replace("-", "_").replace(" ", "_")
    if normalized in SAFE_KEYS:
        return False
    return any(keyword in normalized for keyword in SENSITIVE_KEYWORDS)


def redact_text(value: str) -> str:
    redacted = value
    for pattern in SENSITIVE_PATTERNS:
        redacted = pattern.sub(REDACTED, redacted)
    return redacted


def sanitize_for_llm(value):
    if isinstance(value, Mapping):
        return {
            key: sanitize_for_llm(item)
            for key, item in value.items()
            if not is_sensitive_key(key)
        }

    if isinstance(value, list):
        return [sanitize_for_llm(item) for item in value]

    if isinstance(value, tuple):
        return tuple(sanitize_for_llm(item) for item in value)

    if isinstance(value, str):
        return redact_text(value)

    return value
