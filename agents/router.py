# agents/router.py
"""
Query Router — classifies user intent into one of:
  - "code"    : RTL/Verilog code generation request
  - "problem" : timing / logic problem solving
  - "concept" : conceptual / theory explanation

Uses a weighted keyword-scoring approach so that queries with multiple
signals are assigned the *most likely* intent rather than the first match.
"""

from utils.logger import get_logger

logger = get_logger(__name__)

# ── Keyword banks with relative weights ──────────────────────────────────────
CODE_KEYWORDS: dict[str, int] = {
    "verilog": 3,
    "systemverilog": 3,
    "code": 2,
    "module": 2,
    "always": 2,
    "write": 1,
    "implement": 2,
    "rtl": 3,
    "testbench": 3,
    "tb": 2,
    "generate": 1,
    "synthesize": 2,
    "instantiate": 2,
    "port": 1,
}

PROBLEM_KEYWORDS: dict[str, int] = {
    "calculate": 3,
    "find": 2,
    "solve": 3,
    "timing": 2,
    "setup": 2,
    "hold": 2,
    "delay": 2,
    "slack": 3,
    "propagation": 2,
    "critical path": 3,
    "frequency": 2,
    "clock period": 3,
    "tpd": 3,
    "tcq": 3,
}

CONCEPT_KEYWORDS: dict[str, int] = {
    "explain": 2,
    "what is": 2,
    "define": 2,
    "describe": 2,
    "difference": 2,
    "how does": 2,
    "why": 1,
    "when": 1,
    "compare": 2,
    "advantage": 1,
    "disadvantage": 1,
}


def _score(query_lower: str, keyword_map: dict[str, int]) -> int:
    """Return the cumulative weight of matched keywords."""
    return sum(weight for kw, weight in keyword_map.items() if kw in query_lower)


def route_query(query: str) -> str:
    """
    Classify query intent.

    Returns one of: "code" | "problem" | "concept"
    """
    q = query.lower()

    code_score = _score(q, CODE_KEYWORDS)
    problem_score = _score(q, PROBLEM_KEYWORDS)
    concept_score = _score(q, CONCEPT_KEYWORDS)

    logger.debug(
        "Router scores — code: %d | problem: %d | concept: %d",
        code_score, problem_score, concept_score,
    )

    best_score = max(code_score, problem_score, concept_score)

    if best_score == 0:
        intent = "concept"           # Default fallback
    elif code_score == best_score:
        intent = "code"
    elif problem_score == best_score:
        intent = "problem"
    else:
        intent = "concept"

    logger.info("Query routed → intent='%s'  query='%s'", intent, query[:60])
    return intent