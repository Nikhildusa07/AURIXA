from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
    status,
)

from app.ai.rag.pipeline import retrieve_context
from app.documents.extraction import SUPPORTED_EXTENSIONS
from app.documents.ingestion import ingest_document


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


UPLOAD_DIRECTORY = Path("uploads/documents")

MAX_FILE_SIZE = 20 * 1024 * 1024


@router.post(
    "/ingest",
    status_code=status.HTTP_201_CREATED,
)
async def ingest_uploaded_document(
    file: UploadFile = File(...),
) -> dict:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    filename = Path(file.filename).name
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported file type. "
                "Supported types: PDF, DOCX, TXT."
            ),
        )

    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    document_id = str(uuid4())

    stored_filename = (
        f"{document_id}{extension}"
    )

    file_path = (
        UPLOAD_DIRECTORY / stored_filename
    )

    try:
        file_size = 0

        with file_path.open("wb") as buffer:
            while True:
                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                file_size += len(chunk)

                if file_size > MAX_FILE_SIZE:
                    buffer.close()

                    if file_path.exists():
                        file_path.unlink()

                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "File size exceeds the "
                            "20 MB limit."
                        ),
                    )

                buffer.write(chunk)

        result = ingest_document(
            file_path=file_path,
            document_id=document_id,
            metadata={
                "original_filename": filename,
                "content_type": file.content_type,
            },
        )

        if result["status"] == "failed":
            raise HTTPException(
                status_code=400,
                detail=result["error"],
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document ingestion failed: {exc}"
            ),
        )

    finally:
        await file.close()


@router.get("/search")
async def search_documents(
    query: str,
    limit: int = 5,
) -> dict:
    if not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty.",
        )

    if limit < 1 or limit > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Limit must be between 1 and 20."
            ),
        )

    return retrieve_context(
        query=query,
        n_results=limit,
    )