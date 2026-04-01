# News Ledger - Technical Documentation

## Overview

News Ledger is a newspaper-style news dashboard that displays curated news articles organized by category. It's designed to be populated by an AI agent via API.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│                   Port 3000 (Tailwind CSS)                   │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP (REACT_APP_BACKEND_URL)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│                       Port 8001                              │
│                    /api/* endpoints                          │
└─────────────────────────┬───────────────────────────────────┘
                          │ SQLAlchemy Async
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database (SQLite/PostgreSQL)               │
│              SQLite: ./news_ledger.db (local)                │
│         PostgreSQL: For production deployment                │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### Tables

```sql
-- Daily editions container
digests
├── id (UUID, PK)
├── edition_name (VARCHAR) -- "News Ledger"
├── digest_date (DATE) -- The date this digest covers
├── recency_window_hours (INT) -- How old news can be (default: 24)
├── status (VARCHAR) -- draft | published | archived
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

-- Main articles (max 5 per category per digest)
articles
├── id (UUID, PK)
├── digest_id (UUID, FK → digests.id)
├── category (VARCHAR) -- U.S. | World | Local | Business | Technology | Entertainment | Sports | Science | Health
├── rank (INT 1-5) -- Display priority (1 = top story)
├── story_cluster_id (VARCHAR) -- For deduplication tracking
├── headline (TEXT)
├── summary (TEXT)
├── why_it_matters (TEXT)
├── watch_next (TEXT)
├── political_synthesis (TEXT, nullable)
├── importance_score (FLOAT 0-1)
├── is_political (BOOLEAN)
├── image_url (TEXT, nullable)
├── curated_by (VARCHAR)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

-- Supporting articles (max 3 per parent article, depth=1)
supporting_articles
├── id (UUID, PK)
├── parent_article_id (UUID, FK → articles.id)
├── headline (TEXT)
├── summary (TEXT)
├── context_type (VARCHAR) -- context | alternative | deep_dive
├── source_name (VARCHAR)
├── source_url (TEXT)
├── image_url (TEXT, nullable)
├── created_at (TIMESTAMP)
└── updated_at (TIMESTAMP)

-- Sources for main articles
article_sources
├── id (UUID, PK)
├── article_id (UUID, FK → articles.id)
├── source_name (VARCHAR)
├── source_url (TEXT)
├── source_type (VARCHAR) -- primary | supporting | reference
└── created_at (TIMESTAMP)
```

## API Reference

Base URL: `http://localhost:8001/api` (local) or your deployed URL

### Core Endpoints

#### Health Check
```bash
GET /api/
# Response: {"message": "News Ledger API v2.0", "status": "healthy"}
```

#### Get Categories
```bash
GET /api/categories
# Response: {"categories": ["U.S.", "World", "Local", "Business", "Technology", "Entertainment", "Sports", "Science", "Health"]}
```

### Digest Endpoints

#### List Digests
```bash
GET /api/digests?limit=10&status=published
# Returns list of digest summaries
```

#### Get Digest by ID
```bash
GET /api/digests/{digest_id}
# Returns full digest with all nested articles
```

#### Get Digest by Date
```bash
GET /api/digests/date/2026-04-01
# Returns digest for specific date
```

#### Create Digest
```bash
POST /api/digests
Content-Type: application/json

{
  "edition_name": "News Ledger",
  "digest_date": "2026-04-01",
  "recency_window_hours": 24,
  "status": "draft",
  "articles": []  # Optional, can add articles separately
}
```

#### Delete Digest (cascades to all articles)
```bash
DELETE /api/digests/{digest_id}
```

### Bulk Ingest (PRIMARY ENDPOINT FOR AI AGENT)

```bash
POST /api/articles/ingest
Content-Type: application/json

{
  "edition_name": "News Ledger",
  "digest_date": "2026-04-01",
  "recency_window_hours": 24,
  "articles": [
    {
      "category": "U.S.",
      "rank": 1,
      "story_cluster_id": "us-politics-001",
      "headline": "Your headline here",
      "summary": "Brief summary of the article",
      "why_it_matters": "Explanation of significance",
      "watch_next": "What to monitor going forward",
      "political_synthesis": "Political analysis (nullable)",
      "importance_score": 0.95,
      "is_political": true,
      "image_url": "https://example.com/image.jpg",
      "curated_by": "AI News Agent",
      "supporting_articles": [
        {
          "headline": "Related story headline",
          "summary": "Brief summary",
          "context_type": "context",  // or "alternative" or "deep_dive"
          "source_name": "Reuters",
          "source_url": "https://reuters.com/article"
        }
      ],
      "sources": [
        {
          "source_name": "Washington Post",
          "source_url": "https://washingtonpost.com/article",
          "source_type": "primary"  // or "supporting" or "reference"
        }
      ]
    }
  ]
}

# Response:
{
  "digest_id": "uuid-here",
  "edition_name": "News Ledger",
  "digest_date": "2026-04-01",
  "articles_created": 5,
  "supporting_articles_created": 8,
  "sources_created": 10
}
```

**Important:** Bulk ingest REPLACES any existing digest for that date. This is intentional for daily rebuilds.

### Article Endpoints

#### Get Articles with Filters
```bash
GET /api/articles?category=U.S.&digest_date=2026-04-01&limit=5
# Returns articles matching filters with nested supporting_articles and sources
```

#### Create Single Article
```bash
POST /api/articles?digest_id={uuid}
Content-Type: application/json

{
  "category": "Technology",
  "rank": 1,
  "headline": "...",
  # ... same structure as in bulk ingest
}
```

#### Update Article
```bash
PUT /api/articles/{article_id}
Content-Type: application/json

{
  "headline": "Updated headline",
  "summary": "Updated summary"
}
```

#### Delete Article
```bash
DELETE /api/articles/{article_id}
```

### Supporting Article Endpoints

#### Add Supporting Article
```bash
POST /api/articles/{article_id}/supporting
Content-Type: application/json

{
  "headline": "Supporting headline",
  "summary": "Supporting summary",
  "context_type": "deep_dive",
  "source_name": "MIT Tech Review"
}
```

#### Delete Supporting Article
```bash
DELETE /api/supporting/{supporting_id}
```

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env:
# DATABASE_URL="sqlite+aiosqlite:///./news_ledger.db"  # SQLite (default)
# DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/news_ledger"  # PostgreSQL

# Run server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
yarn install

# Configure environment
# Edit .env:
# REACT_APP_BACKEND_URL=http://localhost:8001

# Run development server
yarn start
```

### Environment Variables

**Backend (.env)**
```bash
DATABASE_URL="sqlite+aiosqlite:///./news_ledger.db"
MONGO_URL="mongodb://localhost:27017"  # Legacy, can ignore
DB_NAME="news_ledger"
CORS_ORIGINS="*"
```

**Frontend (.env)**
```bash
REACT_APP_BACKEND_URL=http://localhost:8001
```

## AI Agent Integration Guide

### Daily Digest Workflow

Your agent should follow this workflow:

1. **Gather News** - Collect and cluster news from sources
2. **Rank by Category** - Assign rank 1-5 within each category
3. **Generate Content** - Create headline, summary, why_it_matters, watch_next
4. **Add Supporting Context** - Attach 0-3 supporting articles per main article
5. **Ingest via API** - POST to `/api/articles/ingest`

### Example Agent Payload Structure

```python
payload = {
    "edition_name": "News Ledger",
    "digest_date": "2026-04-01",  # Today's date
    "recency_window_hours": 24,
    "articles": [
        {
            "category": "U.S.",  # Must be valid category
            "rank": 1,  # 1 = most important, max 5 per category
            "story_cluster_id": "unique-cluster-id",  # For dedup tracking
            "headline": "Clear, compelling headline",
            "summary": "2-3 sentence summary",
            "why_it_matters": "Significance explanation",
            "watch_next": "What to monitor",
            "political_synthesis": None,  # or political analysis string
            "importance_score": 0.95,  # 0.0 to 1.0
            "is_political": True,
            "image_url": "https://...",  # Optional
            "curated_by": "AI News Agent",
            "supporting_articles": [
                {
                    "headline": "Context article",
                    "summary": "Brief context",
                    "context_type": "context",  # context | alternative | deep_dive
                    "source_name": "Reuters",
                    "source_url": "https://..."
                }
            ],
            "sources": [
                {
                    "source_name": "Original Source",
                    "source_url": "https://...",
                    "source_type": "primary"  # primary | supporting | reference
                }
            ]
        }
    ]
}
```

### Valid Categories
```
U.S., World, Local, Business, Technology, Entertainment, Sports, Science, Health
```

### Constraints
- Maximum **5 articles per category** per digest
- Maximum **3 supporting articles** per main article
- `rank` must be 1-5 (1 = highest priority)
- `context_type` must be: `context`, `alternative`, or `deep_dive`
- `source_type` must be: `primary`, `supporting`, or `reference`

### Python Client Example

```python
import requests
from datetime import date

API_URL = "http://localhost:8001/api"

def ingest_daily_digest(articles: list):
    """Ingest a full day's digest"""
    payload = {
        "edition_name": "News Ledger",
        "digest_date": str(date.today()),
        "recency_window_hours": 24,
        "articles": articles
    }
    
    response = requests.post(
        f"{API_URL}/articles/ingest",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Created digest {result['digest_id']}")
        print(f"Articles: {result['articles_created']}")
        print(f"Supporting: {result['supporting_articles_created']}")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Example usage
articles = [
    {
        "category": "Technology",
        "rank": 1,
        "headline": "Major Tech Announcement",
        "summary": "Summary here...",
        "why_it_matters": "Impact explanation...",
        "importance_score": 0.9,
        "is_political": False,
        "curated_by": "AI Agent"
    }
]

ingest_daily_digest(articles)
```

## Deployment Notes

### PostgreSQL Setup
```bash
# Create database
createdb news_ledger

# Update backend/.env
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/news_ledger"
```

### Production Checklist
- [ ] Set `CORS_ORIGINS` to specific domains
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up SSL/HTTPS
- [ ] Configure proper logging
- [ ] Set up database backups

## File Structure

```
/app/
├── backend/
│   ├── server.py          # FastAPI application
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── database.py        # Database connection
│   ├── requirements.txt   # Python dependencies
│   ├── .env               # Environment config
│   └── news_ledger.db     # SQLite database (auto-created)
│
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Component styles
│   │   └── index.css      # Global styles + Tailwind
│   ├── package.json       # Node dependencies
│   └── .env               # Frontend config
│
└── memory/
    └── PRD.md             # Product requirements doc
```

## Troubleshooting

### Common Issues

**Database not creating tables:**
```bash
# Tables auto-create on startup. Check logs:
tail -f /var/log/supervisor/backend.err.log
```

**CORS errors:**
```bash
# Update backend/.env
CORS_ORIGINS="http://localhost:3000,https://yourdomain.com"
# Restart backend
```

**Articles not showing:**
```bash
# Check if digest exists
curl http://localhost:8001/api/digests

# Check if articles exist
curl http://localhost:8001/api/articles?limit=10
```

**Category filter not working:**
```bash
# Use exact category names with proper case
curl "http://localhost:8001/api/articles?category=U.S."
```
