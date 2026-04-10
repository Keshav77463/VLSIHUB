# tests/test_router.py
"""
Unit tests for agents/router.py — weighted intent classification.
Run with:  pytest tests/test_router.py -v
"""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from agents.router import route_query


# ── Code intent ───────────────────────────────────────────────────────────────
@pytest.mark.parametrize("query", [
    "Write a synchronous FIFO in Verilog",
    "Implement a 4-bit counter module in SystemVerilog",
    "Write RTL code for a D flip-flop with async reset",
    "Create a testbench for a priority encoder",
])
def test_code_intent(query):
    assert route_query(query) == "code", f"Expected 'code' for: {query}"


# ── Problem intent ────────────────────────────────────────────────────────────
@pytest.mark.parametrize("query", [
    "Calculate the slack for a 10ns path with 2ns clock skew",
    "Find the critical path delay in this circuit",
    "Solve the setup time violation for 200MHz operation",
    "What is the required hold time for this latch?",
])
def test_problem_intent(query):
    assert route_query(query) == "problem", f"Expected 'problem' for: {query}"


# ── Concept intent ────────────────────────────────────────────────────────────
@pytest.mark.parametrize("query", [
    "Explain clock domain crossing",
    "What is a phase-locked loop?",
    "Describe the difference between latch and flip-flop",
    "What are the advantages of pipeline architecture?",
])
def test_concept_intent(query):
    assert route_query(query) == "concept", f"Expected 'concept' for: {query}"


# ── Edge cases ────────────────────────────────────────────────────────────────
def test_empty_query_defaults_to_concept():
    assert route_query("") == "concept"


def test_case_insensitive():
    assert route_query("WRITE A VERILOG MODULE") == "code"
