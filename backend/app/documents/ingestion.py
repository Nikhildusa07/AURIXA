from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.documents.chunking import chunk_text
from app.documents.extraction import (
    SUPPORTED_EXTENSIONS,
    extract_text,
)
from app.documents.indexing import index_chunks


def ingest_document(
    file_path: str | Path,
    document_id: str,
    metadata: dict[str, Any] | None = None,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> dict[str, Any]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Document path is invalid: {path}"
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    ingestion_started_at = datetime.now(
        timezone.utc
    )

    try:
        text = extract_text(path)

        if not text.strip():
            raise ValueError(
                "Document contains no extractable text."
            )

        chunks = chunk_text(
            text=text,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        if not chunks:
            raise ValueError(
                "No chunks were generated from the document."
            )

        document_metadata = {
            **(metadata or {}),
            "filename": path.name,
            "file_extension": extension,
            "file_size_bytes": path.stat().st_size,
            "ingested_at": ingestion_started_at.isoformat(),
        }

        indexed_count = index_chunks(
            chunks=chunks,
            document_id=document_id,
            source=path.name,
            metadata=document_metadata,
        )

        return {
            "document_id": document_id,
            "filename": path.name,
            "file_extension": extension,
            "file_size_bytes": path.stat().st_size,
            "characters": len(text),
            "chunks": len(chunks),
            "indexed_chunks": indexed_count,
            "metadata": document_metadata,
            "status": "indexed",
            "ingested_at": ingestion_started_at.isoformat(),
        }

    except Exception as exc:
        return {
            "document_id": document_id,
            "filename": path.name,
            "status": "failed",
            "error": str(exc),
            "ingested_at": ingestion_started_at.isoformat(),
        }