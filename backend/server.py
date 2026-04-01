from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class Article(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    excerpt: str
    content: str
    category: str
    author: str
    image_url: str
    published_at: str
    is_featured: bool = False
    is_spotlight: bool = False

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Mock News Data
MOCK_ARTICLES = [
    # U.S. Articles
    {
        "id": "1",
        "title": "Your principles are living things",
        "excerpt": "How else could they be nourished, except by the extinction of the corresponding mental images?",
        "content": "Nearly a simple thing is alien to the man, ordered together in their places they together make up the very order of the universe. The wise man, self-sufficient as he is, still desires a friend (if only), for the purpose of practicing friendship.",
        "category": "U.S.",
        "author": "Marcus Aurelius",
        "image_url": "https://images.unsplash.com/photo-1703244551357-233a550c11f5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwyfHx2aW50YWdlJTIwY2l0eSUyMHN0cmVldCUyMGJsYWNrJTIwYW5kJTIwd2hpdGV8ZW58MHx8fHwxNzc1MDgyMTk0fDA&ixlib=rb-4.1.0&q=85",
        "published_at": "January 29, 2026",
        "is_featured": True,
        "is_spotlight": False
    },
    {
        "id": "2",
        "title": "You should take no action unwillingly",
        "excerpt": "Selfishly, unsatisfied or with conflicting motives. Do not dress up your imagination except lively.",
        "content": "A wise person should take no action unwillingly, selfishly, unsatisfied or with conflicting motives. Do not dress up your imagination except lively. The mind is everything; what you think, you become.",
        "category": "U.S.",
        "author": "Seneca",
        "image_url": "https://images.unsplash.com/photo-1580196923348-cffc38b93d84?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwxfHx2aW50YWdlJTIwY2l0eSUyMHN0cmVldCUyMGJsYWNrJTIwYW5kJTIwd2hpdGV8ZW58MHx8fHwxNzc1MDgyMTk0fDA&ixlib=rb-4.1.0&q=85",
        "published_at": "January 28, 2026",
        "is_featured": False,
        "is_spotlight": True
    },
    # World Articles
    {
        "id": "3",
        "title": "National Gallery to reopen with exhibition on Pieter Brueghel",
        "excerpt": "The exhibition will feature more than 10 paintings on display for the first time, highlighting the history of art famous faces.",
        "content": "The National Gallery is set to reopen with a groundbreaking exhibition featuring the works of Pieter Brueghel. The exhibition will feature more than 10 paintings on display for the first time, highlighting the history of art's most famous faces, from George Bernard Shaw to Vivien Leigh, John Gielgud to Princess Margaret.",
        "category": "World",
        "author": "Ellie Barnes",
        "image_url": "https://images.unsplash.com/photo-1622835276155-2681286a8321?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NTZ8MHwxfHNlYXJjaHwzfHxibGFjayUyMGFuZCUyMHdoaXRlJTIwdmludGFnZSUyMG5ld3N8ZW58MHx8fHwxNzc1MDgyMTgyfDA&ixlib=rb-4.1.0&q=85",
        "published_at": "January 27, 2026",
        "is_featured": False,
        "is_spotlight": False
    },
    {
        "id": "4",
        "title": "Five key Renaissance Paintings",
        "excerpt": "A masterful collection of art that defined an era and continues to influence modern creativity.",
        "content": "The Renaissance period produced some of the most influential artworks in human history. From Leonardo da Vinci's Mona Lisa to Michelangelo's Sistine Chapel ceiling, these masterpieces continue to inspire artists and art lovers worldwide.",
        "category": "World",
        "author": "Art Correspondent",
        "image_url": "https://images.pexels.com/photos/16461387/pexels-photo-16461387.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "published_at": "January 26, 2026",
        "is_featured": False,
        "is_spotlight": False
    },
    # Local Articles
    {
        "id": "5",
        "title": "Story Told by the Church Beadle",
        "excerpt": "Frank Bigwinovski was innocently here this special sort of path in the normally absolute looking the same foregoing again.",
        "content": "The church beadle shared an extraordinary tale that has captivated the local community. Frank Bigwinovski's story reveals the hidden depths of our neighborhood's rich history and the remarkable characters who have shaped it over generations.",
        "category": "Local",
        "author": "Local Reporter",
        "image_url": "https://images.unsplash.com/photo-1703244549157-6cb7386abc68?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwzfHx2aW50YWdlJTIwY2l0eSUyMHN0cmVldCUyMGJsYWNrJTIwYW5kJTIwd2hpdGV8ZW58MHx8fHwxNzc1MDgyMTk0fDA&ixlib=rb-4.1.0&q=85",
        "published_at": "January 25, 2026",
        "is_featured": False,
        "is_spotlight": False
    },
    {
        "id": "6",
        "title": "The Last Day before Christmas",
        "excerpt": "A white, clear night came. The stars popped out. The Chapel/mass rose majestically in the sky to greet the good people.",
        "content": "As the community gathered for the last day before Christmas, the atmosphere was filled with anticipation and joy. The white, clear night came with stars popping out across the sky, and the chapel rose majestically to greet the good people of the town.",
        "category": "Local",
        "author": "Community Editor",
        "image_url": "https://images.pexels.com/photos/15935275/pexels-photo-15935275.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "published_at": "January 24, 2026",
        "is_featured": False,
        "is_spotlight": False
    },
    # Business Articles
    {
        "id": "7",
        "title": "Market indicators show promising growth",
        "excerpt": "Analysts predict continued economic expansion as key sectors demonstrate resilience in challenging times.",
        "content": "Economic indicators are pointing towards sustained growth across multiple sectors. Analysts have expressed optimism about the market's trajectory, citing strong performance in technology and manufacturing as key drivers of the expansion.",
        "category": "Business",
        "author": "Financial Desk",
        "image_url": "https://images.unsplash.com/photo-1628564120851-b76dfd932d2f?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHw0fHx2aW50YWdlJTIwY2l0eSUyMHN0cmVldCUyMGJsYWNrJTIwYW5kJTIwd2hpdGV8ZW58MHx8fHwxNzc1MDgyMTk0fDA&ixlib=rb-4.1.0&q=85",
        "published_at": "January 23, 2026",
        "is_featured": False,
        "is_spotlight": False
    },
    # Technology Articles
    {
        "id": "8",
        "title": "And what you dictated your heart to style (or use) is by no means between",
        "excerpt": "A wise person should not seek more to get in real local house is much better.",
        "content": "Technology continues to reshape how we live and work. The latest innovations in artificial intelligence and machine learning are creating unprecedented opportunities for businesses and individuals alike to transform their approaches to problem-solving.",
        "category": "Technology",
        "author": "Robert Woodcroft",
        "image_url": "https://images.unsplash.com/photo-1759405185537-6972d439a261?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NTZ8MHwxfHNlYXJjaHwyfHxibGFjayUyMGFuZCUyMHdoaXRlJTIwdmludGFnZSUyMG5ld3N8ZW58MHx8fHwxNzc1MDgyMTgyfDA&ixlib=rb-4.1.0&q=85",
        "published_at": "January 22, 2026",
        "is_featured": False,
        "is_spotlight": False
    },
    {
        "id": "9",
        "title": "All dispropor-tionate you see, but it still alphaism do shrunk your style more it",
        "excerpt": "If It seemed to be but for I had to out today's why any rules rules of answer.",
        "content": "The digital transformation continues at an unprecedented pace. Companies worldwide are investing heavily in new technologies to stay competitive and meet the evolving demands of their customers in an increasingly connected world.",
        "category": "Technology",
        "author": "Bella Rosalie Wolf",
        "image_url": "https://images.unsplash.com/photo-1713429901232-55af72e11af8?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjY2NzV8MHwxfHNlYXJjaHwyfHxjbGFzc2ljJTIwYmxhY2slMjBhbmQlMjB3aGl0ZSUyMHNwb3J0c3xlbnwwfHx8fDE3NzUwODIxOTR8MA&ixlib=rb-4.1.0&q=85",
        "published_at": "January 21, 2026",
        "is_featured": False,
        "is_spotlight": False
    },
    # Entertainment Articles
    {
        "id": "10",
        "title": "Noise and Thunder at the end of Kiev",
        "excerpt": "Captain parallel in celebrating his son's wedding. Many people about to our and, home will she may like to drink.",
        "content": "The entertainment world is buzzing with excitement as new productions premiere across the globe. Critics and audiences alike are praising the innovative approaches to storytelling that are redefining the industry.",
        "category": "Entertainment",
        "author": "Arts Critic",
        "image_url": "https://images.unsplash.com/photo-1758405392922-569359b88a9b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjY2NzV8MHwxfHNlYXJjaHw0fHxjbGFzc2ljJTIwYmxhY2slMjBhbmQlMjB3aGl0ZSUyMHNwb3J0c3xlbnwwfHx8fDE3NzUwODIxOTR8MA&ixlib=rb-4.1.0&q=85",
        "published_at": "January 20, 2026",
        "is_featured": False,
        "is_spotlight": False
    },
    # Sports Articles
    {
        "id": "11",
        "title": "Championship finals draw record crowds",
        "excerpt": "The athletic competition reached new heights as spectators gathered to witness historic performances.",
        "content": "Sports enthusiasts from around the world gathered to witness what many are calling the most exciting championship finals in decades. Athletes pushed their limits, delivering performances that will be remembered for generations.",
        "category": "Sports",
        "author": "Sports Desk",
        "image_url": "https://images.unsplash.com/photo-1758405392922-569359b88a9b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjY2NzV8MHwxfHNlYXJjaHw0fHxjbGFzc2ljJTIwYmxhY2slMjBhbmQlMjB3aGl0ZSUyMHNwb3J0c3xlbnwwfHx8fDE3NzUwODIxOTR8MA&ixlib=rb-4.1.0&q=85",
        "published_at": "January 19, 2026",
        "is_featured": False,
        "is_spotlight": False
    },
    # Science Articles
    {
        "id": "12",
        "title": "Consistently net your readiest impression - can't we sub-headed it one use",
        "excerpt": "Scientific breakthroughs continue to reshape our understanding of the natural world.",
        "content": "Researchers have made groundbreaking discoveries that promise to transform our understanding of the universe. These findings open new avenues for exploration and technological advancement that could benefit humanity for generations to come.",
        "category": "Science",
        "author": "Alistia Marcha",
        "image_url": "https://images.unsplash.com/photo-1622835276155-2681286a8321?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1NTZ8MHwxfHNlYXJjaHwzfHxibGFjayUyMGFuZCUyMHdoaXRlJTIwdmludGFnZSUyMG5ld3N8ZW58MHx8fHwxNzc1MDgyMTgyfDA&ixlib=rb-4.1.0&q=85",
        "published_at": "January 18, 2026",
        "is_featured": False,
        "is_spotlight": False
    },
    # Health Articles
    {
        "id": "13",
        "title": "If you've got a formidable drive, that is constantly to our will cannot",
        "excerpt": "Health experts share insights on maintaining wellness in modern times.",
        "content": "Medical professionals are sharing new insights into maintaining optimal health in today's fast-paced world. Their recommendations emphasize the importance of balance, mindfulness, and preventive care in achieving long-term wellness.",
        "category": "Health",
        "author": "Joshua B. Markus",
        "image_url": "https://images.unsplash.com/photo-1713429901232-55af72e11af8?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjY2NzV8MHwxfHNlYXJjaHwyfHxjbGFzc2ljJTIwYmxhY2slMjBhbmQlMjB3aGl0ZSUyMHNwb3J0c3xlbnwwfHx8fDE3NzUwODIxOTR8MA&ixlib=rb-4.1.0&q=85",
        "published_at": "January 17, 2026",
        "is_featured": False,
        "is_spotlight": False
    },
    # Additional Articles for variety
    {
        "id": "14",
        "title": "Eduardo Halt breaks new ground in literary criticism",
        "excerpt": "The acclaimed author presents a fresh perspective on classical literature interpretation.",
        "content": "Eduardo Halt's latest work challenges conventional approaches to literary criticism, offering readers a new lens through which to examine classic texts. His methodology has sparked lively debate among scholars and enthusiasts alike.",
        "category": "Entertainment",
        "author": "Eduardo Halt",
        "image_url": "https://images.pexels.com/photos/16461387/pexels-photo-16461387.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "published_at": "January 16, 2026",
        "is_featured": False,
        "is_spotlight": False
    },
    {
        "id": "15",
        "title": "Lucie Antonio Santos shares wisdom on personal growth",
        "excerpt": "The renowned philosopher discusses the path to self-improvement and inner peace.",
        "content": "In an exclusive interview, Lucie Antonio Santos reflects on decades of philosophical inquiry and personal development. Her insights offer guidance for those seeking meaning and fulfillment in an increasingly complex world.",
        "category": "Health",
        "author": "Lucie Antonio Santos",
        "image_url": "https://images.unsplash.com/photo-1580196923348-cffc38b93d84?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwxfHx2aW50YWdlJTIwY2l0eSUyMHN0cmVldCUyMGJsYWNrJTIwYW5kJTIwd2hpdGV8ZW58MHx8fHwxNzc1MDgyMTk0fDA&ixlib=rb-4.1.0&q=85",
        "published_at": "January 15, 2026",
        "is_featured": False,
        "is_spotlight": False
    },
    {
        "id": "16",
        "title": "David Hughes explores the future of sustainable business",
        "excerpt": "Industry leader outlines strategies for environmentally responsible commerce.",
        "content": "David Hughes presents a compelling vision for the future of business that prioritizes environmental sustainability without sacrificing profitability. His framework offers practical steps for companies of all sizes to reduce their ecological footprint.",
        "category": "Business",
        "author": "David Hughes",
        "image_url": "https://images.unsplash.com/photo-1703244549157-6cb7386abc68?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwzfHx2aW50YWdlJTIwY2l0eSUyMHN0cmVldCUyMGJsYWNrJTIwYW5kJTIwd2hpdGV8ZW58MHx8fHwxNzc1MDgyMTk0fDA&ixlib=rb-4.1.0&q=85",
        "published_at": "January 14, 2026",
        "is_featured": False,
        "is_spotlight": False
    }
]

CATEGORIES = ["U.S.", "World", "Local", "Business", "Technology", "Entertainment", "Sports", "Science", "Health"]

# API Routes
@api_router.get("/")
async def root():
    return {"message": "News Ledger API"}

@api_router.get("/articles", response_model=List[Article])
async def get_articles(category: Optional[str] = None):
    """Get all articles, optionally filtered by category"""
    articles = MOCK_ARTICLES
    if category:
        articles = [a for a in articles if a["category"] == category]
    return [Article(**a) for a in articles]

@api_router.get("/articles/featured", response_model=Article)
async def get_featured_article():
    """Get the main featured article"""
    featured = next((a for a in MOCK_ARTICLES if a["is_featured"]), MOCK_ARTICLES[0])
    return Article(**featured)

@api_router.get("/articles/spotlight", response_model=Article)
async def get_spotlight_article():
    """Get the spotlight article"""
    spotlight = next((a for a in MOCK_ARTICLES if a["is_spotlight"]), MOCK_ARTICLES[1])
    return Article(**spotlight)

@api_router.get("/articles/sidebar", response_model=List[Article])
async def get_sidebar_articles():
    """Get articles for the sidebar"""
    sidebar_articles = [a for a in MOCK_ARTICLES if not a["is_featured"] and not a["is_spotlight"]][:5]
    return [Article(**a) for a in sidebar_articles]

@api_router.get("/articles/bottom", response_model=List[Article])
async def get_bottom_articles():
    """Get articles for the bottom section"""
    bottom_articles = [a for a in MOCK_ARTICLES if not a["is_featured"] and not a["is_spotlight"]][3:7]
    return [Article(**a) for a in bottom_articles]

@api_router.get("/articles/opinions", response_model=List[Article])
async def get_opinion_articles():
    """Get opinion articles for the grid"""
    opinion_articles = MOCK_ARTICLES[7:10]
    return [Article(**a) for a in opinion_articles]

@api_router.get("/articles/{article_id}", response_model=Article)
async def get_article(article_id: str):
    """Get a specific article by ID"""
    article = next((a for a in MOCK_ARTICLES if a["id"] == article_id), None)
    if not article:
        return {"error": "Article not found"}
    return Article(**article)

@api_router.get("/categories")
async def get_categories():
    """Get all available categories"""
    return {"categories": CATEGORIES}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
