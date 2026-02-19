from __future__ import annotations


def parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    v = value.strip()
    if v == "":
        return None
    try:
        return int(v)
    except ValueError:
        return None


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    v = value.strip()
    if v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None

