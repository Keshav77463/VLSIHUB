# tests/test_data_ingestion.py
"""
Unit tests for rag/data_ingestion.py.
Uses a temporary directory with synthetic text files to avoid requiring
real PDF fixtures.

Run with:  pytest tests/test_data_ingestion.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document

from rag.data_ingestion import _infer_topic, load_and_chunk_documents


# ── Topic inference ───────────────────────────────────────────────────────────
@pytest.mark.parametrize("filename,expected_topic", [
    ("mano_digital_design.pdf",     "digital_logic"),
    ("digital_circuits.pdf",        "digital_logic"),
    ("verilog_hdl.pdf",             "verilog"),
    ("systemverilog_spear.pdf",     "system_verilog"),
    ("some_random_book.pdf",        "general"),
    ("introduction_to_vlsi.pdf",    "general"),
])
def test_infer_topic(filename, expected_topic):
    assert _infer_topic(filename) == expected_topic, (
        f"Expected topic '{expected_topic}' for file '{filename}'"
    )


# ── load_and_chunk_documents with mocked loader ───────────────────────────────
def _make_doc(content: str, source: str = "mano_digital.pdf") -> Document:
    return Document(page_content=content, metadata={"source": source})


def test_deduplication():
    """Duplicate chunk content must be dropped."""
    fake_docs = [
        _make_doc("The D flip-flop stores a single bit of data."),
        _make_doc("The D flip-flop stores a single bit of data."),   # duplicate
        _make_doc("A latch is a level-triggered storage element."),
    ]

    with patch("rag.data_ingestion.PyPDFDirectoryLoader") as MockLoader, \
         patch("rag.data_ingestion.RecursiveCharacterTextSplitter") as MockSplitter:

        MockLoader.return_value.load.return_value = fake_docs
        MockSplitter.return_value.split_documents.return_value = fake_docs

        result = load_and_chunk_documents("/fake/path")

    assert len(result) == 2, "Duplicate chunk should have been removed"


def test_empty_folder_returns_empty_list():
    """If no PDFs exist, an empty list should be returned gracefully."""
    with patch("rag.data_ingestion.PyPDFDirectoryLoader") as MockLoader:
        MockLoader.return_value.load.return_value = []
        result = load_and_chunk_documents("/fake/empty")

    assert result == []


def test_metadata_enrichment():
    """Each chunk must have 'source' and 'topic' in its metadata."""
    fake_doc = _make_doc("Clock domain crossing requires synchronisers.", "verilog_hdl.pdf")

    with patch("rag.data_ingestion.PyPDFDirectoryLoader") as MockLoader, \
         patch("rag.data_ingestion.RecursiveCharacterTextSplitter") as MockSplitter:

        MockLoader.return_value.load.return_value = [fake_doc]
        MockSplitter.return_value.split_documents.return_value = [fake_doc]

        result = load_and_chunk_documents("/fake/path")

    assert len(result) == 1
    assert "source" in result[0].metadata
    assert "topic" in result[0].metadata
    assert result[0].metadata["topic"] == "verilog"
