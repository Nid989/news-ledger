# News Ledger - Product Requirements Document

## Original Problem Statement
Create a news dashboard called "News Ledger" with the following categories:
- U.S., World, Local, Business, Technology, Entertainment, Sports, Science, Health

Design should follow a classic vintage newspaper style aesthetic.

## User Choices
- Database-driven with API for AI agent ingestion
- No admin interface - API-only management
- SQLite locally (PostgreSQL-ready for production)
- Max 5 articles per category (hard cap)
- Up to 3 supporting articles per main article (depth = 1)

## Architecture

### Database Schema (SQLite/PostgreSQL compatible)

```
digests
├── id (UUID)
├── edition_name
├── digest_date
├── recency_window_hours
├── status (draft/published/archived)
├── created_at / updated_at

articles
├── id (UUID)
├── digest_id (FK)
├── category
├── rank (1-5, display priority)
├── story_cluster_id
├── headline
├── summary
├── why_it_matters
├── watch_next
├── political_synthesis (nullable)
├── importance_score
├── is_political (boolean)
├── image_url (optional)
├── curated_by
├── created_at / updated_at

supporting_articles (depth = 1 only)
├── id (UUID)
├── parent_article_id (FK)
├── headline
├── summary
├── context_type (context/alternative/deep_dive)
├── source_name
├── source_url
├── image_url (optional)
├── created_at / updated_at

article_sources
├── id (UUID)
├── article_id (FK)
├── source_name
├── source_url
├── source_type (primary/supporting/reference)
├── created_at
```

### API Endpoints

**Digests:**
- `POST /api/digests` - Create new digest
- `GET /api/digests` - List digests
- `GET /api/digests/{id}` - Get digest with articles
- `GET /api/digests/date/{date}` - Get digest by date
- `PUT /api/digests/{id}` - Update digest
- `DELETE /api/digests/{id}` - Delete digest (cascades)

**Bulk Ingest (Main endpoint for AI agent):**
- `POST /api/articles/ingest` - Bulk ingest full digest

**Articles:**
- `GET /api/articles` - List with filters (category, date, digest_id)
- `POST /api/articles` - Create single article
- `GET /api/articles/{id}` - Get article with nested data
- `PUT /api/articles/{id}` - Update article
- `DELETE /api/articles/{id}` - Delete article (cascades)

**Supporting Articles:**
- `POST /api/articles/{id}/supporting` - Add supporting article
- `DELETE /api/supporting/{id}` - Remove supporting article

**Utility:**
- `GET /api/categories` - List valid categories

### Example Ingest Payload
```json
{
  "edition_name": "News Ledger",
  "digest_date": "2026-01-30",
  "recency_window_hours": 24,
  "articles": [
    {
      "category": "U.S.",
      "rank": 1,
      "story_cluster_id": "us-politics-001",
      "headline": "Senate Passes Infrastructure Bill",
      "summary": "...",
      "why_it_matters": "...",
      "watch_next": "...",
      "political_synthesis": "...",
      "importance_score": 0.95,
      "is_political": true,
      "image_url": "https://...",
      "curated_by": "AI News Agent",
      "supporting_articles": [
        {
          "headline": "Governors React",
          "summary": "...",
          "context_type": "context",
          "source_name": "Reuters",
          "source_url": "https://..."
        }
      ],
      "sources": [
        {"source_name": "Washington Post", "source_type": "primary"}
      ]
    }
  ]
}
```

## What's Been Implemented (April 2026)

### Backend
- SQLAlchemy async models (SQLite/PostgreSQL compatible)
- Full CRUD for digests, articles, supporting articles
- Bulk ingest endpoint with validation
- Cascade deletes
- Category validation (max 5 per category)
- Supporting article limit (max 3 per parent)

### Frontend
- Vintage newspaper UI with Playfair Display & Merriweather fonts
- Dynamic content from latest digest
- Category navigation with filtering
- Featured article with why_it_matters, watch_next sections
- Related coverage (supporting articles)
- Political synthesis display
- Sidebar with cross-category articles
- Animated news ticker

## For Local Deployment

1. Set DATABASE_URL in backend/.env:
   - SQLite: `sqlite+aiosqlite:///./news_ledger.db`
   - PostgreSQL: `postgresql+asyncpg://user:pass@localhost:5432/news_ledger`

2. Database tables auto-create on startup

3. Your AI agent sends POST to /api/articles/ingest with daily digest

## Prioritized Backlog
- P0: ✅ Database schema - DONE
- P0: ✅ Bulk ingest API - DONE
- P0: ✅ Frontend display - DONE
- P1: Article detail modal/page
- P2: Historical digest navigation
- P2: Search functionality

## Next Tasks
1. Add article detail view when clicking headlines
2. Add date picker to view historical digests
3. Consider adding authentication for write endpoints
