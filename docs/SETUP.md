# 🚀 Setup & Usage Guide

Complete guide to get your Code Review RAG Assistant up and running.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** - Check: `python --version`
- **Node.js 18+** - Check: `node --version`
- **Git** - Check: `git --version`
- **OpenRouter Account** - Sign up at https://openrouter.ai ($1 free credit!)

## 🔧 Quick Setup (5 minutes)

### Step 1: Clone the Repository

```bash
cd code-review-rag
```

### Step 2: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env
```

### Step 3: Configure OpenRouter API Key

1. Go to https://openrouter.ai
2. Sign up (GitHub/Google login)
3. Go to "Keys" section
4. Create a new API key
5. Copy the key (starts with `sk-or-v1-...`)
6. Edit `backend/.env` and paste your key:

```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

### Step 4: Test Backend

```bash
# Make sure you're in backend/ directory with venv activated
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Visit http://localhost:8000/docs to see the API documentation!

### Step 5: Frontend Setup (New Terminal)

```bash
# Navigate to frontend (from project root)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Visit http://localhost:5173 to see the UI!

## 🧪 Testing the System

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database_connected": true,
  "llm_client_initialized": true
}
```

### Test 2: List Available Models

```bash
curl http://localhost:8000/api/models
```

You should see free and paid models listed.

### Test 3: Code Review (Without RAG)

```bash
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b):\n    return a + b",
    "language": "python",
    "model": "meta-llama/llama-3.2-3b-instruct:free",
    "use_rag": false
  }'
```

### Test 4: Ingest Sample Code

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "code_chunks": [
      {
        "id": "example_1",
        "code": "def calculate_sum(numbers):\n    return sum(numbers)",
        "language": "python",
        "metadata": {
          "file_path": "utils.py",
          "function_name": "calculate_sum"
        }
      }
    ]
  }'
```

### Test 5: Code Review (With RAG)

```bash
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def get_total(items):\n    total = 0\n    for i in range(len(items)):\n        total += items[i]\n    return total",
    "language": "python",
    "model": "meta-llama/llama-3.2-3b-instruct:free",
    "use_rag": true
  }'
```

Now it should reference the similar code you ingested!

## 🎯 Common Use Cases

### Use Case 1: Review a Python Function

```python
import requests

code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

response = requests.post(
    "http://localhost:8000/api/review",
    json={
        "code": code,
        "language": "python",
        "model": "meta-llama/llama-3.2-3b-instruct:free"
    }
)

print(response.json()["review"])
```

### Use Case 2: Ingest a Repository's Code

```python
import requests
import os
import glob

def ingest_python_files(directory):
    """Ingest all Python files from a directory"""
    chunks = []
    
    for filepath in glob.glob(f"{directory}/**/*.py", recursive=True):
        with open(filepath, 'r') as f:
            code = f.read()
            
        chunks.append({
            "id": filepath.replace("/", "_"),
            "code": code,
            "language": "python",
            "metadata": {
                "file_path": filepath,
                "repo": os.path.basename(directory)
            }
        })
    
    response = requests.post(
        "http://localhost:8000/api/ingest",
        json={"code_chunks": chunks}
    )
    
    return response.json()

# Example: Ingest your project
result = ingest_python_files("./my-python-project")
print(f"Ingested {result['chunks_ingested']} code chunks!")
```

### Use Case 3: Compare Models

```python
import requests

code = "def process_data(items):\n    return [x * 2 for x in items]"

models = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "google/gemini-flash-1.5:free",
    "anthropic/claude-3.5-haiku"  # This one costs ~$0.002
]

for model in models:
    response = requests.post(
        "http://localhost:8000/api/review",
        json={"code": code, "language": "python", "model": model}
    )
    
    print(f"\n=== {model} ===")
    print(response.json()["review"])
```

## 🐛 Troubleshooting

### Problem: "OpenRouter API key not found"

**Solution:** Make sure you created `backend/.env` with your API key:
```bash
cd backend
cat .env  # Should show your key
```

### Problem: "ModuleNotFoundError"

**Solution:** Make sure virtual environment is activated and dependencies installed:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Problem: "Address already in use" (Port 8000 or 5173)

**Solution:** Kill the process or use different port:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

### Problem: Frontend can't connect to backend

**Solution:** Check CORS settings in `backend/.env`:
```bash
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

### Problem: Slow embeddings generation

**Solution:** First time running downloads the embedding model (~80MB). This is normal and only happens once. The model is cached locally.

### Problem: "Rate limit exceeded" on OpenRouter

**Solution:** 
- You're using free tier (20 requests/minute)
- Wait a minute or upgrade to paid tier
- For development, this is usually fine

## 📊 Monitoring Costs

### Check Your Usage on OpenRouter

1. Go to https://openrouter.ai/activity
2. View your credit balance and usage
3. Free tier: $1 credit should last for ~500-1000 reviews depending on model

### Estimate Costs

Free models (development):
- Cost: $0.00 per review
- Unlimited usage within rate limits

Paid models (production):
- Claude Haiku: ~$0.002 per review
- GPT-4o Mini: ~$0.001 per review
- Budget planning: $5 = 2,500-5,000 reviews

## 🚀 Next Steps

Now that you have the system running:

1. **Ingest your codebase** - Add your own repository's code
2. **Test different models** - Compare free vs paid quality
3. **Customize prompts** - Edit `openrouter_client.py` to tune reviews
4. **Build the frontend** - We'll create the React UI next
5. **Deploy** - Use Docker Compose or deploy to Railway/Modal

## 📚 Additional Resources

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)

## 🤝 Need Help?

- Check the API docs: http://localhost:8000/docs
- Review logs: Backend terminal shows detailed logs
- Test endpoints: Use the Swagger UI at `/docs`

---

**You're all set! 🎉**

The backend is running and ready to review code. Next, we'll build the frontend UI to make it easy to use!
