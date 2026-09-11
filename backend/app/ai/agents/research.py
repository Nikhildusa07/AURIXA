from __future__ import annotations

from dataclasses import dataclass

from app.ai.rag.pipeline import retrieve_context


@dataclass
class ResearchResult:
    query: str
    context: str
    sources: list[str]
    confidence: float
    answer_allowed: bool


def research_knowledge(
    query: str,
    n_results: int = 5,
) -> ResearchResult:
    rag_result = retrieve_context(
        query=query,
        n_results=n_results,
    )

    sources = [
        result["source"]
        for result in rag_result["results"]
        if result.get("source")
    ]

    if not rag_result["answer_allowed"]:
        return ResearchResult(
            query=query,
            context="",
            sources=[],
            confidence=0.0,
            answer_allowed=False,
        )

    distances = [
        result["distance"]
        for result in rag_result["results"]
    ]

    best_distance = min(distances) if distances else 1.0
    confidence = max(0.0, min(1.0, 1.0 - best_distance))

    return ResearchResult(
        query=query,
        context=rag_result["context"],
        sources=sources,
        confidence=confidence,
        answer_allowed=True,
    )