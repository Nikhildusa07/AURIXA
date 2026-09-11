from __future__ import annotations

from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def extract_text(file_path: str | Path) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(
            sorted(SUPPORTED_EXTENSIONS)
        )

        raise ValueError(
            f"Unsupported document type: {extension}. "
            f"Supported types: {supported}"
        )

    if extension == ".pdf":
        text = _extract_pdf(path)

    elif extension == ".docx":
        text = _extract_docx(path)

    else:
        text = _extract_txt(path)

    return text.strip()


def _extract_pdf(path: Path) -> str:
    try:
        reader = PdfReader(str(path))
        pages: list[str] = []

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):
            text = page.extract_text() or ""

            if text.strip():
                pages.append(
                    f"[Page {page_number}]\n{text.strip()}"
                )

        return "\n\n".join(pages)

    except Exception as exc:
        raise ValueError(
            f"Failed to extract PDF text: {exc}"
        ) from exc


def _extract_docx(path: Path) -> str:
    try:
        document = DocxDocument(str(path))

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n\n".join(paragraphs)

    except Exception as exc:
        raise ValueError(
            f"Failed to extract DOCX text: {exc}"
        ) from exc


def _extract_txt(path: Path) -> str:
    try:
        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    except Exception as exc:
        raise ValueError(
            f"Failed to extract TXT text: {exc}"
        ) from exc