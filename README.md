# 🚀 Code Review RAG Assistant

An AI-powered code review system using Retrieval-Augmented Generation (RAG) with Anthropic Claude and vector search.

[![CI](https://github.com/abhishekghaisas/code-review-rag-complete/actions/workflows/ci.yml/badge.svg)](https://github.com/abhishekghaisas/code-review-rag-complete/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![React](https://img.shields.io/badge/React-18.2-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🤖 **AI-Powered Reviews** - Claude 4.5 Haiku/Sonnet for intelligent code analysis
- 🔍 **RAG Integration** - Semantic search finds similar code patterns in your codebase
- 📤 **GitHub Ingestion** - Clone and ingest entire repositories automatically
- 🔄 **Model Comparison** - Compare reviews from multiple models side-by-side
- 📊 **Review History** - Persistent database stores all reviews
- 📥 **Export Options** - Download as Markdown, JSON, or plain text
- 💾 **Code Ingestion** - Manual code upload or GitHub repository cloning
- ⚡ **Real-time Analysis** - Fast reviews with streaming responses

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │ React + TypeScript + Monaco Editor
│  (Port 5173)│
└──────┬──────┘
       │
       ↓ HTTP/REST
┌────────────────────────────────────────────┐
│          FastAPI Backend (Port 8000)       │
│                                            │
│  ┌────────────┐      ┌──────────────┐    │
│  │ GitHub     │      │   RAG        │    │
│  │ Ingestion  │──────▶   Engine     │    │
│  └────────────┘      └──────┬───────┘    │
│                              │             │
│  ┌────────────┐      ┌──────▼───────┐    │
│  │ SQLite DB  │      │   Claude     │    │
│  │ (Reviews)  │      │   API        │    │
│  └────────────┘      └──────────────┘    │
│                              │             │
│  ┌────────────┐      ┌──────▼───────┐    │
│  │ ChromaDB   │◀─────│ sentence-    │    │
│  │ (Vectors)  │      │ transformers │    │
│  └────────────┘      └──────────────┘    │
└────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/code-review-rag.git
cd code-review-rag/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run server
uvicorn app.main:app --reload
```

Backend runs at: http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs at: http://localhost:5173

## 🎯 Usage

### 1. Review Code
- Paste code in the editor
- Select Claude model (Haiku 4.5, Sonnet 4, etc.)
- Toggle RAG for context-aware reviews
- Click "Review Code"

### 2. Ingest Code
- Go to "Ingest" tab
- **Manual**: Paste code directly
- **GitHub**: Enter repository URL
- Code is vectorized and searchable

### 3. Compare Models
- Go to "Compare" tab
- Select 2-3 models
- Compare quality and style differences

### 4. View History
- Go to "History" tab
- Browse all past reviews
- Click to reload or delete

## 💰 Cost Optimization

| Model | Cost/Review | Quality | Use Case |
|-------|------------|---------|----------|
| Claude Haiku 4.5 | ~$0.002 | 9/10 | ⭐ Recommended |
| Claude Sonnet 4 | ~$0.006 | 10/10 | High-stakes |
| Claude 3 Haiku | ~$0.0006 | 8.5/10 | Budget |

**Budget-friendly:** $10 = 5,000 Haiku reviews or 1,600 Sonnet reviews

## 📊 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Anthropic Claude** - LLM for code review
- **ChromaDB** - Vector database for RAG
- **SQLAlchemy** - ORM for review storage
- **sentence-transformers** - Local embeddings (free!)
- **GitPython** - Repository cloning
- **SQLite** - Review persistence

### Frontend
- **React + TypeScript** - UI framework
- **Monaco Editor** - VS Code editor component
- **Tailwind CSS** - Styling
- **Vite** - Build tool
- **Axios** - API client

## 🔧 Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional
DATABASE_URL=sqlite:///./data/reviews.db  # Or PostgreSQL
CHROMA_DB_PATH=./data/chroma_db
DEFAULT_MODEL=claude-haiku-4-5-20251001
LOG_LEVEL=INFO
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

```bash
# Review code
POST /api/review

# List reviews
GET /api/reviews

# Ingest code
POST /api/ingest

# Get stats
GET /api/stats

# List models
GET /api/models
```

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up --build

# Access
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```

## 🚢 Deployment

### Option 1: Railway (Recommended)
1. Fork this repository
2. Connect to Railway
3. Add `ANTHROPIC_API_KEY` environment variable
4. Deploy!

### Option 2: Vercel (Frontend) + Modal (Backend)
- Frontend: Deploy to Vercel
- Backend: Deploy to Modal with GPU support

## 📈 Roadmap

- [x] Basic code review
- [x] RAG integration
- [x] GitHub ingestion
- [x] Review history
- [x] Model comparison
- [x] Export reviews
- [ ] Multi-user authentication
- [ ] Review templates
- [ ] Code diff integration
- [ ] Slack/Discord bot
- [ ] VS Code extension

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [Anthropic](https://www.anthropic.com/) for Claude API
- [ChromaDB](https://www.trychroma.com/) for vector database
- [sentence-transformers](https://www.sbert.net/) for embeddings

## 📧 Contact

Your Name - [@yourhandle](https://twitter.com/yourhandle)

Project Link: [https://github.com/yourusername/code-review-rag](https://github.com/yourusername/code-review-rag)

---

⭐ Star this repo if you find it helpful!

Built with ❤️ as a portfolio project demonstrating RAG, LLMs, and full-stack development.