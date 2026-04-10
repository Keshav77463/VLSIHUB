# rag/data_ingestion.py
"""
PDF document ingestion for VLSIHub knowledge base.

Pipeline:
  1. Load all PDFs from the knowledge_base directory
  2. Split into overlapping chunks (RecursiveCharacterTextSplitter)
  3. Deduplicate identical chunk content
  4. Tag each chunk with a domain topic (digital_logic / verilog / system_verilog / general)
  5. Return clean, enriched Document objects ready for embedding
"""

from __future__ import annotations

from pathlib import Path

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from utils.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHUNK_SEPARATORS,
    TOPIC_RULES,
    DEFAULT_TOPIC,
)
from utils.logger import get_logger

logger = get_logger(__name__)


def _infer_topic(file_name: str) -> str:
    """Return the domain topic tag for a given (lowercase) filename."""
    for topic, keywords in TOPIC_RULES.items():
        if any(kw in file_name for kw in keywords):
            return topic
    return DEFAULT_TOPIC


def load_and_chunk_documents(folder_path: str | Path) -> list[Document]:
    """
    Load PDFs from *folder_path*, split them into chunks, deduplicate, and
    enrich each chunk with source/topic metadata.

    Args:
        folder_path: Path to the directory containing PDF files.

    Returns:
        List of unique, metadata-enriched Document objects.
    """
    folder_path = Path(folder_path)
    logger.info("Loading PDFs from '%s' …", folder_path)

    loader = PyPDFDirectoryLoader(str(folder_path))
    documents = loader.load()
    logger.info("Loaded %d raw document page(s).", len(documents))

    if not documents:
        logger.warning(
            "No PDF files found in '%s'. "
            "Place your VLSI textbooks there before running the embedder.",
            folder_path,
        )
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=CHUNK_SEPARATORS,
    )

    chunks: list[Document] = splitter.split_documents(documents)
    logger.info("Split into %d chunk(s) before deduplication.", len(chunks))

    # ── Deduplication + metadata enrichment ──────────────────────────────────
    seen: set[str] = set()
    unique_chunks: list[Document] = []

    for chunk in chunks:
        content = chunk.page_content.strip()
        if not content or content in seen:
            continue

        seen.add(content)

        source_path: str = chunk.metadata.get("source", "unknown")
        file_name: str = Path(source_path).name.lower()
        topic: str = _infer_topic(file_name)

        chunk.metadata.update(
            {
                "source": file_name,
                "topic": topic,
            }
        )
        unique_chunks.append(chunk)

    logger.info(
        "Ingestion complete — %d unique chunk(s) ready for embedding.",
        len(unique_chunks),
    )
    return unique_chunks