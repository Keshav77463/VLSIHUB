# tests/conftest.py
"""
Shared pytest fixtures for VLSIHub test suite.
"""

import sys
from pathlib import Path

import pytest
from langchain_core.documents import Document

# Ensure project root is always on sys.path when running tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ── Reusable Document fixtures ────────────────────────────────────────────────

@pytest.fixture
def sample_doc_digital():
    """A mock Document tagged as digital logic content."""
    return Document(
        page_content="The D flip-flop captures the value of the D input at the clock edge.",
        metadata={"source": "mano_digital.pdf", "topic": "digital_logic"},
    )


@pytest.fixture
def sample_doc_verilog():
    """A mock Document tagged as Verilog content."""
    return Document(
        page_content="module dff (input clk, input d, output reg q); always @(posedge clk) q <= d; endmodule",
        metadata={"source": "verilog_hdl.pdf", "topic": "verilog"},
    )


@pytest.fixture
def sample_docs(sample_doc_digital, sample_doc_verilog):
    """A list of two sample documents for pipeline testing."""
    return [sample_doc_digital, sample_doc_verilog]
