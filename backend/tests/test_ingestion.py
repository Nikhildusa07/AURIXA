from unittest.mock import patch

import pytest

from app.documents.ingestion import ingest_document


def test_successful_document_ingestion(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text(
        "This is a test document for AURIXA.",
        encoding="utf-8",
    )

    with (
        patch(
            "app.documents.ingestion.extract_text",
            return_value="This is a test document for AURIXA.",
        ),
        patch(
            "app.documents.ingestion.chunk_text",
            return_value=["This is a test document."],
        ),
        patch(
            "app.documents.ingestion.index_chunks",
            return_value=1,
        ),
    ):
        result = ingest_document(
            file_path=file_path,
            document_id="doc-123",
        )

    assert result["status"] == "indexed"
    assert result["document_id"] == "doc-123"
    assert result["indexed_chunks"] == 1


def test_document_not_found():
    with pytest.raises(FileNotFoundError):
        ingest_document(
            "missing_document.txt",
            "doc-123",
        )


def test_unsupported_file_type(tmp_path):
    file_path = tmp_path / "sample.csv"
    file_path.write_text("test", encoding="utf-8")

    with pytest.raises(ValueError):
        ingest_document(
            file_path,
            "doc-123",
        )


def test_empty_document_returns_failed_status(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("", encoding="utf-8")

    result = ingest_document(
        file_path=file_path,
        document_id="doc-123",
    )

    assert result["status"] == "failed"
    assert "no extractable text" in result["error"].lower()


def test_indexing_failure_returns_failed_status(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Test document", encoding="utf-8")

    with (
        patch(
            "app.documents.ingestion.extract_text",
            return_value="Test document",
        ),
        patch(
            "app.documents.ingestion.chunk_text",
            return_value=["Test document"],
        ),
        patch(
            "app.documents.ingestion.index_chunks",
            side_effect=Exception("Indexing failed"),
        ),
    ):
        result = ingest_document(
            file_path=file_path,
            document_id="doc-123",
        )

    assert result["status"] == "failed"
    assert "Indexing failed" in result["error"]