"""
Database models for News Ledger
SQLAlchemy schema - supports SQLite and PostgreSQL
"""
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, Date, ForeignKey, Enum, create_engine, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()


# Custom UUID type that works with SQLite
class GUID(TypeDecorator):
    """Platform-independent GUID type - uses String for SQLite, native UUID for PostgreSQL"""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return uuid.UUID(value)
        return value


class DigestStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContextType(str, enum.Enum):
    CONTEXT = "context"
    ALTERNATIVE = "alternative"
    DEEP_DIVE = "deep_dive"


class SourceType(str, enum.Enum):
    PRIMARY = "primary"
    SUPPORTING = "supporting"
    REFERENCE = "reference"


class Digest(Base):
    """
    Top-level digest table - represents a daily edition
    """
    __tablename__ = "digests"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    edition_name = Column(String(255), nullable=False, default="News Ledger")
    digest_date = Column(Date, nullable=False)
    recency_window_hours = Column(Integer, default=24)
    status = Column(String(20), default=DigestStatus.DRAFT.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    articles = relationship("Article", back_populates="digest", cascade="all, delete-orphan")


class Article(Base):
    """
    Main articles table - 5 per category per digest
    """
    __tablename__ = "articles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    digest_id = Column(GUID(), ForeignKey("digests.id", ondelete="CASCADE"), nullable=False)
    
    # Content fields
    category = Column(String(50), nullable=False)
    rank = Column(Integer, nullable=False)  # 1-5, display order (1 = highest priority)
    story_cluster_id = Column(String(255), nullable=True)  # From clustering/deduplication
    
    headline = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    why_it_matters = Column(Text, nullable=True)
    watch_next = Column(Text, nullable=True)
    political_synthesis = Column(Text, nullable=True)
    
    # Metadata
    importance_score = Column(Float, default=0.0)
    is_political = Column(Boolean, default=False)
    image_url = Column(Text, nullable=True)
    curated_by = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    digest = relationship("Digest", back_populates="articles")
    supporting_articles = relationship("SupportingArticle", back_populates="parent_article", cascade="all, delete-orphan")
    sources = relationship("ArticleSource", back_populates="article", cascade="all, delete-orphan")


class SupportingArticle(Base):
    """
    Supporting articles - up to 3 per main article (depth = 1)
    Provides context, alternative reporting, or deeper understanding
    """
    __tablename__ = "supporting_articles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    parent_article_id = Column(GUID(), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    
    # Content fields
    headline = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    context_type = Column(String(20), default=ContextType.CONTEXT.value)  # context, alternative, deep_dive
    
    # Source info
    source_name = Column(String(255), nullable=True)
    source_url = Column(Text, nullable=True)
    
    # Optional image
    image_url = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    parent_article = relationship("Article", back_populates="supporting_articles")


class ArticleSource(Base):
    """
    Sources for main articles
    """
    __tablename__ = "article_sources"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    article_id = Column(GUID(), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    
    source_name = Column(String(255), nullable=False)
    source_url = Column(Text, nullable=True)
    source_type = Column(String(20), default=SourceType.PRIMARY.value)  # primary, supporting, reference
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    article = relationship("Article", back_populates="sources")
