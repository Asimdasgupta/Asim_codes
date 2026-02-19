from __future__ import annotations

import json
import zlib


def to_json_text(obj: dict) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def compress_text(text: str) -> bytes:
    return zlib.compress(text.encode("utf-8"), level=6)


def decompress_text(blob: bytes) -> str:
    return zlib.decompress(blob).decode("utf-8")


def compress_json(obj: dict) -> tuple[str, bytes]:
    text = to_json_text(obj)
    return text, compress_text(text)


def decompress_json(blob: bytes) -> dict:
    return json.loads(decompress_text(blob))

