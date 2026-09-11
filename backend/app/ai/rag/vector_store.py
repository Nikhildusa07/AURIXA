from __future__ import annotations

from pathlib import Path

import chromadb

VECTOR_DB_PATH = Path("data/vector_db")


class VectorStore:
    def __init__(self) -> None:
        VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB_PATH)
        )

        self.collection = self.client.get_or_create_collection(
            name="aurixa_knowledge",
            metadata={"description": "AURIXA enterprise knowledge base"},
        )

    def add_chunks(
        self,
        chunk_ids: list[str],
        texts: list[str],
        metadatas: list[dict],
    ) -> None:
        if not chunk_ids:
            return

        if not (len(chunk_ids) == len(texts) == len(metadatas)):
            raise ValueError(
                "chunk_ids, texts, and metadatas must have the same length"
            )

        self.collection.upsert(
            ids=chunk_ids,
            documents=texts,
            metadatas=metadatas,
        )

    def search(
        self,
        query: str,
        n_results: int = 5,
    ) -> dict:
        if not query.strip():
            raise ValueError("query cannot be empty")

        return self.collection.query(
            query_texts=[query],
            n_results=n_results,
        )

    def count(self) -> int:
        return self.collection.count()


vector_store = VectorStore()