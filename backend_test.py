import requests
import sys
from datetime import datetime, date
import uuid

class NewsLedgerAPITester:
    def __init__(self, base_url="https://news-hub-reader.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, expected_fields=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Check response structure if expected_fields provided
                if expected_fields:
                    try:
                        response_data = response.json()
                        if isinstance(expected_fields, list):
                            # Check if response is a list
                            if isinstance(response_data, list) and len(response_data) > 0:
                                for field in expected_fields:
                                    if field not in response_data[0]:
                                        print(f"⚠️  Warning: Missing field '{field}' in response")
                            elif isinstance(response_data, dict):
                                for field in expected_fields:
                                    if field not in response_data:
                                        print(f"⚠️  Warning: Missing field '{field}' in response")
                        elif isinstance(expected_fields, dict):
                            # Check specific structure
                            for key, expected_type in expected_fields.items():
                                if key in response_data:
                                    if expected_type == "list" and not isinstance(response_data[key], list):
                                        print(f"⚠️  Warning: Field '{key}' should be a list")
                                    elif expected_type == "string" and not isinstance(response_data[key], str):
                                        print(f"⚠️  Warning: Field '{key}' should be a string")
                                else:
                                    print(f"⚠️  Warning: Missing field '{key}' in response")
                        
                        print(f"   Response preview: {str(response_data)[:200]}...")
                    except Exception as e:
                        print(f"⚠️  Warning: Could not parse JSON response: {e}")
                
            else:
                self.failed_tests.append({
                    "test": name,
                    "endpoint": endpoint,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200] if response.text else "No response"
                })
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")

            return success, response.json() if success and response.text else {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout")
            self.failed_tests.append({
                "test": name,
                "endpoint": endpoint,
                "error": "Request timeout"
            })
            return False, {}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error")
            self.failed_tests.append({
                "test": name,
                "endpoint": endpoint,
                "error": "Connection error"
            })
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                "test": name,
                "endpoint": endpoint,
                "error": str(e)
            })
            return False, {}

    def test_categories(self):
        """Test GET /api/categories returns 9 categories"""
        success, response = self.run_test(
            "Get Categories",
            "GET",
            "categories",
            200,
            expected_fields={"categories": "list"}
        )
        
        if success and "categories" in response:
            categories = response["categories"]
            expected_categories = ["U.S.", "World", "Local", "Business", "Technology", "Entertainment", "Sports", "Science", "Health"]
            
            if len(categories) == 9:
                print(f"✅ Found all 9 categories")
            else:
                print(f"⚠️  Warning: Expected 9 categories, found {len(categories)}")
            
            missing_categories = [cat for cat in expected_categories if cat not in categories]
            if missing_categories:
                print(f"⚠️  Warning: Missing categories: {missing_categories}")
            else:
                print(f"✅ All expected categories present")
                
        return success

    def test_digests_list(self):
        """Test GET /api/digests - list digests"""
        success, response = self.run_test(
            "List Digests",
            "GET",
            "digests",
            200,
            expected_fields=["id", "edition_name", "digest_date", "status", "article_count"]
        )
        
        if success and isinstance(response, list):
            print(f"✅ Digests returned as list with {len(response)} digests")
            if len(response) > 0:
                print(f"✅ Found digests in database")
                # Store first digest ID for later tests
                self.first_digest_id = response[0].get("id")
            else:
                print(f"⚠️  Warning: No digests found in database")
                
        return success

    def test_digest_by_date(self):
        """Test GET /api/digests/date/{date} - get digest by date (2026-01-29)"""
        test_date = "2026-01-29"
        success, response = self.run_test(
            f"Get Digest by Date ({test_date})",
            "GET",
            f"digests/date/{test_date}",
            200,
            expected_fields=["id", "edition_name", "digest_date", "articles"]
        )
        
        if success:
            if "articles" in response and isinstance(response["articles"], list):
                print(f"✅ Digest contains {len(response['articles'])} articles")
                # Store digest ID for later tests
                self.test_digest_id = response.get("id")
            else:
                print(f"⚠️  Warning: Digest missing articles array")
                
        return success

    def test_digest_by_id(self):
        """Test GET /api/digests/{id} - get digest with articles"""
        if not hasattr(self, 'test_digest_id'):
            print("⚠️  Skipping digest by ID test - no digest ID available")
            return True
            
        success, response = self.run_test(
            "Get Digest by ID",
            "GET",
            f"digests/{self.test_digest_id}",
            200,
            expected_fields=["id", "edition_name", "digest_date", "articles"]
        )
        
        if success and "articles" in response:
            articles = response["articles"]
            print(f"✅ Digest contains {len(articles)} articles")
            
            # Check for supporting articles and sources
            for article in articles:
                if "supporting_articles" in article:
                    print(f"✅ Article has {len(article['supporting_articles'])} supporting articles")
                if "sources" in article:
                    print(f"✅ Article has {len(article['sources'])} sources")
                    
        return success

    def test_articles_filter_by_category(self):
        """Test GET /api/articles?category=U.S. - filter by category"""
        success, response = self.run_test(
            "Filter Articles by Category (U.S.)",
            "GET",
            "articles?category=U.S.",
            200,
            expected_fields=["id", "category", "headline", "summary", "supporting_articles", "sources"]
        )
        
        if success and isinstance(response, list):
            print(f"✅ Found {len(response)} U.S. articles")
            
            # Check that all articles are U.S. category
            for article in response:
                if article.get("category") != "U.S.":
                    print(f"⚠️  Warning: Non-U.S. article found: {article.get('category')}")
                    break
            else:
                print(f"✅ All articles are U.S. category")
                
            # Check for nested supporting articles and sources
            for article in response:
                if "supporting_articles" in article and isinstance(article["supporting_articles"], list):
                    print(f"✅ Article has {len(article['supporting_articles'])} supporting articles nested")
                if "sources" in article and isinstance(article["sources"], list):
                    print(f"✅ Article has {len(article['sources'])} sources nested")
                    
        return success

    def test_create_single_article(self):
        """Test POST /api/articles - create single article"""
        if not hasattr(self, 'test_digest_id'):
            print("⚠️  Skipping create article test - no digest ID available")
            return True
            
        article_data = {
            "category": "Technology",
            "rank": 1,
            "headline": "Test Article for API Testing",
            "summary": "This is a test article created during API testing",
            "why_it_matters": "Testing is important for quality assurance",
            "watch_next": "Monitor for any issues",
            "importance_score": 0.8,
            "is_political": False,
            "curated_by": "API Tester",
            "supporting_articles": [
                {
                    "headline": "Supporting Test Article",
                    "summary": "Additional context for the main article",
                    "context_type": "context",
                    "source_name": "Test Source"
                }
            ],
            "sources": [
                {
                    "source_name": "Test News Source",
                    "source_url": "https://example.com/test",
                    "source_type": "primary"
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Single Article",
            "POST",
            f"articles?digest_id={self.test_digest_id}",
            201,
            data=article_data,
            expected_fields=["id", "category", "headline", "supporting_articles", "sources"]
        )
        
        if success:
            print(f"✅ Article created successfully")
            if "supporting_articles" in response and len(response["supporting_articles"]) > 0:
                print(f"✅ Supporting articles created and nested")
            if "sources" in response and len(response["sources"]) > 0:
                print(f"✅ Sources created and nested")
                
        return success

    def test_bulk_ingest(self):
        """Test POST /api/articles/ingest - bulk ingest endpoint"""
        bulk_data = {
            "edition_name": "Test Edition",
            "digest_date": "2026-01-30",
            "recency_window_hours": 24,
            "articles": [
                {
                    "category": "Technology",
                    "rank": 1,
                    "headline": "Bulk Ingest Test Article",
                    "summary": "Testing bulk ingest functionality",
                    "why_it_matters": "Bulk ingest is critical for AI agent integration",
                    "importance_score": 0.9,
                    "is_political": False,
                    "curated_by": "Bulk Tester",
                    "supporting_articles": [
                        {
                            "headline": "Supporting Article for Bulk Test",
                            "summary": "Additional context",
                            "context_type": "context",
                            "source_name": "Bulk Test Source"
                        }
                    ],
                    "sources": [
                        {
                            "source_name": "Bulk News Source",
                            "source_url": "https://example.com/bulk",
                            "source_type": "primary"
                        }
                    ]
                }
            ]
        }
        
        success, response = self.run_test(
            "Bulk Ingest Articles",
            "POST",
            "articles/ingest",
            200,
            data=bulk_data,
            expected_fields=["digest_id", "articles_created", "supporting_articles_created", "sources_created"]
        )
        
        if success:
            print(f"✅ Bulk ingest successful")
            print(f"   Articles created: {response.get('articles_created', 0)}")
            print(f"   Supporting articles created: {response.get('supporting_articles_created', 0)}")
            print(f"   Sources created: {response.get('sources_created', 0)}")
                
        return success

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "API Root",
            "GET",
            "",
            200
        )
        return success

def main():
    print("🗞️  News Ledger API Testing Suite")
    print("=" * 50)
    
    # Setup
    tester = NewsLedgerAPITester()
    
    # Run all tests
    print("\n📋 Running API Tests...")
    
    # Test root endpoint
    tester.test_root_endpoint()
    
    # Test categories (should return 9 categories)
    tester.test_categories()
    
    # Test digest endpoints
    tester.test_digests_list()
    tester.test_digest_by_date()
    tester.test_digest_by_id()
    
    # Test article endpoints
    tester.test_articles_filter_by_category()
    tester.test_create_single_article()
    
    # Test bulk ingest
    tester.test_bulk_ingest()

    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    
    if tester.failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in tester.failed_tests:
            error_msg = test.get('error', f"Expected {test.get('expected')}, got {test.get('actual')}")
            print(f"   - {test['test']}: {error_msg}")
    
    success_rate = (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())