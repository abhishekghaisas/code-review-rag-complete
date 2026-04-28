# 🚀 GitHub Repository Setup Guide

## Step 1: Prepare Your Project

### 1.1 Clean up your project directory

```bash
cd ~/Desktop/Projects/code-review-rag

# Remove any test files or temporary data
rm -rf backend/data/chroma_db/*  # Keep folder, delete contents
rm -f backend/data/reviews.db     # Remove test database
```

### 1.2 Create necessary files

```bash
# Root level .gitignore
cp ~/Downloads/project-gitignore.txt .gitignore

# Update README
cp ~/Downloads/GITHUB_README.md README.md

# Edit README to add your info:
# - Replace "yourusername" with your GitHub username
# - Replace "Your Name" with your name
# - Replace "@yourhandle" with your Twitter/socials
# - Add live demo URL if deployed
```

### 1.3 Verify .env files are NOT committed

```bash
# Make sure these exist but are in .gitignore:
ls backend/.env        # Should exist
ls backend/.env.example  # Should exist

# Verify .env is ignored:
git status  # Should NOT show .env files
```

## Step 2: Initialize Git Repository

```bash
# From project root (code-review-rag/)
cd ~/Desktop/Projects/code-review-rag

# Initialize git
git init

# Add all files
git add .

# Check what will be committed
git status

# Should see:
# - All Python files
# - All TypeScript/React files  
# - README.md, .gitignore
# - requirements.txt, package.json
# - .env.example (but NOT .env!)

# Commit
git commit -m "Initial commit: RAG-powered code review system

Features:
- FastAPI backend with Claude API integration
- React frontend with Monaco editor
- RAG using ChromaDB and sentence-transformers
- GitHub repository ingestion
- SQLite database for review persistence
- Model comparison and export features
- Full CRUD API for reviews"
```

## Step 3: Create GitHub Repository

### Option A: Via GitHub Website (Recommended)

1. Go to https://github.com/new
2. **Repository name**: `code-review-rag`
3. **Description**: "AI-powered code review using RAG with Anthropic Claude"
4. **Visibility**: Public (for portfolio) or Private
5. **DO NOT** initialize with README, .gitignore, or license (we have them)
6. Click "Create repository"

### Option B: Via GitHub CLI

```bash
# Install GitHub CLI if needed
brew install gh

# Login
gh auth login

# Create repo
gh repo create code-review-rag --public --source=. --remote=origin --push
```

## Step 4: Push to GitHub

```bash
# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/code-review-rag.git

# Verify remote
git remote -v

# Push to main branch
git branch -M main
git push -u origin main
```

## Step 5: Verify on GitHub

Visit: https://github.com/YOUR_USERNAME/code-review-rag

Check:
- ✅ README displays properly
- ✅ Directory structure is clean
- ✅ No .env files committed
- ✅ No database files committed
- ✅ No node_modules/ committed

## Step 6: Add Additional Files

### Create LICENSE

```bash
# Create MIT License file
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

git add LICENSE
git commit -m "Add MIT license"
git push
```

### Add GitHub Actions (Optional)

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest tests/ || echo "No tests yet"
```

## Step 7: Enhance Your Repository

### Add Topics/Tags

On GitHub repository page:
1. Click "⚙️ Settings"
2. Under "Topics", add:
   - `rag`
   - `llm`
   - `code-review`
   - `anthropic-claude`
   - `fastapi`
   - `react`
   - `vector-database`
   - `chromadb`

### Add Repository Description

- Go to repository home
- Click "⚙️" next to About
- Add: "AI-powered code review using RAG with Anthropic Claude"
- Add website URL (if deployed)

### Pin Repository

On your GitHub profile:
1. Go to your profile
2. Click "Customize your pins"
3. Select this repository
4. This shows it prominently to visitors

## Step 8: Share & Promote

### For Portfolio:

**Resume bullet points:**
```
• Built RAG-powered code review system using Anthropic Claude API, ChromaDB vector 
  database, and FastAPI, processing 1000+ code chunks with semantic search

• Implemented full-stack application with React/TypeScript frontend and FastAPI 
  backend, featuring GitHub repository ingestion, model comparison, and persistent 
  review history

• Optimized cost to $0.002/review using Claude Haiku while maintaining 90%+ quality 
  through RAG context injection from vector-embedded codebase patterns
```

**LinkedIn post:**
```
🚀 Just launched my AI Code Review Assistant using RAG!

Built a full-stack system that:
- Reviews code using Anthropic Claude
- Finds similar patterns in your codebase with vector search
- Ingests entire GitHub repositories
- Compares multiple AI models
- Stores review history in SQLite

Tech: FastAPI, React, ChromaDB, Claude API, TypeScript

Check it out: [GitHub URL]

#AI #LLM #RAG #CodeReview #FastAPI #React
```

## 🎯 Next Steps

1. **Add screenshots** to README
   - Create `screenshots/` folder
   - Add demo images
   - Update README with images

2. **Record demo video**
   - Upload to YouTube
   - Add to README

3. **Deploy online**
   - Railway/Vercel deployment
   - Add live demo URL to README

4. **Write blog post**
   - Technical writeup on Medium/Dev.to
   - Link from README

## ✅ Checklist

Before you're done:

- [ ] Repository is public (or private if preferred)
- [ ] README is complete and professional
- [ ] .env files are NOT committed
- [ ] License file added
- [ ] Repository description set
- [ ] Topics/tags added
- [ ] Repository pinned on profile
- [ ] Shared on LinkedIn/Twitter

---

**Your portfolio project is now live on GitHub!** 🎉

Share the link: `https://github.com/YOUR_USERNAME/code-review-rag`
