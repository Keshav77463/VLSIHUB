# rag/answer_generator.py
"""
Answer Generator Agent for VLSIHub.

Generates domain-specific answers using Groq's LLaMA-3.3-70B model.
Different prompt templates are used based on the query intent routed
by agents/router.py.

Changes from v1:
- Uses centralised config (LLM_MODEL, GROQ_API_KEY, GENERATOR_TEMPERATURE, CONTEXT_CHAR_LIMIT)
- Structured logging
- Extracted _build_prompt() for cleaner, testable prompt construction
- No-docs guard returns a helpful message instead of a bare string
"""

from __future__ import annotations

from groq import Groq

from utils.config import (
    GROQ_API_KEY,
    LLM_MODEL,
    GENERATOR_TEMPERATURE,
    CONTEXT_CHAR_LIMIT,
)
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Shared scope restriction appended to every prompt ─────────────────────────
_SCOPE_GUARD = (
    "If the topic is outside VLSI/RTL/Digital Logic scope "
    "(e.g. semiconductor manufacturing, physics, sputtering), "
    'reply EXACTLY: "I cannot find relevant information about this topic in the provided documents."'
)

_TRUTH_TABLE_RULES = """
Truth Table Rules (VERY IMPORTANT):
- Use ONLY 0 and 1 wherever possible.
- Use Q(prev) ONLY when the circuit has memory and it is unavoidable.
- DO NOT expand unnecessary combinations or repeat rows.
- For combinational circuits  → use a full 0/1 truth table.
- For sequential circuits     → show only meaningful cases; prefer 0/1 outputs;
                                 use Q(prev) ONLY for the hold condition.
- Clearly mark INVALID states (if any).
- Avoid symbolic clutter (unnecessary X values).
- Keep tables clean and minimal.
- Include Boolean equations if useful.
"""


def _build_prompt(query: str, context: str, intent: str) -> str:
    """
    Build the appropriate prompt string for the given *intent*.

    Args:
        query:   User question.
        context: Concatenated document chunk text.
        intent:  One of "concept" | "code" | "problem" | other.

    Returns:
        The full prompt string to send to the LLM.
    """
    if intent == "concept":
        return f"""
You are a VLSI Design Verification expert. Answer in a concise, interview-ready format.

Structure your answer as:
1. Definition
2. How it works
3. Key points
4. Truth table (if applicable)
5. Example (if helpful)

Question:
{query}

Context:
{context}

Strict Instructions:
- Be precise and minimal.
- Use the Context primarily. If the Context does not contain the answer, you may
  answer from general VLSI/Digital Logic knowledge ONLY.
- {_SCOPE_GUARD}
{_TRUTH_TABLE_RULES}
"""

    if intent == "code":
        return f"""
You are a Verilog/SystemVerilog expert.

Write clean, synthesisable, and correct RTL code for the given problem.

Question:
{query}

Context:
{context}

Instructions:
- Use the Context primarily. Fall back to general knowledge ONLY for RTL topics.
- {_SCOPE_GUARD}
- Output ONLY the code (plus brief inline comments where helpful).
- Use proper syntax; keep it minimal and correct.
- Prefer: output register named q; derive q_bar with a continuous assign.
"""

    if intent == "problem":
        return f"""
You are a VLSI engineer solving timing and logic problems.

Solve step-by-step, showing all intermediate values.

Question:
{query}

Context:
{context}

Instructions:
- Use the Context primarily. Fall back to general knowledge ONLY for STA/Digital Logic.
- {_SCOPE_GUARD}
- Show each step clearly.
- Use formulas with variable names before substituting numbers.
- State your final answer prominently.
"""

    # ── Fallback / unknown intent ─────────────────────────────────────────────
    return f"""
Answer the question as a VLSI expert.

Question:
{query}

Context:
{context}

Use the context if helpful. Supplement with general VLSI/RTL knowledge only.
{_SCOPE_GUARD}
"""


def generate_answer(query: str, docs: list, intent: str = "concept") -> str:
    """
    Generate an LLM answer for *query* given retrieved *docs*.

    Args:
        query:  User question.
        docs:   Retrieved LangChain Document objects.
        intent: Query intent (from router agent).

    Returns:
        The generated answer string.
    """
    if not docs:
        logger.warning("No documents provided to generator — returning fallback message.")
        return (
            "No relevant VLSI documentation was found in the knowledge base for this query. "
            "Please ensure your PDFs are ingested, or rephrase your question."
        )

    context = "\n\n".join([doc.page_content[:CONTEXT_CHAR_LIMIT] for doc in docs])
    prompt = _build_prompt(query, context, intent)

    logger.info(
        "Generating answer — intent='%s'  docs=%d  query='%s'",
        intent, len(docs), query[:60],
    )

    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=GENERATOR_TEMPERATURE,
    )

    answer = response.choices[0].message.content
    logger.info("Answer generated (%d chars).", len(answer))
    return answer