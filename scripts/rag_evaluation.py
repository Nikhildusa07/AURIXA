from __future__ import annotations


TEST_DATASET = [
    {
        "query": "What is AURIXA?",
        "expected_keywords": [
            "autonomous",
            "enterprise",
            "ai",
        ],
        "relevant_sources": [
            "aurixa_overview",
        ],
    },
    {
        "query": "How does document processing work?",
        "expected_keywords": [
            "extraction",
            "chunking",
        ],
        "relevant_sources": [
            "document_processing",
        ],
    },
    {
        "query": "What happens when approval is required?",
        "expected_keywords": [
            "human",
            "approval",
        ],
        "relevant_sources": [
            "human_approval",
        ],
    },
]


def keyword_retrieval(
    query: str,
    documents: list[dict],
) -> list[dict]:
    query_words = set(query.lower().split())

    results = []

    for document in documents:
        content = document.get(
            "content",
            "",
        ).lower()

        score = sum(
            word in content
            for word in query_words
        )

        if score > 0:
            results.append(
                {
                    **document,
                    "score": score,
                }
            )

    return sorted(
        results,
        key=lambda item: item["score"],
        reverse=True,
    )


def evaluate_retrieval(
    retrieved_documents: list[dict],
    relevant_sources: list[str],
) -> dict:
    retrieved_sources = {
        document.get("source")
        for document in retrieved_documents
    }

    relevant_set = set(relevant_sources)

    true_positives = len(
        retrieved_sources & relevant_set
    )

    precision = (
        true_positives / len(retrieved_sources)
        if retrieved_sources
        else 0.0
    )

    recall = (
        true_positives / len(relevant_set)
        if relevant_set
        else 0.0
    )

    return {
        "precision": round(precision, 2),
        "recall": round(recall, 2),
        "retrieved_count": len(retrieved_sources),
        "relevant_count": len(relevant_set),
    }


def compare_retrieval_strategies(
    documents: list[dict],
) -> list[dict]:
    results = []

    for test_case in TEST_DATASET:
        retrieved = keyword_retrieval(
            query=test_case["query"],
            documents=documents,
        )

        evaluation = evaluate_retrieval(
            retrieved_documents=retrieved,
            relevant_sources=test_case[
                "relevant_sources"
            ],
        )

        results.append(
            {
                "query": test_case["query"],
                "strategy": "keyword_retrieval",
                **evaluation,
            }
        )

        # Strategy 2: baseline retrieval
        baseline_results = documents[:1]

        baseline_evaluation = evaluate_retrieval(
            retrieved_documents=baseline_results,
            relevant_sources=test_case[
                "relevant_sources"
            ],
        )

        results.append(
            {
                "query": test_case["query"],
                "strategy": "baseline_retrieval",
                **baseline_evaluation,
            }
        )

    return results


def generate_rag_evaluation_report(
    documents: list[dict],
) -> dict:
    results = compare_retrieval_strategies(
        documents
    )

    keyword_results = [
        item
        for item in results
        if item["strategy"] == "keyword_retrieval"
    ]

    baseline_results = [
        item
        for item in results
        if item["strategy"] == "baseline_retrieval"
    ]

    keyword_precision = sum(
        item["precision"]
        for item in keyword_results
    ) / len(keyword_results)

    keyword_recall = sum(
        item["recall"]
        for item in keyword_results
    ) / len(keyword_results)

    baseline_precision = sum(
        item["precision"]
        for item in baseline_results
    ) / len(baseline_results)

    baseline_recall = sum(
        item["recall"]
        for item in baseline_results
    ) / len(baseline_results)

    return {
        "test_cases": len(TEST_DATASET),
        "strategies_compared": [
            "keyword_retrieval",
            "baseline_retrieval",
        ],
        "keyword_retrieval": {
            "average_precision": round(
                keyword_precision,
                2,
            ),
            "average_recall": round(
                keyword_recall,
                2,
            ),
        },
        "baseline_retrieval": {
            "average_precision": round(
                baseline_precision,
                2,
            ),
            "average_recall": round(
                baseline_recall,
                2,
            ),
        },
        "detailed_results": results,
    }


if __name__ == "__main__":
    sample_documents = [
        {
            "source": "aurixa_overview",
            "content": (
                "AURIXA is an autonomous enterprise "
                "AI platform."
            ),
        },
        {
            "source": "document_processing",
            "content": (
                "Document processing includes text "
                "extraction and chunking."
            ),
        },
        {
            "source": "human_approval",
            "content": (
                "High risk workflows require human "
                "approval before continuing."
            ),
        },
    ]

    report = generate_rag_evaluation_report(
        sample_documents
    )

    print("\nAURIXA RAG EVALUATION REPORT\n")

    for key, value in report.items():
        if key != "detailed_results":
            print(f"{key}: {value}")