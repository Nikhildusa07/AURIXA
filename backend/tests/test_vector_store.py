from unittest.mock import MagicMock, patch

import pytest


@patch("app.ai.rag.vector_store.chromadb.PersistentClient")
def test_vector_store_initialization(mock_client_class):
    mock_client = MagicMock()
    mock_collection = MagicMock()

    mock_client_class.return_value = mock_client
    mock_client.get_or_create_collection.return_value = (
        mock_collection
    )

    from app.ai.rag.vector_store import VectorStore

    store = VectorStore()

    mock_client_class.assert_called()
    mock_client.get_or_create_collection.assert_called_once_with(
        name="aurixa_knowledge",
        metadata={
            "description": "AURIXA enterprise knowledge base"
        },
    )

    assert store.client == mock_client
    assert store.collection == mock_collection


@patch("app.ai.rag.vector_store.chromadb.PersistentClient")
def test_add_chunks_success(mock_client_class):
    mock_client = MagicMock()
    mock_collection = MagicMock()

    mock_client_class.return_value = mock_client
    mock_client.get_or_create_collection.return_value = (
        mock_collection
    )

    from app.ai.rag.vector_store import VectorStore

    store = VectorStore()

    chunk_ids = ["chunk-1", "chunk-2"]
    texts = ["First text", "Second text"]
    metadatas = [
        {"document_id": "doc-1"},
        {"document_id": "doc-2"},
    ]

    store.add_chunks(
        chunk_ids=chunk_ids,
        texts=texts,
        metadatas=metadatas,
    )

    mock_collection.upsert.assert_called_once_with(
        ids=chunk_ids,
        documents=texts,
        metadatas=metadatas,
    )


@patch("app.ai.rag.vector_store.chromadb.PersistentClient")
def test_add_chunks_empty_ids_does_nothing(mock_client_class):
    mock_client = MagicMock()
    mock_collection = MagicMock()

    mock_client_class.return_value = mock_client
    mock_client.get_or_create_collection.return_value = (
        mock_collection
    )

    from app.ai.rag.vector_store import VectorStore

    store = VectorStore()

    store.add_chunks(
        chunk_ids=[],
        texts=[],
        metadatas=[],
    )

    mock_collection.upsert.assert_not_called()


@patch("app.ai.rag.vector_store.chromadb.PersistentClient")
def test_add_chunks_length_mismatch_raises_error(
    mock_client_class,
):
    mock_client = MagicMock()
    mock_collection = MagicMock()

    mock_client_class.return_value = mock_client
    mock_client.get_or_create_collection.return_value = (
        mock_collection
    )

    from app.ai.rag.vector_store import VectorStore

    store = VectorStore()

    with pytest.raises(
        ValueError,
        match=(
            "chunk_ids, texts, and metadatas "
            "must have the same length"
        ),
    ):
        store.add_chunks(
            chunk_ids=["chunk-1"],
            texts=["text-1", "text-2"],
            metadatas=[{"document_id": "doc-1"}],
        )


@patch("app.ai.rag.vector_store.chromadb.PersistentClient")
def test_search_success(mock_client_class):
    mock_client = MagicMock()
    mock_collection = MagicMock()

    mock_client_class.return_value = mock_client
    mock_client.get_or_create_collection.return_value = (
        mock_collection
    )

    expected_result = {
        "ids": [["chunk-1"]],
        "documents": [["Test content"]],
    }

    mock_collection.query.return_value = expected_result

    from app.ai.rag.vector_store import VectorStore

    store = VectorStore()

    result = store.search(
        query="test query",
        n_results=10,
    )

    mock_collection.query.assert_called_once_with(
        query_texts=["test query"],
        n_results=10,
    )

    assert result == expected_result


@patch("app.ai.rag.vector_store.chromadb.PersistentClient")
@pytest.mark.parametrize(
    "query",
    [
        "",
        "   ",
        "\n",
        "\t",
    ],
)
def test_search_empty_query_raises_error(
    mock_client_class,
    query,
):
    mock_client = MagicMock()
    mock_collection = MagicMock()

    mock_client_class.return_value = mock_client
    mock_client.get_or_create_collection.return_value = (
        mock_collection
    )

    from app.ai.rag.vector_store import VectorStore

    store = VectorStore()

    with pytest.raises(
        ValueError,
        match="query cannot be empty",
    ):
        store.search(query)


@patch("app.ai.rag.vector_store.chromadb.PersistentClient")
def test_search_default_n_results(mock_client_class):
    mock_client = MagicMock()
    mock_collection = MagicMock()

    mock_client_class.return_value = mock_client
    mock_client.get_or_create_collection.return_value = (
        mock_collection
    )

    mock_collection.query.return_value = {}

    from app.ai.rag.vector_store import VectorStore

    store = VectorStore()

    store.search("test query")

    mock_collection.query.assert_called_once_with(
        query_texts=["test query"],
        n_results=5,
    )


@patch("app.ai.rag.vector_store.chromadb.PersistentClient")
def test_count(mock_client_class):
    mock_client = MagicMock()
    mock_collection = MagicMock()

    mock_client_class.return_value = mock_client
    mock_client.get_or_create_collection.return_value = (
        mock_collection
    )

    mock_collection.count.return_value = 25

    from app.ai.rag.vector_store import VectorStore

    store = VectorStore()

    result = store.count()

    assert result == 25
    mock_collection.count.assert_called_once()
    