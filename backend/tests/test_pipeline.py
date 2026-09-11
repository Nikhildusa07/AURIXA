from unittest.mock import patch

from app.ai.rag.pipeline import retrieve_context


@patch("app.ai.rag.pipeline.retrieve_knowledge")
def test_no_results(mock_retrieve_knowledge):
    mock_retrieve_knowledge.return_value = []

    result = retrieve_context("What is AI?")

    assert result["query"] == "What is AI?"
    assert result["results"] == []
    assert result["sources"] == []
    assert result["context"] == ""
    assert result["has_evidence"] is False
    assert result["answer_allowed"] is False
    assert result["message"] == (
        "No reliable evidence was found "
        "in the knowledge base."
    )


@patch("app.ai.rag.pipeline.build_context")
@patch("app.ai.rag.pipeline.retrieve_knowledge")
def test_results_with_evidence(
    mock_retrieve_knowledge,
    mock_build_context,
):
    results = [
        {
            "source": "document.pdf",
            "document_id": "doc-1",
            "chunk_id": "chunk-1",
            "chunk_index": 0,
            "confidence": 0.9,
            "text": "Artificial intelligence information.",
        }
    ]

    mock_retrieve_knowledge.return_value = results
    mock_build_context.return_value = (
        "[Source 1]\nArtificial intelligence information."
    )

    result = retrieve_context("What is AI?")

    assert result["query"] == "What is AI?"
    assert result["results"] == results
    assert result["has_evidence"] is True
    assert result["answer_allowed"] is True
    assert result["message"] == (
        "Reliable knowledge-base evidence found."
    )

    assert result["context"] == (
        "[Source 1]\nArtificial intelligence information."
    )


@patch("app.ai.rag.pipeline.build_context")
@patch("app.ai.rag.pipeline.retrieve_knowledge")
def test_sources_are_extracted_correctly(
    mock_retrieve_knowledge,
    mock_build_context,
):
    results = [
        {
            "source": "file1.pdf",
            "document_id": "doc-1",
            "chunk_id": "chunk-1",
            "chunk_index": 0,
            "confidence": 0.95,
        },
        {
            "source": "file2.pdf",
            "document_id": "doc-2",
            "chunk_id": "chunk-2",
            "chunk_index": 3,
            "confidence": 0.8,
        },
    ]

    mock_retrieve_knowledge.return_value = results
    mock_build_context.return_value = "Combined context"

    result = retrieve_context("test query")

    assert result["sources"] == [
        {
            "source": "file1.pdf",
            "document_id": "doc-1",
            "chunk_id": "chunk-1",
            "chunk_index": 0,
            "confidence": 0.95,
        },
        {
            "source": "file2.pdf",
            "document_id": "doc-2",
            "chunk_id": "chunk-2",
            "chunk_index": 3,
            "confidence": 0.8,
        },
    ]


@patch("app.ai.rag.pipeline.retrieve_knowledge")
def test_passes_default_parameters(mock_retrieve_knowledge):
    mock_retrieve_knowledge.return_value = []

    retrieve_context("test query")

    mock_retrieve_knowledge.assert_called_once_with(
        query="test query",
        n_results=5,
        max_distance=1.0,
    )


@patch("app.ai.rag.pipeline.retrieve_knowledge")
def test_passes_custom_parameters(mock_retrieve_knowledge):
    mock_retrieve_knowledge.return_value = []

    retrieve_context(
        query="custom query",
        n_results=10,
        max_distance=0.5,
    )

    mock_retrieve_knowledge.assert_called_once_with(
        query="custom query",
        n_results=10,
        max_distance=0.5,
    )


@patch("app.ai.rag.pipeline.build_context")
@patch("app.ai.rag.pipeline.retrieve_knowledge")
def test_build_context_receives_results(
    mock_retrieve_knowledge,
    mock_build_context,
):
    results = [
        {
            "source": "test.pdf",
            "document_id": "doc-1",
            "chunk_id": "chunk-1",
            "chunk_index": 1,
            "confidence": 0.9,
        }
    ]

    mock_retrieve_knowledge.return_value = results
    mock_build_context.return_value = "Test context"

    retrieve_context("test query")

    mock_build_context.assert_called_once_with(results)