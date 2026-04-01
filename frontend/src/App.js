import { useState, useEffect, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Categories for navigation
const CATEGORIES = ["U.S.", "World", "Local", "Business", "Technology", "Entertainment", "Sports", "Science", "Health"];

// Fallback mock data when no articles exist in database
const MOCK_ARTICLES = {
  "U.S.": [
    {
      id: "mock-1",
      headline: "Your principles are living things",
      summary: "How else could they be nourished, except by the extinction of the corresponding mental images?",
      why_it_matters: "Nearly a simple thing is alien to the man, ordered together in their places they together make up the very order of the universe.",
      curated_by: "Marcus Aurelius",
      image_url: "https://images.unsplash.com/photo-1703244551357-233a550c11f5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDJ8MHwxfHNlYXJjaHwyfHx2aW50YWdlJTIwY2l0eSUyMHN0cmVldCUyMGJsYWNrJTIwYW5kJTIwd2hpdGV8ZW58MHx8fHwxNzc1MDgyMTk0fDA&ixlib=rb-4.1.0&q=85",
      rank: 1,
      supporting_articles: [
        { headline: "The wise man, self-sufficient as he is, still desires a friend", summary: "For the purpose of practicing friendship.", source_name: "Lucius Antonio Santos", context_type: "context" }
      ]
    }
  ],
  "World": [
    {
      id: "mock-2",
      headline: "National Gallery to reopen with exhibition on Pieter Brueghel",
      summary: "The exhibition will feature more than 10 paintings on display for the first time.",
      why_it_matters: "Highlighting the history of art's famous faces, from George Bernard Shaw to Vivien Leigh.",
      curated_by: "Ellie Barnes",
      image_url: "https://images.unsplash.com/photo-1622835276155-2681286a8321",
      rank: 1,
      supporting_articles: []
    }
  ]
};

function App() {
  const [selectedCategory, setSelectedCategory] = useState("U.S.");
  const [currentDigest, setCurrentDigest] = useState(null);
  const [articles, setArticles] = useState([]);
  const [allArticles, setAllArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [usingMockData, setUsingMockData] = useState(false);

  // Get current date formatted
  const getCurrentDate = () => {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return new Date().toLocaleDateString('en-US', options);
  };

  // Fetch latest digest on mount
  useEffect(() => {
    const fetchDigest = async () => {
      try {
        setLoading(true);
        
        // Try to get the most recent digest
        const digestsResponse = await axios.get(`${API}/digests?limit=1`);
        
        if (digestsResponse.data && digestsResponse.data.length > 0) {
          const latestDigest = digestsResponse.data[0];
          
          // Fetch full digest with articles
          const fullDigestResponse = await axios.get(`${API}/digests/${latestDigest.id}`);
          setCurrentDigest(fullDigestResponse.data);
          setAllArticles(fullDigestResponse.data.articles || []);
          setUsingMockData(false);
        } else {
          // No digests exist, use mock data
          console.log("No digests found, using mock data");
          setUsingMockData(true);
          setAllArticles([]);
        }
      } catch (error) {
        console.error("Error fetching digest:", error);
        setUsingMockData(true);
        setAllArticles([]);
      } finally {
        setLoading(false);
      }
    };

    fetchDigest();
  }, []);

  // Filter articles by category
  useEffect(() => {
    if (usingMockData) {
      setArticles(MOCK_ARTICLES[selectedCategory] || []);
    } else {
      const filtered = allArticles
        .filter(a => a.category === selectedCategory)
        .sort((a, b) => a.rank - b.rank);
      setArticles(filtered);
    }
  }, [selectedCategory, allArticles, usingMockData]);

  // Get featured article (rank 1 of selected category)
  const featuredArticle = articles.find(a => a.rank === 1) || articles[0];
  
  // Get other articles for the category
  const otherArticles = articles.filter(a => a.id !== featuredArticle?.id);
  
  // Get articles from other categories for sidebar
  const sidebarArticles = allArticles
    .filter(a => a.category !== selectedCategory)
    .slice(0, 5);
  
  // Get bottom articles (different categories)
  const bottomArticles = allArticles
    .filter(a => a.category !== selectedCategory)
    .slice(0, 4);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F4F1EA] flex items-center justify-center">
        <div className="font-headline text-2xl text-[#111111]">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F4F1EA] pb-12" data-testid="news-ledger-app">
      {/* Masthead Header */}
      <header className="text-center py-6 border-b-4 border-t-8 border-[#111111] mb-0" data-testid="masthead">
        <h1 className="masthead-title text-5xl sm:text-6xl md:text-7xl lg:text-8xl text-[#111111] mb-2">
          News Ledger
        </h1>
        <p className="font-label text-xs tracking-widest text-[#4A4A4A] uppercase">
          {currentDigest ? new Date(currentDigest.digest_date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) : getCurrentDate()}
        </p>
        {usingMockData && (
          <p className="text-xs text-[#4A4A4A] mt-2 font-label">Demo Mode - Ingest articles via API to see real content</p>
        )}
      </header>

      {/* Main Content Area */}
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-0">
          
          {/* Left Sidebar - Categories */}
          <aside className="col-span-12 md:col-span-2 py-8 pr-0 md:pr-6 md:border-r border-[#111111]/30" data-testid="category-sidebar">
            <nav className="flex flex-row md:flex-col gap-2 md:gap-0 flex-wrap md:flex-nowrap mb-8">
              {CATEGORIES.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`category-nav-item text-left ${selectedCategory === category ? 'active' : ''}`}
                  data-testid={`category-${category.toLowerCase().replace(/\./g, '').replace(/\s+/g, '-')}`}
                >
                  {category}
                </button>
              ))}
            </nav>

            {/* Articles & Print Edition Links */}
            <div className="hidden md:block mt-8 pt-4 border-t border-[#111111]/30">
              <p className="font-label text-xs tracking-widest text-[#4A4A4A] mb-4">ARTICLES</p>
              <p className="font-label text-xs tracking-widest text-[#4A4A4A] mb-8">PRINT EDITION</p>
              
              <div className="mt-8">
                <p className="font-body text-sm text-[#4A4A4A]">@TheLedger</p>
                <p className="font-body text-sm text-[#4A4A4A] mt-2 flex items-center gap-2">
                  <span className="inline-block w-2 h-2 bg-[#111111]"></span>
                  Subscribe
                </p>
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <main className="col-span-12 md:col-span-7 py-8 px-0 md:px-6" data-testid="main-content">
            {/* Featured Article */}
            {featuredArticle ? (
              <article className="mb-8 pb-8 border-b border-[#111111]/30" data-testid="featured-article">
                <p className="section-label mb-3">{selectedCategory.toUpperCase()}</p>
                <h2 className="article-headline text-4xl md:text-5xl lg:text-6xl mb-4">
                  {featuredArticle.headline}
                </h2>
                <p className="article-excerpt text-lg text-[#4A4A4A] mb-4">
                  {featuredArticle.summary}
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    {featuredArticle.image_url && (
                      <img 
                        src={featuredArticle.image_url} 
                        alt={featuredArticle.headline}
                        className="news-image w-full aspect-video"
                      />
                    )}
                  </div>
                  <div className="flex flex-col justify-between">
                    <div>
                      {featuredArticle.why_it_matters && (
                        <div className="mb-4">
                          <p className="section-label mb-1">WHY IT MATTERS</p>
                          <p className="font-body text-sm leading-relaxed text-[#4A4A4A]">
                            {featuredArticle.why_it_matters}
                          </p>
                        </div>
                      )}
                      {featuredArticle.watch_next && (
                        <div className="mb-4">
                          <p className="section-label mb-1">WHAT TO WATCH</p>
                          <p className="font-body text-sm leading-relaxed text-[#4A4A4A]">
                            {featuredArticle.watch_next}
                          </p>
                        </div>
                      )}
                      <div className="flex items-center gap-2 mt-4">
                        <div className="w-8 h-8 bg-[#111111]/10 rounded-full flex items-center justify-center">
                          <span className="text-xs font-label">{(featuredArticle.curated_by || 'N')[0]}</span>
                        </div>
                        <span className="article-author">{featuredArticle.curated_by || 'News Ledger'}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Supporting Articles */}
                {featuredArticle.supporting_articles && featuredArticle.supporting_articles.length > 0 && (
                  <div className="mt-6 pt-4 border-t border-[#111111]/20">
                    <p className="section-label mb-3">RELATED COVERAGE</p>
                    <div className="space-y-3">
                      {featuredArticle.supporting_articles.map((sa, idx) => (
                        <div key={idx} className="flex items-start gap-3">
                          <span className="text-xs font-label uppercase text-[#4A4A4A] bg-[#111111]/5 px-2 py-1">
                            {sa.context_type === 'deep_dive' ? 'ANALYSIS' : sa.context_type === 'alternative' ? 'ALT VIEW' : 'CONTEXT'}
                          </span>
                          <div>
                            <p className="font-body text-sm font-bold">{sa.headline}</p>
                            {sa.summary && <p className="font-body text-xs text-[#4A4A4A] mt-1">{sa.summary}</p>}
                            {sa.source_name && <p className="article-author text-[10px] mt-1">— {sa.source_name}</p>}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Political Synthesis */}
                {featuredArticle.political_synthesis && (
                  <div className="mt-4 pt-4 border-t border-[#111111]/20 bg-[#111111]/5 p-4">
                    <p className="section-label mb-2">POLITICAL SYNTHESIS</p>
                    <p className="font-body text-sm italic text-[#4A4A4A]">
                      {featuredArticle.political_synthesis}
                    </p>
                  </div>
                )}
              </article>
            ) : (
              <div className="mb-8 pb-8 border-b border-[#111111]/30">
                <p className="section-label mb-3">{selectedCategory.toUpperCase()}</p>
                <p className="font-body text-lg text-[#4A4A4A]">No articles available for this category.</p>
              </div>
            )}

            {/* Other articles in category */}
            {otherArticles.length > 0 && (
              <div className="mb-8" data-testid="category-articles">
                <p className="section-label mb-4">MORE IN {selectedCategory.toUpperCase()}</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {otherArticles.map((article) => (
                    <div key={article.id} className="pb-4 border-b border-[#111111]/20 article-card">
                      {article.image_url && (
                        <img 
                          src={article.image_url} 
                          alt={article.headline}
                          className="news-image w-full aspect-video mb-3"
                        />
                      )}
                      <h3 className="font-headline text-lg font-bold leading-tight mb-2">
                        {article.headline}
                      </h3>
                      <p className="font-body text-sm text-[#4A4A4A] mb-2">
                        {article.summary}
                      </p>
                      <div className="flex items-center gap-2">
                        <span className="article-author text-[10px]">{article.curated_by || 'News Ledger'}</span>
                        {article.is_political && (
                          <span className="text-[10px] font-label uppercase text-[#4A4A4A] bg-[#111111]/10 px-1">POLITICAL</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Issue Number */}
            <div className="text-center py-6 border-y border-[#111111]/30 my-8">
              <p className="font-headline text-6xl md:text-7xl font-bold">NO. 01</p>
            </div>
          </main>

          {/* Right Sidebar - Featured Articles */}
          <aside className="col-span-12 md:col-span-3 py-8 pl-0 md:pl-6 md:border-l border-[#111111]/30" data-testid="featured-sidebar">
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-headline text-xl font-bold">Featured Articles</h3>
              <button className="text-xs font-label tracking-widest hover:underline">See All</button>
            </div>

            {/* Sidebar Article List */}
            <div className="space-y-4 mb-8">
              {(sidebarArticles.length > 0 ? sidebarArticles : Object.values(MOCK_ARTICLES).flat()).slice(0, 5).map((article, idx) => (
                <div key={article.id || idx} className="flex gap-3 pb-4 border-b border-[#111111]/20 article-card">
                  {article.image_url && (
                    <img 
                      src={article.image_url} 
                      alt={article.headline}
                      className="news-image w-16 h-16 object-cover flex-shrink-0"
                    />
                  )}
                  <div>
                    <h4 className="font-headline text-sm font-bold leading-tight mb-1">
                      {article.headline?.slice(0, 50)}...
                    </h4>
                    <span className="article-author text-[10px]">{article.curated_by || 'News Ledger'}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Large Featured Article */}
            {sidebarArticles[0] && (
              <article className="mb-6" data-testid="sidebar-featured">
                <h3 className="font-headline text-2xl font-bold leading-tight mb-2">
                  {sidebarArticles[0].headline}
                </h3>
                <p className="article-author mb-2">by {sidebarArticles[0].curated_by || 'News Ledger'}</p>
                <p className="font-body text-sm text-[#4A4A4A] mb-4">
                  {sidebarArticles[0].summary}
                </p>
                <button className="text-xs font-label tracking-widest hover:underline flex items-center gap-1">
                  <span>&#8592;</span> See More
                </button>
              </article>
            )}

            {/* Bottom Sidebar Image */}
            {sidebarArticles[1] && sidebarArticles[1].image_url && (
              <div className="mt-6">
                <img 
                  src={sidebarArticles[1].image_url}
                  alt={sidebarArticles[1].headline}
                  className="news-image w-full aspect-[4/3]"
                />
                <h4 className="font-headline text-xl font-bold mt-3">{sidebarArticles[1].headline}</h4>
              </div>
            )}
          </aside>
        </div>

        {/* Bottom Section - Article Cards */}
        {bottomArticles.length > 0 && (
          <section className="border-t-2 border-[#111111]/50 pt-8 mt-8" data-testid="bottom-articles">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {bottomArticles.map((article) => (
                <article key={article.id} className="article-card" data-testid={`bottom-article-${article.id}`}>
                  {article.image_url && (
                    <img 
                      src={article.image_url} 
                      alt={article.headline}
                      className="news-image w-full aspect-[4/3] mb-3"
                    />
                  )}
                  <p className="section-label mb-1">{article.category}</p>
                  <h3 className="font-headline text-lg font-bold leading-tight mb-2">
                    {article.headline}
                  </h3>
                  <p className="font-body text-sm text-[#4A4A4A]">
                    {article.summary?.slice(0, 80)}...
                  </p>
                </article>
              ))}
            </div>
          </section>
        )}
      </div>

      {/* News Ticker */}
      <footer className="news-ticker py-2 px-4 fixed bottom-0 left-0 right-0" data-testid="news-ticker">
        <div className="ticker-content ticker-animation">
          {allArticles.slice(0, 6).map((article, idx) => (
            <span key={idx} className="mx-8">&#9679; {article.headline?.slice(0, 40)}...</span>
          ))}
          {allArticles.length === 0 && (
            <>
              <span className="mx-8">&#9679; Welcome to News Ledger</span>
              <span className="mx-8">&#9679; Ingest articles via /api/articles/ingest endpoint</span>
              <span className="mx-8">&#9679; Your AI agent can populate this dashboard</span>
            </>
          )}
          {/* Duplicate for seamless loop */}
          {allArticles.slice(0, 6).map((article, idx) => (
            <span key={`dup-${idx}`} className="mx-8">&#9679; {article.headline?.slice(0, 40)}...</span>
          ))}
        </div>
      </footer>
    </div>
  );
}

export default App;
