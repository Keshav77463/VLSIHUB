# agents/verifier.py
"""
Answer Verification Agent for VLSIHub.

Reviews the generated answer against the retrieved context and the original
question, then returns a corrected, interview-ready response.

Changes from v1:
- Uses centralised config (LLM_MODEL, GROQ_API_KEY, VERIFIER_TEMPERATURE)
- Structured logging
- Early-exit guard for the "no-information" sentinel phrase
- Max context tokens trimmed per CONTEXT_CHAR_LIMIT from config
"""

from __future__ import annotations

from groq import Groq

from utils.config import (
    GROQ_API_KEY,
    LLM_MODEL,
    VERIFIER_TEMPERATURE,
    CONTEXT_CHAR_LIMIT,
)
from utils.logger import get_logger

logger = get_logger(__name__)

# Sentinel phrase emitted by the generator when no relevant info is found.
NO_INFO_SENTINEL = "I cannot find relevant information about this topic in the provided documents."


def verify_answer(query: str, docs: list, answer: str) -> str:
    """
    Verify and (if needed) correct *answer* using retrieved *docs*.

    Args:
        query:  Original user question.
        docs:   Retrieved LangChain Document objects.
        answer: Raw answer from the generator agent.

    Returns:
        The verified / corrected answer string.
    """
    # ── Early exits ───────────────────────────────────────────────────────────
    if not docs:
        logger.info("Verifier skipped — no documents retrieved.")
        return answer

    if NO_INFO_SENTINEL in answer:
        logger.info("Verifier skipped — generator returned sentinel phrase.")
        return NO_INFO_SENTINEL

    # ── Build trimmed context ─────────────────────────────────────────────────
    context = "\n\n".join([doc.page_content[:CONTEXT_CHAR_LIMIT] for doc in docs])

    prompt = f"""
You are a strict VLSI Design Verification expert.

Your job is to VERIFY and CORRECT the answer if needed.

Question:
{query}

Context:
{context}

Answer:
{answer}

Strict Instructions:

- If the Answer is already "{NO_INFO_SENTINEL}", output that EXACT phrase and STOP.
- Always ensure the answer is technically correct and interview-ready.
- DO NOT allow suboptimal RTL or incorrect explanations.
- If ANY issue exists → FIX it completely (do not leave partially correct answers).

Correction Rules:
- Fix incorrect logic, missing details, or bad design practices.
- Improve clarity and correctness even if the answer is mostly correct.

Truth Table Rules (VERY IMPORTANT):
- Use ONLY 0 and 1 wherever possible.
- Use Q(prev) ONLY when memory behaviour cannot be avoided.
- DO NOT expand unnecessary combinations or repeat rows.
- For sequential circuits → show only meaningful transitions.
- Clearly mark INVALID states if applicable.

RTL Code Rules:
- Avoid redundant registers.
- Prefer:
  • q as the register output
  • q_bar derived using assign (not a separate reg)
- Ensure synthesisable, clean, minimal code.

Output Rules:
- Output ONLY the final corrected answer.
- NO meta-comments such as "Here is the corrected answer".
- NO explanations about what was changed.
- Keep it concise and professional.
"""

    logger.info("Running verifier for query: '%s'", query[:60])

    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=VERIFIER_TEMPERATURE,
    )

    verified = response.choices[0].message.content
    logger.info("Verification complete.")
    return verified