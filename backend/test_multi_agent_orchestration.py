from app.ai.agents.orchestrator import orchestrate_request


def print_result(title: str, result) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    print("Request Type:", result.request_type)
    print(
        "Classification Confidence:",
        result.classification_confidence,
    )
    print(
        "Classification Reasoning:",
        result.classification_reasoning,
    )
    print("Action:", result.action)
    print("Tool:", result.tool_name)
    print("Requires Approval:", result.requires_approval)

    print("\nDOCUMENT RESULT:")
    print(result.document_result)

    print("\nPOLICY RESULT:")
    print(result.policy_result)

    print("\nRESEARCH RESULT:")
    print(result.research_result)

    print("\nTOOL RESULT:")
    print(result.tool_result)

    print("\nVALIDATION:")
    print(result.validation)

    print("\nEXECUTION TRACE:")
    for step in result.execution_trace:
        print("-", step)


def main() -> None:
    # Test 1: High Value Invoice
    invoice_result = orchestrate_request(
        title="Process High Value Invoice",
        content=(
            "Invoice Number: INV-1001\n"
            "Vendor: ABC Technologies Pvt Ltd\n"
            "Invoice Date: 08-09-2026\n"
            "Total: INR 500000\n"
            "Please validate and process the invoice."
        ),
    )

    print_result(
        "TEST 1: HIGH VALUE INVOICE APPROVAL FLOW",
        invoice_result,
    )

    # Test 2: Knowledge / RAG
    knowledge_result = orchestrate_request(
        title="Invoice Approval Policy",
        content=(
            "What is the policy for high value "
            "invoice approval?"
        ),
    )

    print_result(
        "TEST 2: KNOWLEDGE RAG MULTI-AGENT FLOW",
        knowledge_result,
    )

    # Test 3: Unknown Request
    unknown_result = orchestrate_request(
        title="Something Unusual",
        content="Please handle this request.",
    )

    print_result(
        "TEST 3: HUMAN REVIEW FLOW",
        unknown_result,
    )


if __name__ == "__main__":
    main()