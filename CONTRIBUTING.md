# CONTRIBUTING.md

# Contributing to VLSIHub

Thank you for considering a contribution! This guide explains how to set up
the development environment, coding standards, and the pull-request workflow.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Coding Standards](#coding-standards)
4. [Running Tests](#running-tests)
5. [Adding New Features](#adding-new-features)
6. [Pull Request Process](#pull-request-process)

---

## Getting Started

```bash
# 1. Fork & clone
git clone https://github.com/<your-fork>/VLSIHUB.git
cd VLSIHUB

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install uv
uv sync

# 4. Set up your environment file
cp .env.example .env
# Fill in GROQ_API_KEY=...

# 5. (Optional) Build the vector store
cd rag && python embedder.py && cd ..
```

---

## Project Structure

| Path | Purpose |
|------|---------|
| `app.py` | Streamlit UI entry point |
| `agents/router.py` | Weighted keyword-scoring intent classifier |
| `agents/verifier.py` | LLM-based answer verification agent |
| `rag/answer_generator.py` | Prompt construction + Groq LLM call |
| `rag/retriever.py` | ChromaDB semantic document retrieval |
| `rag/data_ingestion.py` | PDF loading, chunking, deduplication |
| `rag/embedder.py` | Embedding generation and persistence |
| `utils/config.py` | **All** tuneable constants (edit here, not in modules) |
| `utils/logger.py` | Shared structured logger |
| `tests/` | pytest unit tests |
| `data/knowledge_base/` | Place VLSI PDF textbooks here |

---

## Coding Standards

- **Python 3.11+** — use modern type hints (`list[str]`, `str | None`)
- **Imports** — use absolute imports from the project root
- **Logging** — always use `from utils.logger import get_logger`, never bare `print()`
- **Config** — all constants belong in `utils/config.py`; never hardcode paths or model names
- **Docstrings** — every public function needs a Google-style docstring
- **Type hints** — all function signatures must be annotated
- **Line length** — 100 characters maximum

---

## Running Tests

```bash
pytest tests/ -v
```

Individual test files:

```bash
pytest tests/test_router.py -v
pytest tests/test_data_ingestion.py -v
```

---

## Adding New Features

### Adding a New Intent Type

1. Add keywords to the appropriate bank in `agents/router.py`
2. Add a new `elif intent == "your_intent":` block in `rag/answer_generator.py → _build_prompt()`
3. Add tests in `tests/test_router.py`

### Adding Support for New Document Formats

1. Add a new loader in `rag/data_ingestion.py`
2. Update `TOPIC_RULES` in `utils/config.py` if a new domain is needed
3. Re-run `python rag/embedder.py` to rebuild the vector store

### Changing the LLM Model

Update `LLM_MODEL` in `utils/config.py`:

```python
LLM_MODEL: str = "llama-3.3-70b-versatile"   # ← change here only
```

---

## Pull Request Process

1. Create a feature branch: `git checkout -b feat/your-feature`
2. Make your changes with clear, atomic commits
3. Ensure all tests pass: `pytest tests/ -v`
4. Update `CHANGELOG.md` under `[Unreleased]`
5. Open a PR with a clear description of what changed and why
6. Request a review and address feedback

---

Thank you for helping improve VLSIHub! 🔧
