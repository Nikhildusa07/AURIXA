from __future__ import annotations

from typing import Any

from app.ai.rag.vector_store import vector_store


def index_chunks(
    chunks: list[str],
    document_id: str,
    source: str,
    metadata: dict[str, Any] | None = None,
) -> int:
    valid_chunks = [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]

    if not valid_chunks:
        return 0

    base_metadata = metadata or {}

    chunk_ids = [
        f"{document_id}-chunk-{index + 1}"
        for index in range(len(valid_chunks))
    ]

    metadatas = []

    for index, chunk in enumerate(
        valid_chunks,
        start=1,
    ):
        chunk_metadata = {
            **base_metadata,
            "document_id": document_id,
            "source": source,
            "chunk_index": index,
            "chunk_count": len(valid_chunks),
            "chunk_characters": len(chunk),
        }

        metadatas.append(chunk_metadata)

    vector_store.add_chunks(
        chunk_ids=chunk_ids,
        texts=valid_chunks,
        metadatas=metadatas,
    )

    return len(valid_chunks)