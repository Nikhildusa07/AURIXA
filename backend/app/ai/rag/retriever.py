from __future__ import annotations

from app.ai.rag.filter import filter_results
from app.ai.rag.vector_store import vector_store


def retrieve_knowledge(
    query: str,
    n_results: int = 5,
    max_distance: float = 1.0,
) -> list[dict]:
    result = vector_store.search(
        query=query,
        n_results=n_results,
    )

    ids = result.get("ids", [[]])[0]
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    raw_results = []

    for chunk_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        metadata = metadata or {}

        confidence = max(
            0.0,
            min(1.0, 1.0 - float(distance)),
        )

        raw_results.append(
            {
                "chunk_id": chunk_id,
                "document_id": metadata.get(
                    "document_id",
                    "unknown",
                ),
                "source": metadata.get(
                    "source",
                    "unknown",
                ),
                "chunk_index": metadata.get(
                    "chunk_index",
                    None,
                ),
                "text": document,
                "distance": float(distance),
                "confidence": round(confidence, 4),
                "metadata": metadata,
            }
        )

    return filter_results(
        raw_results,
        max_distance=max_distance,
    )