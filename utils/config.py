# utils/config.py
"""
Centralised configuration for VLSIHub.
All tuneable constants live here — avoid magic numbers scattered across files.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR: Path = BASE_DIR / "data" / "knowledge_base"
CHROMA_DB_DIR: Path = BASE_DIR / "rag" / "data" / "chroma_db"
LOGS_DIR: Path = BASE_DIR / "logs"

# ── Embedding ────────────────────────────────────────────────────────────────
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
EMBEDDING_DEVICE: str = "cpu"

# ── Chunking ─────────────────────────────────────────────────────────────────
CHUNK_SIZE: int = 400
CHUNK_OVERLAP: int = 120
CHUNK_SEPARATORS: list[str] = ["\n\n", "\n", ".", " ", ""]

# ── Retrieval ────────────────────────────────────────────────────────────────
RETRIEVAL_TOP_K: int = 4
CONTEXT_CHAR_LIMIT: int = 400       # chars per doc snippet fed to LLM

# ── LLM ──────────────────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
LLM_MODEL: str = "llama-3.3-70b-versatile"
GENERATOR_TEMPERATURE: float = 0.2
VERIFIER_TEMPERATURE: float = 0.1

# ── Domain guard (topics explicitly blocked from answering) ──────────────────
BLOCKED_KEYWORDS: list[str] = [
    "sputtering", "semiconductor manufacturing", "cvd", "pvd",
    "photolithography", "etching", "doping", "implantation",
]

# ── Domain-tagging rules for data ingestion ─────────────────────────────────
TOPIC_RULES: dict[str, list[str]] = {
    "digital_logic":   ["mano", "digital"],
    "verilog":         ["verilog"],
    "system_verilog":  ["systemverilog", "spear"],
}
DEFAULT_TOPIC: str = "general"
