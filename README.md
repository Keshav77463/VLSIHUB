# 🔧 VLSI AI Assistant (VLSIHub)

A domain-specific AI tutor for VLSI Design, Digital Logic, and RTL Development, powered by a **multi-agent RAG pipeline** with Groq LLaMA-3.3-70B and ChromaDB.

---

## 🚀 Features

- 📚 **RAG Pipeline** — Retrieve answers from your own VLSI documents (PDFs)
- 🤖 **Multi-Agent Architecture** — Router, Generator, and Verifier agents
- ✅ **Answer Verification** — A dedicated agent reviews and corrects responses
- 💡 **Intent Routing** — Separates concept, code, and problem-solving queries
- 🧠 **Domain-Restricted** — Won't hallucinate outside VLSI/RTL/Logic scope
- 🖥️ **Streamlit UI** — Clean dark-mode interface with circuit board aesthetics

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────┐     ┌──────────────┐     ┌──────────────────┐
│  Router │────▶│  Retriever   │────▶│ Answer Generator │
│  Agent  │     │ (ChromaDB)   │     │  (Groq LLaMA-3)  │
└─────────┘     └──────────────┘     └──────────────────┘
                                              │
                                              ▼
                                    ┌──────────────────┐
                                    │ Verifier Agent   │
                                    │ (Groq LLaMA-3)   │
                                    └──────────────────┘
                                              │
                                              ▼
                                       Final Answer
```

---

## 📁 Project Structure

```
VLSIFI/
├── app.py                  # Streamlit UI entry point
├── agents/
│   ├── router.py           # Query intent classification
│   └── verifier.py         # Answer verification & correction
├── rag/
│   ├── answer_generator.py # LLM answer generation with Groq
│   ├── data_ingestion.py   # PDF loading, chunking, deduplication
│   ├── embedder.py         # Embedding & ChromaDB persistence
│   ├── retriever.py        # Semantic document retrieval
│   └── main.py             # RAG pipeline entry point
├── data/
│   ├── knowledge_base/     # Place your VLSI PDF books here
│   └── chroma_db/          # Auto-generated vector store
├── pyproject.toml
└── .env                    # GROQ_API_KEY goes here
```

---

## ⚙️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Keshav77463/VLSIHUB.git
cd VLSIHUB
```

### 2. Install Dependencies

```bash
pip install uv
uv sync
```

### 3. Configure Environment

Create a `.env` file in the root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Add Knowledge Base Documents

Place your VLSI PDF textbooks inside:

```
data/knowledge_base/
```

Recommended books:
- Morris Mano — Digital Design
- Samir Palnitkar — Verilog HDL
- Chris Spear — SystemVerilog for Verification

### 5. Build the Vector Store

```bash
cd rag
python embedder.py
```

### 6. Launch the App

```bash
streamlit run app.py
```

---

## 🧪 Supported Query Types

| Intent    | Examples                                          |
|-----------|---------------------------------------------------|
| `concept` | "Explain setup and hold time violations"          |
| `code`    | "Write a synchronous FIFO in Verilog"             |
| `problem` | "Calculate the slack for a path with 10ns delay"  |

---

## 🛠️ Tech Stack

| Component        | Technology                        |
|-----------------|-----------------------------------|
| UI              | Streamlit                         |
| LLM             | Groq API — LLaMA-3.3-70B          |
| Embeddings      | HuggingFace `all-MiniLM-L6-v2`   |
| Vector Store    | ChromaDB                          |
| Document Loader | LangChain PyPDFDirectoryLoader    |
| Env Management  | python-dotenv                     |

---

## 📄 License

MIT License — see [LICENSE](LICENSE)