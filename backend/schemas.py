"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
from enum import Enum


# Enums
class DigestStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContextType(str, Enum):
    CONTEXT = "context"
    ALTERNATIVE = "alternative"
    DEEP_DIVE = "deep_dive"


class SourceType(str, Enum):
    PRIMARY = "primary"
    SUPPORTING = "supporting"
    REFERENCE = "reference"


# Category enum for validation
VALID_CATEGORIES = ["U.S.", "World", "Local", "Business", "Technology", "Entertainment", "Sports", "Science", "Health"]


# ============ Article Sources ============
class ArticleSourceBase(BaseModel):
    source_name: str
    source_url: Optional[str] = None
    source_type: SourceType = SourceType.PRIMARY


class ArticleSourceCreate(ArticleSourceBase):
    pass


class ArticleSourceResponse(ArticleSourceBase):
    id: UUID
    article_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ Supporting Articles ============
class SupportingArticleBase(BaseModel):
    headline: str
    summary: Optional[str] = None
    context_type: ContextType = ContextType.CONTEXT
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None


class SupportingArticleCreate(SupportingArticleBase):
    pass


class SupportingArticleResponse(SupportingArticleBase):
    id: UUID
    parent_article_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ Main Articles ============
class ArticleBase(BaseModel):
    category: str
    rank: int = Field(ge=1, le=5, description="Display priority 1-5, where 1 is highest")
    story_cluster_id: Optional[str] = None
    headline: str
    summary: Optional[str] = None
    why_it_matters: Optional[str] = None
    watch_next: Optional[str] = None
    political_synthesis: Optional[str] = None
    importance_score: float = 0.0
    is_political: bool = False
    image_url: Optional[str] = None
    curated_by: Optional[str] = None


class ArticleCreate(ArticleBase):
    supporting_articles: Optional[List[SupportingArticleCreate]] = []
    sources: Optional[List[ArticleSourceCreate]] = []


class ArticleUpdate(BaseModel):
    category: Optional[str] = None
    rank: Optional[int] = Field(default=None, ge=1, le=5)
    story_cluster_id: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    why_it_matters: Optional[str] = None
    watch_next: Optional[str] = None
    political_synthesis: Optional[str] = None
    importance_score: Optional[float] = None
    is_political: Optional[bool] = None
    image_url: Optional[str] = None
    curated_by: Optional[str] = None


class ArticleResponse(ArticleBase):
    id: UUID
    digest_id: UUID
    created_at: datetime
    updated_at: datetime
    supporting_articles: List[SupportingArticleResponse] = []
    sources: List[ArticleSourceResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ============ Digests ============
class DigestBase(BaseModel):
    edition_name: str = "News Ledger"
    digest_date: date
    recency_window_hours: int = 24
    status: DigestStatus = DigestStatus.DRAFT


class DigestCreate(DigestBase):
    articles: Optional[List[ArticleCreate]] = []


class DigestUpdate(BaseModel):
    edition_name: Optional[str] = None
    digest_date: Optional[date] = None
    recency_window_hours: Optional[int] = None
    status: Optional[DigestStatus] = None


class DigestResponse(DigestBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    articles: List[ArticleResponse] = []

    model_config = ConfigDict(from_attributes=True)


class DigestSummary(BaseModel):
    """Lightweight digest response without full article content"""
    id: UUID
    edition_name: str
    digest_date: date
    status: DigestStatus
    article_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ Bulk Ingest ============
class BulkIngestRequest(BaseModel):
    """
    Full digest ingest payload - what your agent will send
    """
    edition_name: str = "News Ledger"
    digest_date: date
    recency_window_hours: int = 24
    articles: List[ArticleCreate]


class BulkIngestResponse(BaseModel):
    digest_id: UUID
    edition_name: str
    digest_date: date
    articles_created: int
    supporting_articles_created: int
    sources_created: int


# ============ Query Params ============
class ArticleQueryParams(BaseModel):
    category: Optional[str] = None
    digest_date: Optional[date] = None
    digest_id: Optional[UUID] = None
    is_political: Optional[bool] = None
    limit: int = Field(default=5, le=50)
