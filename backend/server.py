from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from sqlalchemy.orm import selectinload
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, date

# Local imports
from database import get_db, init_db, close_db
from models import Digest, Article, SupportingArticle, ArticleSource
from schemas import (
    DigestCreate, DigestUpdate, DigestResponse, DigestSummary,
    ArticleCreate, ArticleUpdate, ArticleResponse,
    SupportingArticleCreate, SupportingArticleResponse,
    ArticleSourceCreate, ArticleSourceResponse,
    BulkIngestRequest, BulkIngestResponse,
    VALID_CATEGORIES
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (for legacy status checks)
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
mongo_client = AsyncIOMotorClient(mongo_url)
mongo_db = mongo_client[os.environ.get('DB_NAME', 'news_ledger')]

# Create the main app
app = FastAPI(title="News Ledger API", version="2.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ============ Pydantic Models for Legacy ============
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str


# ============ Root & Health ============
@api_router.get("/")
async def root():
    return {"message": "News Ledger API v2.0", "status": "healthy"}


@api_router.get("/categories")
async def get_categories():
    """Get all available categories"""
    return {"categories": VALID_CATEGORIES}


# ============ Digest Endpoints ============
@api_router.post("/digests", response_model=DigestResponse)
async def create_digest(digest_data: DigestCreate, db: AsyncSession = Depends(get_db)):
    """Create a new digest (daily edition)"""
    # Check if digest already exists for this date
    existing = await db.execute(
        select(Digest).where(
            and_(
                Digest.digest_date == digest_data.digest_date,
                Digest.edition_name == digest_data.edition_name
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Digest for {digest_data.digest_date} already exists")
    
    # Create digest
    digest = Digest(
        edition_name=digest_data.edition_name,
        digest_date=digest_data.digest_date,
        recency_window_hours=digest_data.recency_window_hours,
        status=digest_data.status.value
    )
    db.add(digest)
    
    # Add articles if provided
    for article_data in digest_data.articles:
        article = Article(
            digest_id=digest.id,
            **article_data.model_dump(exclude={'supporting_articles', 'sources'})
        )
        db.add(article)
        
        # Add supporting articles
        for sa_data in article_data.supporting_articles or []:
            sa = SupportingArticle(parent_article_id=article.id, **sa_data.model_dump())
            db.add(sa)
        
        # Add sources
        for source_data in article_data.sources or []:
            source = ArticleSource(article_id=article.id, **source_data.model_dump())
            db.add(source)
    
    await db.commit()
    await db.refresh(digest)
    
    # Reload with relationships
    result = await db.execute(
        select(Digest)
        .options(
            selectinload(Digest.articles)
            .selectinload(Article.supporting_articles),
            selectinload(Digest.articles)
            .selectinload(Article.sources)
        )
        .where(Digest.id == digest.id)
    )
    return result.scalar_one()


@api_router.get("/digests", response_model=List[DigestSummary])
async def list_digests(
    status: Optional[str] = None,
    limit: int = Query(default=10, le=50),
    db: AsyncSession = Depends(get_db)
):
    """List all digests with summary info"""
    query = select(Digest).order_by(Digest.digest_date.desc()).limit(limit)
    if status:
        query = query.where(Digest.status == status)
    
    result = await db.execute(query)
    digests = result.scalars().all()
    
    # Get article counts
    summaries = []
    for digest in digests:
        count_result = await db.execute(
            select(func.count(Article.id)).where(Article.digest_id == digest.id)
        )
        article_count = count_result.scalar()
        summaries.append(DigestSummary(
            id=digest.id,
            edition_name=digest.edition_name,
            digest_date=digest.digest_date,
            status=digest.status,
            article_count=article_count,
            created_at=digest.created_at
        ))
    
    return summaries


@api_router.get("/digests/{digest_id}", response_model=DigestResponse)
async def get_digest(digest_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific digest with all articles"""
    result = await db.execute(
        select(Digest)
        .options(
            selectinload(Digest.articles)
            .selectinload(Article.supporting_articles),
            selectinload(Digest.articles)
            .selectinload(Article.sources)
        )
        .where(Digest.id == digest_id)
    )
    digest = result.scalar_one_or_none()
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    return digest


@api_router.get("/digests/date/{digest_date}", response_model=DigestResponse)
async def get_digest_by_date(digest_date: date, db: AsyncSession = Depends(get_db)):
    """Get digest for a specific date"""
    result = await db.execute(
        select(Digest)
        .options(
            selectinload(Digest.articles)
            .selectinload(Article.supporting_articles),
            selectinload(Digest.articles)
            .selectinload(Article.sources)
        )
        .where(Digest.digest_date == digest_date)
    )
    digest = result.scalar_one_or_none()
    if not digest:
        raise HTTPException(status_code=404, detail=f"No digest found for {digest_date}")
    return digest


@api_router.put("/digests/{digest_id}", response_model=DigestResponse)
async def update_digest(digest_id: uuid.UUID, digest_data: DigestUpdate, db: AsyncSession = Depends(get_db)):
    """Update digest metadata"""
    result = await db.execute(select(Digest).where(Digest.id == digest_id))
    digest = result.scalar_one_or_none()
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    
    update_data = digest_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(digest, key, value.value if hasattr(value, 'value') else value)
    
    await db.commit()
    await db.refresh(digest)
    return digest


@api_router.delete("/digests/{digest_id}")
async def delete_digest(digest_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete a digest and all its articles (cascade)"""
    result = await db.execute(select(Digest).where(Digest.id == digest_id))
    digest = result.scalar_one_or_none()
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
    
    await db.delete(digest)
    await db.commit()
    return {"message": "Digest deleted", "id": str(digest_id)}


# ============ Bulk Ingest Endpoint ============
@api_router.post("/articles/ingest", response_model=BulkIngestResponse)
async def bulk_ingest(data: BulkIngestRequest, db: AsyncSession = Depends(get_db)):
    """
    Bulk ingest a full digest - main endpoint for your agent
    Creates or replaces digest for the given date
    """
    # Check for existing digest and delete if exists (replace mode)
    existing = await db.execute(
        select(Digest).where(
            and_(
                Digest.digest_date == data.digest_date,
                Digest.edition_name == data.edition_name
            )
        )
    )
    existing_digest = existing.scalar_one_or_none()
    if existing_digest:
        await db.delete(existing_digest)
        await db.flush()
    
    # Validate article counts per category (max 5)
    category_counts = {}
    for article in data.articles:
        if article.category not in VALID_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Invalid category: {article.category}")
        category_counts[article.category] = category_counts.get(article.category, 0) + 1
        if category_counts[article.category] > 5:
            raise HTTPException(status_code=400, detail=f"Max 5 articles per category. {article.category} has {category_counts[article.category]}")
    
    # Create new digest
    digest = Digest(
        edition_name=data.edition_name,
        digest_date=data.digest_date,
        recency_window_hours=data.recency_window_hours,
        status="published"
    )
    db.add(digest)
    await db.flush()  # Get digest.id
    
    articles_created = 0
    supporting_created = 0
    sources_created = 0
    
    for article_data in data.articles:
        article = Article(
            digest_id=digest.id,
            category=article_data.category,
            rank=article_data.rank,
            story_cluster_id=article_data.story_cluster_id,
            headline=article_data.headline,
            summary=article_data.summary,
            why_it_matters=article_data.why_it_matters,
            watch_next=article_data.watch_next,
            political_synthesis=article_data.political_synthesis,
            importance_score=article_data.importance_score,
            is_political=article_data.is_political,
            image_url=article_data.image_url,
            curated_by=article_data.curated_by
        )
        db.add(article)
        await db.flush()  # Get article.id
        articles_created += 1
        
        # Add supporting articles (max 3)
        for sa_data in (article_data.supporting_articles or [])[:3]:
            sa = SupportingArticle(
                parent_article_id=article.id,
                headline=sa_data.headline,
                summary=sa_data.summary,
                context_type=sa_data.context_type.value,
                source_name=sa_data.source_name,
                source_url=sa_data.source_url,
                image_url=sa_data.image_url
            )
            db.add(sa)
            supporting_created += 1
        
        # Add sources
        for source_data in (article_data.sources or []):
            source = ArticleSource(
                article_id=article.id,
                source_name=source_data.source_name,
                source_url=source_data.source_url,
                source_type=source_data.source_type.value
            )
            db.add(source)
            sources_created += 1
    
    await db.commit()
    
    return BulkIngestResponse(
        digest_id=digest.id,
        edition_name=digest.edition_name,
        digest_date=digest.digest_date,
        articles_created=articles_created,
        supporting_articles_created=supporting_created,
        sources_created=sources_created
    )


# ============ Article Endpoints ============
@api_router.get("/articles", response_model=List[ArticleResponse])
async def get_articles(
    category: Optional[str] = None,
    digest_date: Optional[date] = None,
    digest_id: Optional[uuid.UUID] = None,
    is_political: Optional[bool] = None,
    limit: int = Query(default=5, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get articles with optional filters"""
    query = select(Article).options(
        selectinload(Article.supporting_articles),
        selectinload(Article.sources)
    ).order_by(Article.rank)
    
    if digest_id:
        query = query.where(Article.digest_id == digest_id)
    elif digest_date:
        # Join with digest to filter by date
        query = query.join(Digest).where(Digest.digest_date == digest_date)
    
    if category:
        if category not in VALID_CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        query = query.where(Article.category == category)
    
    if is_political is not None:
        query = query.where(Article.is_political == is_political)
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@api_router.post("/articles", response_model=ArticleResponse)
async def create_article(
    article_data: ArticleCreate,
    digest_id: uuid.UUID = Query(..., description="Digest ID to add article to"),
    db: AsyncSession = Depends(get_db)
):
    """Create a single article within a digest"""
    # Verify digest exists
    digest_result = await db.execute(select(Digest).where(Digest.id == digest_id))
    if not digest_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Digest not found")
    
    # Check category article count
    count_result = await db.execute(
        select(func.count(Article.id)).where(
            and_(Article.digest_id == digest_id, Article.category == article_data.category)
        )
    )
    if count_result.scalar() >= 5:
        raise HTTPException(status_code=400, detail=f"Max 5 articles per category in digest")
    
    article = Article(
        digest_id=digest_id,
        **article_data.model_dump(exclude={'supporting_articles', 'sources'})
    )
    db.add(article)
    await db.flush()
    
    for sa_data in article_data.supporting_articles or []:
        sa = SupportingArticle(parent_article_id=article.id, **sa_data.model_dump())
        db.add(sa)
    
    for source_data in article_data.sources or []:
        source = ArticleSource(article_id=article.id, **source_data.model_dump())
        db.add(source)
    
    await db.commit()
    
    # Reload with relationships
    result = await db.execute(
        select(Article)
        .options(selectinload(Article.supporting_articles), selectinload(Article.sources))
        .where(Article.id == article.id)
    )
    return result.scalar_one()


@api_router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific article with supporting articles and sources"""
    result = await db.execute(
        select(Article)
        .options(selectinload(Article.supporting_articles), selectinload(Article.sources))
        .where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@api_router.put("/articles/{article_id}", response_model=ArticleResponse)
async def update_article(article_id: uuid.UUID, article_data: ArticleUpdate, db: AsyncSession = Depends(get_db)):
    """Update an article"""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    update_data = article_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(article, key, value)
    
    await db.commit()
    await db.refresh(article)
    return article


@api_router.delete("/articles/{article_id}")
async def delete_article(article_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete an article (cascades to supporting articles and sources)"""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    await db.delete(article)
    await db.commit()
    return {"message": "Article deleted", "id": str(article_id)}


# ============ Supporting Article Endpoints ============
@api_router.post("/articles/{article_id}/supporting", response_model=SupportingArticleResponse)
async def add_supporting_article(
    article_id: uuid.UUID,
    sa_data: SupportingArticleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a supporting article to a main article (max 3)"""
    # Verify parent article exists
    article_result = await db.execute(select(Article).where(Article.id == article_id))
    if not article_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Parent article not found")
    
    # Check supporting article count
    count_result = await db.execute(
        select(func.count(SupportingArticle.id)).where(SupportingArticle.parent_article_id == article_id)
    )
    if count_result.scalar() >= 3:
        raise HTTPException(status_code=400, detail="Max 3 supporting articles per main article")
    
    sa = SupportingArticle(parent_article_id=article_id, **sa_data.model_dump())
    db.add(sa)
    await db.commit()
    await db.refresh(sa)
    return sa


@api_router.delete("/supporting/{supporting_id}")
async def delete_supporting_article(supporting_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete a supporting article"""
    result = await db.execute(select(SupportingArticle).where(SupportingArticle.id == supporting_id))
    sa = result.scalar_one_or_none()
    if not sa:
        raise HTTPException(status_code=404, detail="Supporting article not found")
    
    await db.delete(sa)
    await db.commit()
    return {"message": "Supporting article deleted", "id": str(supporting_id)}


# ============ Legacy Status Endpoints (MongoDB) ============
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    _ = await mongo_db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await mongo_db.status_checks.find({}, {"_id": 0}).to_list(1000)
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    return status_checks


# ============ App Setup ============
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    try:
        await init_db()
        logger.info("PostgreSQL database initialized")
    except Exception as e:
        logger.warning(f"PostgreSQL not available, some features disabled: {e}")


@app.on_event("shutdown")
async def shutdown():
    """Close connections on shutdown"""
    mongo_client.close()
    await close_db()
