from unittest.mock import patch

from app.documents.indexing import index_chunks


@patch("app.documents.indexing.vector_store.add_chunks")
def test_index_valid_chunks(mock_add_chunks):
    chunks = [
        "First chunk",
        "Second chunk",
    ]

    result = index_chunks(
        chunks=chunks,
        document_id="doc-123",
        source="sample.pdf",
    )

    assert result == 2
    assert mock_add_chunks.called


@patch("app.documents.indexing.vector_store.add_chunks")
def test_empty_chunks_returns_zero(mock_add_chunks):
    result = index_chunks(
        chunks=[],
        document_id="doc-123",
        source="sample.pdf",
    )

    assert result == 0
    mock_add_chunks.assert_not_called()


@patch("app.documents.indexing.vector_store.add_chunks")
def test_whitespace_chunks_are_ignored(mock_add_chunks):
    result = index_chunks(
        chunks=["Valid chunk", "   ", "\n"],
        document_id="doc-123",
        source="sample.txt",
    )

    assert result == 1


@patch("app.documents.indexing.vector_store.add_chunks")
def test_chunk_metadata_is_created_correctly(mock_add_chunks):
    index_chunks(
        chunks=["Hello world"],
        document_id="doc-123",
        source="sample.txt",
        metadata={"category": "test"},
    )

    kwargs = mock_add_chunks.call_args.kwargs

    assert kwargs["metadatas"][0]["document_id"] == "doc-123"
    assert kwargs["metadatas"][0]["source"] == "sample.txt"
    assert kwargs["metadatas"][0]["category"] == "test"


@patch("app.documents.indexing.vector_store.add_chunks")
def test_chunk_ids_are_generated_correctly(mock_add_chunks):
    index_chunks(
        chunks=["One", "Two"],
        document_id="doc-123",
        source="sample.txt",
    )

    kwargs = mock_add_chunks.call_args.kwargs

    assert kwargs["chunk_ids"] == [
        "doc-123-chunk-1",
        "doc-123-chunk-2",
    ]