from app.documents.ingestion import ingest_document


def main():
    result = ingest_document(
        file_path="sample_knowledge.txt",
        document_id="invoice-policy-001",
    )

    print("\nINGESTION RESULT:")
    print(result)


if __name__ == "__main__":
    main()