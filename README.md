<p align="center">
  <img src="https://img.icons8.com/fluency/96/document.png" width="80" alt="PageIndex Logo"/>
</p>

<h1 align="center">PageIndex RAG</h1>

<p align="center">
  <strong>🧠 Vectorless, Reasoning-Based Document Retrieval</strong><br/>
  <em>What if your RAG system could <b>think</b> instead of just matching vectors?</em>
</p>

<p align="center">
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Get_Started-▶-00C853?style=for-the-badge" alt="Get Started"/></a>
  <a href="#-how-it-works"><img src="https://img.shields.io/badge/How_It_Works-📖-2196F3?style=for-the-badge" alt="How It Works"/></a>
  <a href="#-api-reference"><img src="https://img.shields.io/badge/API_Docs-📡-FF6F00?style=for-the-badge" alt="API Docs"/></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Groq-LLM_Inference-F55036?style=flat-square" alt="Groq"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"/>
</p>

---

## 💡 The Problem with Traditional RAG

Most RAG pipelines follow a **brute-force** approach: chunk documents → embed into vectors → retrieve by cosine similarity. This works, but it has fundamental limitations:

- **Similarity ≠ Relevance** — cosine distance doesn't understand meaning
- **Lost context** — chunking destroys document structure
- **No reasoning** — retrieval is a dumb lookup, not intelligent search

**PageIndex RAG takes a fundamentally different approach** — it builds a hierarchical tree index of your document and uses LLM reasoning to navigate it, just like a human expert would scan a table of contents to find the right section.

<table>
<tr>
<th width="50%">❌ Traditional RAG</th>
<th width="50%">✅ PageIndex RAG (This Project)</th>
</tr>
<tr>
<td>

- Chunk documents into fragments
- Embed chunks into vector DB
- Retrieve by cosine similarity
- Similarity ≠ Relevance
- Context is lost during chunking

</td>
<td>

- Preserve full document structure
- Build hierarchical tree index
- Navigate by LLM reasoning
- Reasoning = Understanding
- Full page context retained

</td>
</tr>
</table>

---

## ✨ Key Features

| Feature                          | Description                                                                              |
| -------------------------------- | ---------------------------------------------------------------------------------------- |
| 🌳 **Tree-Based Indexing**       | Automatically builds a hierarchical index from document structure (TOC or LLM-generated) |
| 🧠 **Reasoning-Based Retrieval** | LLM navigates the tree like a human expert — no vector similarity needed                 |
| 📄 **Full Page Context**         | Retrieves entire pages, not fragments — preserving context and coherence                 |
| 💬 **Built-in Q&A Chat**         | Ask natural language questions and get cited answers with source pages                   |
| 🔍 **Tree Visualization**        | Interactive tree viewer to explore how your document is indexed                          |
| ⚡ **Groq-Powered**              | Ultra-fast inference using Groq's LPU with `llama-3.3-70b-versatile`                     |
| 🚫 **Zero Vector DB**            | No Pinecone, no Weaviate, no Chroma — just pure reasoning                                |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (Port 3000)                       │
│  ┌──────────────┐  ┌──────────────────┐  ┌───────────────────┐ │
│  │  📤 Upload   │  │  🌳 Tree Viewer  │  │  💬 Q&A Chat      │ │
│  │    Panel     │  │   (Index Tree)   │  │  (RAG Interface)  │ │
│  └──────────────┘  └──────────────────┘  └───────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API
┌────────────────────────────┴────────────────────────────────────┐
│                      Backend (Port 8000)                        │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     FastAPI Router                         │ │
│  │    POST /upload    GET /documents    POST /query           │ │
│  └──────────┬─────────────────────────────────┬───────────────┘ │
│             │                                 │                 │
│  ┌──────────▼──────────┐       ┌──────────────▼──────────────┐ │
│  │   Index Pipeline    │       │    Retrieval Pipeline        │ │
│  │ PDF → TOC → Tree    │       │ Query → Tree Search → RAG   │ │
│  └──────────┬──────────┘       └──────────────┬──────────────┘ │
│             │                                 │                 │
│  ┌──────────▼─────────────────────────────────▼──────────────┐ │
│  │                Groq LLM Service                           │ │
│  │            (llama-3.3-70b-versatile)                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Local Storage (./storage/)                    │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **[Groq API Key](https://console.groq.com/)** — free tier available, no credit card needed

### 1. Clone & Install

```bash
git clone https://github.com/tamilarasu18/pageindex-rag-poc.git
cd pageindex-rag-poc

cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Open `.env` and add your Groq API key:

```env
GROQ_API_KEY=gsk_your_api_key_here
```

### 3. Start the Backend

```bash
python main.py
# ✅ Server running → http://localhost:8000
```

### 4. Start the Frontend

```bash
# Open a new terminal
cd frontend
python -m http.server 3000
# ✅ UI available → http://localhost:3000
```

### 5. Try It Out

1. Open `http://localhost:3000` in your browser
2. Upload any PDF document
3. Watch the tree index get built in real-time
4. Ask questions in the Q&A chat and get cited answers!

---

## ⚙️ How It Works

PageIndex replaces vector similarity with a **3-stage reasoning pipeline**:

### Stage 1 — Upload & Extract

```
PDF Document  →  PyPDF2 / pymupdf  →  Page-level text content
```

### Stage 2 — Build Tree Index

```
LLM analyzes first N pages for Table of Contents
  ├── TOC found?    → Parse into hierarchical tree structure
  └── No TOC?       → LLM generates section structure from content

Each tree node contains:
  • Title (section/chapter name)
  • Page range (start → end)
  • Summary (LLM-generated description)
```

### Stage 3 — Reasoning-Based Retrieval

```
User Question
  → LLM reads the tree structure (like scanning a TOC)
  → Identifies most relevant sections via reasoning
  → Extracts full content from those pages
  → Generates answer with source citations
```

> **Why this works:** It mimics how a human expert searches a document — not by matching keywords, but by understanding structure and reasoning about where the answer is likely to be.

---

## 📡 API Reference

| Method   | Endpoint                   | Description                                    |
| -------- | -------------------------- | ---------------------------------------------- |
| `GET`    | `/api/health`              | Health check + API key status                  |
| `POST`   | `/api/upload`              | Upload PDF → triggers background indexing      |
| `GET`    | `/api/documents`           | List all indexed documents                     |
| `GET`    | `/api/documents/{id}`      | Get document details + metadata                |
| `GET`    | `/api/documents/{id}/tree` | Get the generated tree index                   |
| `DELETE` | `/api/documents/{id}`      | Delete document & its index                    |
| `POST`   | `/api/query`               | Ask a question → get RAG answer with citations |

<details>
<summary><b>Example: Ask a Question</b></summary>

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "abc123",
    "question": "What are the key findings?"
  }'
```

**Response:**

```json
{
  "answer": "The key findings include...",
  "sources": [
    { "page": 5, "section": "Results" },
    { "page": 12, "section": "Conclusion" }
  ]
}
```

</details>

---

## 🧪 Test Results

Tested on a 15-page AI/ML report generated with `generate_test_pdf.py`:

| #   | Query Category    | Status  | Response Time | Sources Found |
| --- | ----------------- | ------- | ------------- | ------------- |
| 1   | Factual Retrieval | ✅ Pass | 4.8s          | 2             |
| 2   | Section Lookup    | ✅ Pass | 4.4s          | 4             |
| 3   | Specific Detail   | ✅ Pass | 4.7s          | 1             |
| 4   | Topic Summary     | ✅ Pass | 4.4s          | 1             |
| 5   | Comparison        | ✅ Pass | 4.5s          | 1             |

> **Avg Response Time: 4.6s** · **Success Rate: 100%** · **Zero Failures**

```bash
# Run the tests yourself
cd backend
python generate_test_pdf.py   # Generate sample PDF
python run_tests.py            # Run automated test suite
```

---

## 📂 Project Structure

```
pageindex-rag-poc/
│
├── backend/
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Centralized configuration & settings
│   ├── services/
│   │   ├── llm_service.py       # Groq API wrapper (OpenAI-compatible)
│   │   ├── pdf_service.py       # PDF text extraction (PyPDF2 + pymupdf)
│   │   ├── index_service.py     # 🧠 Core: Tree index builder (PageIndex logic)
│   │   ├── retrieval_service.py # 🧠 Core: Reasoning-based tree search + RAG
│   │   └── storage_service.py   # Local file & metadata persistence
│   ├── routes/
│   │   ├── documents.py         # Upload / list / delete endpoints
│   │   └── query.py             # Q&A endpoint
│   ├── generate_test_pdf.py     # Generate sample test PDF
│   ├── run_tests.py             # Automated test suite
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Environment template
│
└── frontend/
    ├── index.html               # Single-page application
    ├── styles.css               # Clean, professional UI theme
    └── app.js                   # Upload, tree viewer & chat logic
```

---

## 🛠️ Tech Stack

| Layer           | Technology                           | Purpose                                       |
| --------------- | ------------------------------------ | --------------------------------------------- |
| **Backend**     | Python, FastAPI, Uvicorn             | REST API server                               |
| **LLM**         | Groq API (`llama-3.3-70b-versatile`) | Tree building + reasoning + answer generation |
| **PDF Parsing** | PyPDF2, pymupdf                      | Robust text extraction with fallback          |
| **Frontend**    | HTML, CSS, JavaScript (vanilla)      | Lightweight, zero-dependency UI               |
| **Storage**     | Local filesystem (JSON + PDF)        | Simple persistence, no DB required            |

---

## 🗺️ Roadmap

- [ ] Multi-document querying (cross-document reasoning)
- [ ] Support for DOCX, PPTX, and other formats
- [ ] Streaming responses for real-time answer generation
- [ ] Docker Compose for one-command setup
- [ ] Cloud deployment (Vercel + Railway/Render)
- [ ] Evaluation benchmarks against traditional vector RAG

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — free to use for demos, POCs, learning, and production.

---

<p align="center">
  <strong>Built with ❤️ to demonstrate that RAG doesn't need vectors to be intelligent.</strong>
</p>

<p align="center">
  <a href="https://github.com/tamilarasu18/pageindex-rag-poc/stargazers">⭐ Star this repo</a> if you found it useful!
</p>
