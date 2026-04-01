# News Ledger - Product Requirements Document

## Original Problem Statement
Create a news dashboard called "News Ledger" with the following categories:
- U.S., World, Local, Business, Technology, Entertainment, Sports, Science, Health

Design should follow a classic vintage newspaper style aesthetic.

## User Choices
- Mock/sample news data for demonstration
- No additional features (search, bookmarks, dark mode)
- Follow exact vintage newspaper style from reference image

## Architecture
- **Frontend**: React with Tailwind CSS, vintage newspaper styling
- **Backend**: FastAPI with mock article data
- **Database**: MongoDB (used for status checks, articles are mock data)

## What's Been Implemented (January 2026)

### Backend
- `/api/categories` - Returns all 9 news categories
- `/api/articles` - Returns all articles (optional category filter)
- `/api/articles/featured` - Returns main featured article
- `/api/articles/spotlight` - Returns spotlight article
- `/api/articles/sidebar` - Returns sidebar articles
- `/api/articles/bottom` - Returns bottom section articles
- `/api/articles/opinions` - Returns opinion articles
- `/api/articles/{id}` - Returns specific article

### Frontend
- Masthead with "News Ledger" title and date
- Category navigation sidebar (9 categories)
- Featured article section with vintage-filtered image
- Spotlight article section
- "NO. 01" issue number display
- Opinions grid section
- Right sidebar with featured articles thumbnails
- Bottom section with 4 article cards
- Animated news ticker at bottom

### Design
- Classic newspaper typography (Playfair Display, Merriweather, Oswald)
- Off-white background (#F4F1EA)
- Black borders and text (#111111)
- Grayscale sepia-filtered images
- Sharp corners (no rounded edges)
- Column-based layout mimicking print newspapers

## User Personas
- News readers who appreciate classic editorial design
- Users seeking a distraction-free reading experience
- Design enthusiasts who value typographic excellence

## Prioritized Backlog
- P0: ✅ Core dashboard layout - DONE
- P0: ✅ Category navigation - DONE
- P0: ✅ Article display sections - DONE
- P1: Article detail view/modal
- P1: Category filtering functionality
- P2: Search functionality
- P2: Bookmarking articles
- P3: User preferences/settings

## Next Tasks
1. Implement category filtering (show articles by selected category)
2. Add article detail modal/page
3. Connect to real news API (if desired)
