from __future__ import annotations


PROMPT_TEST_CASES = [
    {
        "name": "classifier_general_request",
        "prompt": "classifier",
        "input": {
            "title": "General Request",
            "content": "Please provide information about the system.",
        },
        "expected": "general",
    },
    {
        "name": "classifier_invoice_request",
        "prompt": "classifier",
        "input": {
            "title": "Invoice Processing",
            "content": (
                "Invoice number INV-001 "
                "with total amount 5000."
            ),
        },
        "expected": "invoice_processing",
    },
    {
        "name": "research_knowledge_query",
        "prompt": "research",
        "input": {
            "query": "What is AURIXA?",
            "context": (
                "AURIXA is an Autonomous Enterprise "
                "AI Platform."
            ),
        },
        "expected": "grounded_answer",
    },
    {
        "name": "document_invoice_extraction",
        "prompt": "document",
        "input": {
            "document_type": "invoice",
            "content": (
                "Invoice INV-001. Total amount: 5000."
            ),
        },
        "expected": "structured_extraction",
    },
    {
        "name": "validation_low_confidence",
        "prompt": "validation",
        "input": {
            "result": {
                "action": "automate",
            },
            "confidence": 0.40,
        },
        "expected": "human_review",
    },
]


def get_prompt_test_cases(
    prompt_name: str | None = None,
) -> list[dict]:
    if prompt_name is None:
        return PROMPT_TEST_CASES

    return [
        test_case
        for test_case in PROMPT_TEST_CASES
        if test_case["prompt"] == prompt_name
    ]