from __future__ import annotations


def build_context(results: list[dict]) -> str:
    if not results:
        return ""

    sections: list[str] = []

    for index, result in enumerate(results, start=1):
        source = result.get("source", "unknown")
        document_id = result.get(
            "document_id",
            "unknown",
        )
        chunk_index = result.get("chunk_index")
        confidence = result.get("confidence", 0.0)
        text = result.get("text", "").strip()

        if not text:
            continue

        citation = (
            f"[Source {index} | "
            f"Document: {document_id} | "
            f"File: {source}"
        )

        if chunk_index is not None:
            citation += f" | Chunk: {chunk_index}"

        citation += (
            f" | Confidence: {confidence:.2%}]"
        )

        sections.append(
            f"{citation}\n{text}"
        )

    return "\n\n".join(sections)