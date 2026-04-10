# CHANGELOG.md

# Changelog

All notable changes to VLSIHub are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- `utils/logger.py` — centralised structured logging (file + console handlers)
- `utils/config.py` — all tuneable constants in one place (paths, model names, temps, chunk sizes)
- `utils/__init__.py`, `agents/__init__.py`, `rag/__init__.py` — proper Python package inits
- `tests/test_router.py` — parametrised unit tests for query intent routing
- `tests/test_data_ingestion.py` — unit tests for chunking, deduplication, topic tagging
- `CONTRIBUTING.md` — developer guide for contributing to VLSIHub
- `CHANGELOG.md` — this file

### Changed
- `agents/router.py` — replaced simple first-match keyword logic with weighted scoring across all three intents
- `agents/verifier.py` — uses config constants; adds early-exit guard for sentinel phrase before calling LLM
- `rag/answer_generator.py` — extracted `_build_prompt()`; shared scope-guard and truth-table rules strings; improved no-docs fallback
- `rag/retriever.py` — LRU-cached embedding model and vector store; score-threshold filtering; structured logging
- `rag/data_ingestion.py` — extracted `_infer_topic()`; uses config constants; guards against empty folder
- `rag/embedder.py` — uses config paths; explicit `mkdir(parents=True)` for persist directory
- `README.md` — full project documentation with architecture diagram, setup guide, and feature table

### Fixed
- Retriever no longer returns low-relevance chunks (score > 1.2) that caused off-topic answers
- Verifier no longer calls the LLM when the generator already returned the "no info" sentinel phrase
- Router no longer misclassifies mixed-intent queries (e.g. "calculate Verilog module delay")

---

## [0.1.0] — Initial Release

### Added
- Multi-agent RAG pipeline: Router → Retriever → Generator → Verifier
- ChromaDB vector store with HuggingFace `all-MiniLM-L6-v2` embeddings
- Groq LLaMA-3.3-70B for answer generation and verification
- Streamlit dark-mode UI with circuit-board aesthetics
- Domain restriction: blocks out-of-scope topics (manufacturing, physics, sputtering)
- PDF ingestion with chunk deduplication and domain topic tagging
