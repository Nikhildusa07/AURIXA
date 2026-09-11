from __future__ import annotations

import re


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be >= 0 and smaller than chunk_size"
        )

    cleaned_text = _clean_text(text)

    if not cleaned_text:
        return []

    chunks: list[str] = []

    start = 0
    text_length = len(cleaned_text)

    while start < text_length:
        end = min(
            start + chunk_size,
            text_length,
        )

        if end < text_length:
            end = _find_best_break(
                cleaned_text,
                start,
                end,
            )

        chunk = cleaned_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        next_start = end - overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def _clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def _find_best_break(
    text: str,
    start: int,
    end: int,
) -> int:
    minimum_break_position = start + (
        (end - start) // 2
    )

    break_characters = [
        "\n\n",
        ". ",
        "! ",
        "? ",
        "\n",
        " ",
    ]

    for separator in break_characters:
        position = text.rfind(
            separator,
            minimum_break_position,
            end,
        )

        if position != -1:
            return position + len(separator)

    return end