# rag/embedder.py
"""
Embedding & ChromaDB persistence for VLSIHub.

Run this script once (or whenever you add new PDFs) to rebuild the
vector store:

    cd rag
    python embedder.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running directly from the rag/ subdirectory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from rag.data_ingestion import load_and_chunk_documents
from utils.config import (
    KNOWLEDGE_BASE_DIR,
    CHROMA_DB_DIR,
    EMBEDDING_MODEL,
    EMBEDDING_DEVICE,
)
from utils.logger import get_logger

logger = get_logger(__name__)


def create_vector_store(
    chunks,
    persist_directory: str | Path = CHROMA_DB_DIR,
) -> Chroma:
    """
    Generate embeddings for *chunks* and persist them to ChromaDB.

    Args:
        chunks:            List of LangChain Document objects.
        persist_directory: Where to write the ChromaDB files.

    Returns:
        The persisted Chroma vector store instance.

    Raises:
        ValueError: If *chunks* is empty.
    """
    if not chunks:
        raise ValueError(
            "No document chunks provided. "
            "Make sure load_and_chunk_documents() returns data."
        )

    persist_directory = Path(persist_directory)
    persist_directory.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Creating embeddings for %d chunk(s) using '%s' …",
        len(chunks),
        EMBEDDING_MODEL,
    )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": EMBEDDING_DEVICE},
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(persist_directory),
    )

    vector_store.persist()

    logger.info(
        "Vector store created and persisted at '%s'.",
        persist_directory,
    )
    return vector_store


if __name__ == "__main__":
    logger.info("=== VLSIHub Embedder — starting knowledge base ingestion ===")
    logger.info("Knowledge base directory: '%s'", KNOWLEDGE_BASE_DIR)

    chunks = load_and_chunk_documents(KNOWLEDGE_BASE_DIR)

    if not chunks:
        logger.error("No chunks to embed. Aborting.")
        sys.exit(1)

    logger.info("Total chunks to embed: %d", len(chunks))
    create_vector_store(chunks)
    logger.info("=== Embedding complete ===")