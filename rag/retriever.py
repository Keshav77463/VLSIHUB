# rag/retriever.py
"""
Semantic document retriever using ChromaDB + HuggingFace embeddings.

Improvements over v1:
- Uses centralised config (CHROMA_DB_DIR, EMBEDDING_MODEL, RETRIEVAL_TOP_K)
- Structured logging instead of print()
- Score-threshold filtering (discards low-relevance chunks)
- Vector store is loaded lazily and cached for the session lifetime
"""

from __future__ import annotations

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from utils.config import (
    CHROMA_DB_DIR,
    EMBEDDING_MODEL,
    EMBEDDING_DEVICE,
    RETRIEVAL_TOP_K,
)
from utils.logger import get_logger

logger = get_logger(__name__)

# Cosine-distance threshold: lower = more similar.
# Chunks with distance > this value are dropped as noise.
SCORE_THRESHOLD: float = 1.2


@lru_cache(maxsize=1)
def _load_embeddings() -> HuggingFaceEmbeddings:
    """Load the embedding model once and cache it for the process lifetime."""
    logger.info("Loading embedding model '%s' on %s …", EMBEDDING_MODEL, EMBEDDING_DEVICE)
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": EMBEDDING_DEVICE},
    )


@lru_cache(maxsize=1)
def load_vector_store() -> Chroma:
    """Load (and cache) the ChromaDB vector store."""
    logger.info("Loading vector store from '%s' …", CHROMA_DB_DIR)

    vector_store = Chroma(
        persist_directory=str(CHROMA_DB_DIR),
        embedding_function=_load_embeddings(),
    )

    try:
        count = vector_store._collection.count()
        logger.info("Vector store loaded — %d document chunks available.", count)
    except Exception:
        logger.warning("Could not read collection count from vector store.")

    return vector_store


def retrieve_documents(query: str, k: int = RETRIEVAL_TOP_K) -> list:
    """
    Retrieve the top-k most relevant document chunks for *query*.

    Chunks with a cosine distance above SCORE_THRESHOLD are filtered out
    so the LLM never receives irrelevant context.

    Args:
        query: The user's question.
        k:     Maximum number of chunks to return (default from config).

    Returns:
        A list of LangChain Document objects (may be empty).
    """
    logger.info("Retrieving top-%d chunks for query: '%s'", k, query[:80])

    vector_store = load_vector_store()
    results = vector_store.similarity_search_with_score(query, k=k)

    docs = []
    for doc, score in results:
        logger.debug("  chunk score=%.4f  source=%s", score, doc.metadata.get("source", "?"))
        if score <= SCORE_THRESHOLD:
            docs.append(doc)
        else:
            logger.debug("  → dropped (score above threshold %.2f)", SCORE_THRESHOLD)

    if not docs:
        logger.warning("No relevant documents found for query: '%s'", query[:80])
    else:
        logger.info("Retrieved %d relevant chunk(s).", len(docs))

    return docs


# ── Quick sanity-check ────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_query = "setup time"
    retrieved = retrieve_documents(test_query)
    print(f"\n--- Retrieved {len(retrieved)} chunk(s) ---\n")
    for i, doc in enumerate(retrieved, 1):
        print(f"[Chunk {i}]")
        print(doc.page_content[:300])
        print("-" * 50)