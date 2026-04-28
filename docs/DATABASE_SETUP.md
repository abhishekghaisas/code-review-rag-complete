# 💾 Database Integration Setup

## ✨ What This Adds:

- ✅ **Persistent storage** for all reviews (SQLite database)
- ✅ **Review history** accessible from any device
- ✅ **Ingestion job tracking** with status and timestamps
- ✅ **Easy migration** to PostgreSQL for production
- ✅ **API endpoints** for CRUD operations

## 📥 Installation

### 1. Place backend files:

```bash
cd backend/app

# Download and place these files:
cp ~/Downloads/database.py .
cp ~/Downloads/main-with-db.py main.py  # Replace main.py
```

### 2. Place frontend file:

```bash
cd frontend/src

# Replace api.ts
cp ~/Downloads/api-with-db.ts api.ts
```

### 3. Create data directory:

```bash
cd backend
mkdir -p data
```

### 4. Restart both servers:

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

You should see:
```
INFO - Initializing database...
INFO - ✅ Database initialized
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## 🗄️ Database Schema

### `code_reviews` table:
- `id` - Primary key
- `code` - Code that was reviewed
- `language` - Programming language
- `model` - Claude model used
- `use_rag` - Whether RAG was enabled
- `review_text` - The review content
- `similar_code` - JSON array of similar code
- `similar_code_metadata` - JSON array of metadata
- `model_used` - Actual model that generated review
- `rag_enabled` - RAG status
- `context_used` - Whether RAG context was used
- `created_at` - Timestamp
- `user_id` - Optional user tracking

### `ingestion_jobs` table:
- `id` - Primary key
- `job_type` - 'manual' or 'github'
- `source` - GitHub URL or 'manual input'
- `status` - 'pending', 'success', 'error'
- `chunks_ingested` - Number of chunks
- `error_message` - If failed
- `created_at` - Started timestamp
- `completed_at` - Finished timestamp

## 🎯 New API Endpoints:

### Reviews:
- `GET /api/reviews` - List all reviews
- `GET /api/reviews/{id}` - Get specific review
- `DELETE /api/reviews/{id}` - Delete review
- `POST /api/review` - Create review (now saves to DB!)

### Ingestion Jobs:
- `GET /api/ingestion/jobs` - List ingestion history

## 🧪 Test It:

### 1. Create a review:

```bash
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def hello():\n    print(\"hi\")",
    "language": "python",
    "model": "claude-haiku-4-5-20251001",
    "use_rag": true,
    "n_similar": 3
  }'
```

Response will include `"id": 1` ← Database ID!

### 2. List reviews:

```bash
curl http://localhost:8000/api/reviews
```

### 3. Get specific review:

```bash
curl http://localhost:8000/api/reviews/1
```

### 4. Delete review:

```bash
curl -X DELETE http://localhost:8000/api/reviews/1
```

## 📁 Database Location:

SQLite file: `backend/data/reviews.db`

To view/inspect:
```bash
cd backend/data
sqlite3 reviews.db
.tables
SELECT * FROM code_reviews;
.quit
```

## 🔄 Migrating to PostgreSQL (Optional):

For production, switch to PostgreSQL:

1. Install psycopg2:
```bash
pip install psycopg2-binary
```

2. Update `.env`:
```bash
DATABASE_URL=postgresql://user:password@localhost/code_review_db
```

3. Restart - SQLAlchemy handles the rest!

## ✅ What Changed:

### Backend:
- ✅ Reviews automatically saved to database
- ✅ New endpoints for list/get/delete reviews
- ✅ Ingestion jobs tracked
- ✅ Database initialized on startup

### Frontend:
- ✅ ReviewHistory now loads from API (not localStorage!)
- ✅ Can delete reviews
- ✅ Pagination support for large histories
- ✅ Review IDs tracked

## 🎉 Benefits:

1. **Persistent** - Reviews survive browser cache clears
2. **Shareable** - Access from any device
3. **Searchable** - Can add search later
4. **Analytics** - Can track usage patterns
5. **Production-ready** - Easy PostgreSQL migration

## 🐛 Troubleshooting:

**Error: "No module named 'sqlalchemy'"**
```bash
pip install sqlalchemy==2.0.49
```

**Database file not created:**
- Check `backend/data/` directory exists
- Check write permissions

**Reviews not showing in History tab:**
- Check browser console for API errors
- Check backend logs
- Test API directly: `curl http://localhost:8000/api/reviews`

---

**Your reviews are now persistent and production-ready!** 🎉
