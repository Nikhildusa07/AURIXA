from unittest.mock import patch

from app.ai.rag.retriever import retrieve_knowledge


@patch("app.ai.rag.retriever.vector_store.search")
def test_empty_results(mock_search):
    mock_search.return_value = {
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]],
    }

    results = retrieve_knowledge("test query")

    assert results == []


@patch("app.ai.rag.retriever.vector_store.search")
def test_successful_retrieval(mock_search):
    mock_search.return_value = {
        "ids": [["chunk-1"]],
        "documents": [["This is test content"]],
        "metadatas": [[
            {
                "document_id": "doc-1",
                "source": "test.pdf",
                "chunk_index": 0,
            }
        ]],
        "distances": [[0.2]],
    }

    results = retrieve_knowledge("test query")

    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk-1"
    assert results[0]["document_id"] == "doc-1"
    assert results[0]["source"] == "test.pdf"
    assert results[0]["chunk_index"] == 0
    assert results[0]["text"] == "This is test content"
    assert results[0]["distance"] == 0.2
    assert results[0]["confidence"] == 0.8


@patch("app.ai.rag.retriever.vector_store.search")
def test_missing_metadata_uses_defaults(mock_search):
    mock_search.return_value = {
        "ids": [["chunk-1"]],
        "documents": [["Test content"]],
        "metadatas": [[{}]],
        "distances": [[0.3]],
    }

    results = retrieve_knowledge("test query")

    assert len(results) == 1
    assert results[0]["document_id"] == "unknown"
    assert results[0]["source"] == "unknown"
    assert results[0]["chunk_index"] is None


@patch("app.ai.rag.retriever.vector_store.search")
def test_none_metadata_uses_defaults(mock_search):
    mock_search.return_value = {
        "ids": [["chunk-1"]],
        "documents": [["Test content"]],
        "metadatas": [[None]],
        "distances": [[0.3]],
    }

    results = retrieve_knowledge("test query")

    assert len(results) == 1
    assert results[0]["metadata"] == {}


@patch("app.ai.rag.retriever.vector_store.search")
def test_confidence_calculation(mock_search):
    mock_search.return_value = {
        "ids": [["chunk-1"]],
        "documents": [["Test content"]],
        "metadatas": [[{}]],
        "distances": [[0.25]],
    }

    results = retrieve_knowledge("test query")

    assert results[0]["confidence"] == 0.75


@patch("app.ai.rag.retriever.vector_store.search")
def test_confidence_lower_boundary(mock_search):
    mock_search.return_value = {
        "ids": [["chunk-1"]],
        "documents": [["Test content"]],
        "metadatas": [[{}]],
        "distances": [[2.0]],
    }

    results = retrieve_knowledge(
        "test query",
        max_distance=2.0,
    )

    assert results[0]["confidence"] == 0.0


@patch("app.ai.rag.retriever.vector_store.search")
def test_confidence_upper_boundary(mock_search):
    mock_search.return_value = {
        "ids": [["chunk-1"]],
        "documents": [["Test content"]],
        "metadatas": [[{}]],
        "distances": [[-0.5]],
    }

    results = retrieve_knowledge(
        "test query",
        max_distance=1.0,
    )

    assert results[0]["confidence"] == 1.0


@patch("app.ai.rag.retriever.vector_store.search")
def test_respects_max_distance(mock_search):
    mock_search.return_value = {
        "ids": [["chunk-1", "chunk-2"]],
        "documents": [["Valid content", "Too far"]],
        "metadatas": [[{}, {}]],
        "distances": [[0.5, 1.5]],
    }

    results = retrieve_knowledge(
        "test query",
        max_distance=1.0,
    )

    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk-1"


@patch("app.ai.rag.retriever.vector_store.search")
def test_passes_query_and_n_results(mock_search):
    mock_search.return_value = {
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]],
    }

    retrieve_knowledge(
        "my query",
        n_results=10,
    )

    mock_search.assert_called_once_with(
        query="my query",
        n_results=10,
    )

@patch("app.ai.rag.retriever.vector_store.search")
def test_confidence_lower_boundary(mock_search):
    mock_search.return_value = {
        "ids": [["chunk-1"]],
        "documents": [["Test content"]],
        "metadatas": [[{}]],
        "distances": [[2.0]],
    }

    results = retrieve_knowledge(
        "test query",
        max_distance=2.0,
    )

    assert results == []