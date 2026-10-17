from __future__ import annotations

import json
from typing import Any, Protocol

import tiktoken

from .config import TOKEN_ENCODING


class Counter(Protocol):
    def count_text(self, text: str) -> int: ...


class TokenCounter:
    def __init__(self, encoding_name: str = TOKEN_ENCODING) -> None:
        self._encoding = tiktoken.get_encoding(encoding_name)

    def count_text(self, text: str) -> int:
        return len(self._encoding.encode_ordinary(text))


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
