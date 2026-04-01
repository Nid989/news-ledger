import { useState, useEffect } from "react";
import "@/App.css";
import axios from "axios";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Categories for navigation
const CATEGORIES = ["U.S.", "World", "Local", "Business", "Technology", "Entertainment", "Sports", "Science", "Health"];

function App() {
  const [selectedCategory, setSelectedCategory] = useState("U.S.");
  const [featuredArticle, setFeaturedArticle] = useState(null);
  const [spotlightArticle, setSpotlightArticle] = useState(null);
  const [sidebarArticles, setSidebarArticles] = useState([]);
  const [bottomArticles, setBottomArticles] = useState([]);
  const [opinionArticles, setOpinionArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  // Get current date formatted
  const getCurrentDate = () => {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return new Date().toLocaleDateString('en-US', options);
  };

  // Fetch all articles on mount
  useEffect(() => {
    const fetchArticles = async () => {
      try {
        setLoading(true);
        const [featured, spotlight, sidebar, bottom, opinions] = await Promise.all([
          axios.get(`${API}/articles/featured`),
          axios.get(`${API}/articles/spotlight`),
          axios.get(`${API}/articles/sidebar`),
          axios.get(`${API}/articles/bottom`),
          axios.get(`${API}/articles/opinions`)
        ]);
        
        setFeaturedArticle(featured.data);
        setSpotlightArticle(spotlight.data);
        setSidebarArticles(sidebar.data);
        setBottomArticles(bottom.data);
        setOpinionArticles(opinions.data);
      } catch (error) {
        console.error("Error fetching articles:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F4F1EA] flex items-center justify-center">
        <div className="font-headline text-2xl text-[#111111]">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F4F1EA]" data-testid="news-ledger-app">
      {/* Masthead Header */}
      <header className="text-center py-6 border-b-4 border-t-8 border-[#111111] mb-0" data-testid="masthead">
        <h1 className="masthead-title text-5xl sm:text-6xl md:text-7xl lg:text-8xl text-[#111111] mb-2">
          News Ledger
        </h1>
        <p className="font-label text-xs tracking-widest text-[#4A4A4A] uppercase">
          {getCurrentDate()}
        </p>
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
                  data-testid={`category-${category.toLowerCase().replace('.', '').replace(' ', '-')}`}
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
            {featuredArticle && (
              <article className="mb-8 pb-8 border-b border-[#111111]/30" data-testid="featured-article">
                <p className="section-label mb-3">PHILOSOPHY</p>
                <h2 className="article-headline text-4xl md:text-5xl lg:text-6xl mb-4">
                  {featuredArticle.title}
                </h2>
                <p className="article-excerpt text-lg text-[#4A4A4A] mb-4">
                  {featuredArticle.excerpt}
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <img 
                      src={featuredArticle.image_url} 
                      alt={featuredArticle.title}
                      className="news-image w-full aspect-video"
                    />
                  </div>
                  <div className="flex flex-col justify-between">
                    <div>
                      <p className="font-body text-sm leading-relaxed text-[#4A4A4A] mb-4">
                        <span className="font-bold">&#8220;</span> {featuredArticle.content.slice(0, 200)}...
                      </p>
                      <div className="flex items-center gap-2 mt-4">
                        <div className="w-8 h-8 bg-[#111111]/10 rounded-full flex items-center justify-center">
                          <span className="text-xs font-label">{featuredArticle.author.charAt(0)}</span>
                        </div>
                        <span className="article-author">{featuredArticle.author}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Additional quote */}
                <div className="mt-6 pt-4 border-t border-[#111111]/20">
                  <p className="font-body text-sm italic text-[#4A4A4A]">
                    &#8220; ...the wise man, self-sufficient as he is, still desires a friend (if only), for the purpose of practicing friendship.
                  </p>
                  <div className="flex items-center gap-2 mt-3">
                    <div className="w-6 h-6 bg-[#111111]/10 rounded-full flex items-center justify-center">
                      <span className="text-[10px] font-label">L</span>
                    </div>
                    <span className="article-author text-[10px]">Lucius Antonio Santos</span>
                  </div>
                </div>
              </article>
            )}

            {/* Spotlight Article */}
            {spotlightArticle && (
              <article className="mb-8" data-testid="spotlight-article">
                <p className="section-label mb-3">SPOTLIGHT</p>
                <h3 className="article-headline text-2xl md:text-3xl mb-3">
                  {spotlightArticle.title}
                </h3>
                <p className="article-excerpt text-base text-[#4A4A4A] mb-4">
                  {spotlightArticle.excerpt}
                </p>
              </article>
            )}

            {/* Issue Number */}
            <div className="text-center py-6 border-y border-[#111111]/30 my-8">
              <p className="font-headline text-6xl md:text-7xl font-bold">NO. 01</p>
            </div>

            {/* Opinion Articles Grid */}
            <div className="mb-8" data-testid="opinions-section">
              <p className="section-label mb-4">OPINIONS</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {opinionArticles.map((article, index) => (
                  <div key={article.id} className="pb-4 border-b border-[#111111]/20">
                    <p className="font-body text-sm text-[#4A4A4A] mb-2">
                      {article.title.slice(0, 60)}...
                    </p>
                    <div className="flex items-center gap-2">
                      <div className="w-5 h-5 bg-[#111111]/10 rounded-full flex items-center justify-center">
                        <span className="text-[8px] font-label">{article.author.charAt(0)}</span>
                      </div>
                      <span className="article-author text-[10px]">{article.author}</span>
                    </div>
                    <p className="font-body text-xs text-[#4A4A4A] mt-2 italic">
                      &#8220; {article.excerpt.slice(0, 50)}...
                    </p>
                  </div>
                ))}
              </div>
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
              {sidebarArticles.slice(0, 3).map((article) => (
                <div key={article.id} className="flex gap-3 pb-4 border-b border-[#111111]/20 article-card">
                  <img 
                    src={article.image_url} 
                    alt={article.title}
                    className="news-image w-16 h-16 object-cover flex-shrink-0"
                  />
                  <div>
                    <h4 className="font-headline text-sm font-bold leading-tight mb-1">
                      {article.title.slice(0, 50)}...
                    </h4>
                    <span className="article-author text-[10px]">{article.author}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Large Featured Article */}
            {sidebarArticles[3] && (
              <article className="mb-6" data-testid="sidebar-featured">
                <h3 className="font-headline text-2xl font-bold leading-tight mb-2">
                  National Gallery to reopen with exhibition on Pieter Brueghel
                </h3>
                <p className="article-author mb-2">by Ellie Barnes</p>
                <p className="font-body text-sm text-[#4A4A4A] mb-4">
                  The exhibition will feature more than 10 paintings on display for the first time, highlighting the history of art's famous faces, from George Bernard Shaw to Vivien Leigh, John Gielgud to Princess Margaret.
                </p>
                <button className="text-xs font-label tracking-widest hover:underline flex items-center gap-1">
                  <span>&#8592;</span> See More
                </button>
              </article>
            )}

            {/* Bottom Sidebar Image */}
            <div className="mt-6">
              <img 
                src="https://images.pexels.com/photos/16461387/pexels-photo-16461387.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
                alt="Renaissance Art"
                className="news-image w-full aspect-[4/3]"
              />
              <h4 className="font-headline text-xl font-bold mt-3">Five key Renaissance Paintings</h4>
            </div>
          </aside>
        </div>

        {/* Bottom Section - Article Cards */}
        <section className="border-t-2 border-[#111111]/50 pt-8 mt-8 pb-12" data-testid="bottom-articles">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {bottomArticles.map((article) => (
              <article key={article.id} className="article-card" data-testid={`bottom-article-${article.id}`}>
                <img 
                  src={article.image_url} 
                  alt={article.title}
                  className="news-image w-full aspect-[4/3] mb-3"
                />
                <h3 className="font-headline text-lg font-bold leading-tight mb-2">
                  {article.title}
                </h3>
                <p className="font-body text-sm text-[#4A4A4A]">
                  {article.excerpt.slice(0, 80)}...
                </p>
              </article>
            ))}
          </div>
        </section>
      </div>

      {/* News Ticker */}
      <footer className="news-ticker py-2 px-4 fixed bottom-0 left-0 right-0" data-testid="news-ticker">
        <div className="ticker-content ticker-animation">
          <span className="mx-8">&#9679; NYS sheds after long slideroad inhaul</span>
          <span className="mx-8">&#9679; 16th Exhibition / National/Portrait Gallery</span>
          <span className="mx-8">&#9679; Now It : First Art at The Seattle NYM</span>
          <span className="mx-8">&#9679; NYS Opsin Area Long Lockstead Choice</span>
          <span className="mx-8">&#9679; MoPS Global / National Portrait Gallery</span>
          <span className="mx-8">&#9679; Vhise in : Pho Art at the Seattle</span>
          {/* Duplicate for seamless loop */}
          <span className="mx-8">&#9679; NYS sheds after long slideroad inhaul</span>
          <span className="mx-8">&#9679; 16th Exhibition / National/Portrait Gallery</span>
          <span className="mx-8">&#9679; Now It : First Art at The Seattle NYM</span>
          <span className="mx-8">&#9679; NYS Opsin Area Long Lockstead Choice</span>
          <span className="mx-8">&#9679; MoPS Global / National Portrait Gallery</span>
          <span className="mx-8">&#9679; Vhise in : Pho Art at the Seattle</span>
        </div>
      </footer>
    </div>
  );
}

export default App;
