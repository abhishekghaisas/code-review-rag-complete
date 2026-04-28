# GitHub Ingestion Setup Guide

## 📦 Installation

### 1. Place the files:

```bash
cd backend/app

# Download and place github_ingestion.py
cp ~/Downloads/github_ingestion.py .

# Replace main.py with updated version
cp ~/Downloads/main.py .
```

### 2. The GitPython dependency should already be in requirements.txt, but verify:

```bash
cd backend
grep gitpython requirements.txt
# Should show: gitpython==3.1.41
```

If not there, add it:
```bash
echo "gitpython==3.1.41" >> requirements.txt
pip install gitpython==3.1.41
```

### 3. Restart backend:

```bash
uvicorn app.main:app --reload
```

## 🧪 Test GitHub Ingestion

### Option 1: Via Swagger UI

1. Go to http://localhost:8000/docs
2. Find **POST /api/ingest**
3. Click "Try it out"
4. Use this example:

```json
{
  "repo_url": "https://github.com/psf/requests"
}
```

5. Click "Execute"
6. Wait 30-60 seconds (it's cloning and processing!)

### Option 2: Via curl

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/yourusername/small-repo"
  }'
```

### Option 3: Via Frontend

1. Open http://localhost:5173
2. Go to **Ingest** tab
3. Click **"GitHub Repo"** button
4. Enter: `https://github.com/psf/requests`
5. Click "Ingest Repository"

## ✅ What Happens:

1. **Clones** the repository to temp directory
2. **Scans** all files recursively
3. **Filters** to only code files (Python, JS, etc.)
4. **Chunks** large files into ~1000 char pieces with overlap
5. **Ingests** into ChromaDB vector database
6. **Cleans up** temp directory

## 📊 Supported Languages:

- Python (.py)
- JavaScript (.js, .jsx, .mjs)
- TypeScript (.ts, .tsx)
- Java (.java)
- Go (.go)
- Rust (.rs)
- C/C++ (.c, .cpp, .h, .hpp)
- Ruby (.rb)
- PHP (.php)
- Swift (.swift)
- Kotlin (.kt)
- And more!

## 🚫 What Gets Ignored:

- `node_modules/`, `.git/`, `__pycache__/`
- `build/`, `dist/`, `target/`
- Binary files, lock files
- Files larger than 1MB (configurable)

## ⚙️ Configuration:

In `github_ingestion.py`, you can adjust:

```python
# Maximum file size
github = GitHubIngestion(max_file_size_mb=10)

# Chunk size and overlap
chunks = github.process_repository(
    repo_url=repo_url,
    chunk_size=1000,     # Characters per chunk
    chunk_overlap=100    # Overlap between chunks
)
```

## 🎯 Good Repos to Test With:

**Small (fast, for testing):**
- https://github.com/psf/requests (~100 files)
- https://github.com/pallets/flask (~200 files)

**Medium:**
- https://github.com/fastapi/fastapi (~500 files)
- https://github.com/django/django (~2000 files)

**Large (will take time):**
- https://github.com/pytorch/pytorch (~10,000+ files)

## 💡 Tips:

- Start with small repos to test
- Large repos can take 2-5 minutes
- Monitor backend logs to see progress
- Check `/api/stats` to see total chunks after ingestion

## 🐛 Troubleshooting:

**Error: "Failed to clone repository"**
- Check if repo URL is valid and public
- Private repos need authentication (not implemented yet)

**Error: "No module named 'git'"**
- Install GitPython: `pip install gitpython==3.1.41`

**Takes too long:**
- Use smaller repos for testing
- Check backend logs for progress
- Large repos are slow but will work

## 🎉 Success!

After ingestion completes, check:
- `/api/stats` - Should show increased chunk count
- Do a code review with RAG enabled
- You should now see similar code from the ingested repo!

---

**Ready to ingest entire codebases for RAG!** 🚀
