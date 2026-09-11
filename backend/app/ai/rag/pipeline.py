from __future__ import annotations

from app.ai.rag.context import build_context
from app.ai.rag.retriever import retrieve_knowledge


def retrieve_context(
    query: str,
    n_results: int = 5,
    max_distance: float = 1.0,
) -> dict:
    results = retrieve_knowledge(
        query=query,
        n_results=n_results,
        max_distance=max_distance,
    )

    if not results:
        return {
            "query": query,
            "results": [],
            "sources": [],
            "context": "",
            "has_evidence": False,
            "answer_allowed": False,
            "message": (
                "No reliable evidence was found "
                "in the knowledge base."
            ),
        }

    sources = [
        {
            "source": result["source"],
            "document_id": result["document_id"],
            "chunk_id": result["chunk_id"],
            "chunk_index": result["chunk_index"],
            "confidence": result["confidence"],
        }
        for result in results
    ]

    return {
        "query": query,
        "results": results,
        "sources": sources,
        "context": build_context(results),
        "has_evidence": True,
        "answer_allowed": True,
        "message": "Reliable knowledge-base evidence found.",
    }