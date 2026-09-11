import pytest

from app.documents.chunking import chunk_text


def test_empty_text_returns_empty_list():
    assert chunk_text("") == []
    assert chunk_text("   \n\t  ") == []


def test_short_text_returns_single_chunk():
    text = "This is a short document."

    result = chunk_text(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert result == [text]


def test_large_text_is_split_into_chunks():
    text = "This is a sentence. " * 100

    result = chunk_text(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert len(result) > 1
    assert all(chunk.strip() for chunk in result)


def test_invalid_chunk_size_raises_error():
    with pytest.raises(
        ValueError,
        match="chunk_size must be greater than 0",
    ):
        chunk_text("Hello world", chunk_size=0)


def test_invalid_overlap_raises_error():
    with pytest.raises(
        ValueError,
        match="overlap must be >= 0",
    ):
        chunk_text(
            "Hello world",
            chunk_size=100,
            overlap=100,
        )