from app.ai.rag.pipeline import retrieve_context


def main():
    query = "high value invoice approval"

    result = retrieve_context(
        query=query,
        n_results=5,
    )

    print("\nQUERY:")
    print(result["query"])

    print("\nHAS EVIDENCE:")
    print(result["has_evidence"])

    print("\nANSWER ALLOWED:")
    print(result["answer_allowed"])

    print("\nSOURCES:")
    for source in result["sources"]:
        print(source)

    print("\nCONTEXT:")
    print(result["context"])

    print("\nMESSAGE:")
    print(result["message"])


if __name__ == "__main__":
    main()