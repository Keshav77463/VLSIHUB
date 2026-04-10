# rag/main.py
"""
VLSIHub CLI — run the full RAG pipeline from the command line.

Usage:
    python rag/main.py
    python rag/main.py --query "Explain setup time violations"

The script runs the same pipeline as the Streamlit UI:
  Router → Retriever → Generator → Verifier
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure imports resolve from the project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.router import route_query
from agents.verifier import verify_answer
from rag.retriever import retrieve_documents
from rag.answer_generator import generate_answer
from utils.logger import get_logger

logger = get_logger(__name__)


def run_pipeline(query: str) -> str:
    """
    Execute the full multi-agent RAG pipeline for *query*.

    Args:
        query: The user's VLSI question.

    Returns:
        The verified final answer string.
    """
    logger.info("=== Pipeline started ===")

    # Step 1: Route
    intent = route_query(query)
    logger.info("Intent: %s", intent)

    # Step 2: Retrieve
    docs = retrieve_documents(query)
    logger.info("Documents retrieved: %d", len(docs))

    # Step 3: Generate
    answer = generate_answer(query, docs, intent)
    logger.info("Raw answer length: %d chars", len(answer))

    # Step 4: Verify
    final_answer = verify_answer(query, docs, answer)
    logger.info("=== Pipeline complete ===")

    return final_answer


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="vlsihub",
        description="VLSIHub CLI — ask VLSI questions from the terminal.",
    )
    parser.add_argument(
        "--query", "-q",
        type=str,
        default=None,
        help="Question to ask (if omitted, prompts interactively).",
    )
    args = parser.parse_args()

    query = args.query or input("Enter your VLSI question: ").strip()

    if not query:
        print("Error: query cannot be empty.")
        sys.exit(1)

    print(f"\n🔧 Query   : {query}")
    print("⚙️  Running pipeline …\n")

    answer = run_pipeline(query)

    print("\n" + "=" * 60)
    print("✅ FINAL ANSWER")
    print("=" * 60)
    print(answer)
    print("=" * 60)


if __name__ == "__main__":
    main()