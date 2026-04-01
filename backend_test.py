import requests
import sys
from datetime import datetime

class NewsLedgerAPITester:
    def __init__(self, base_url="https://news-hub-reader.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, expected_fields=None):
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
                response = requests.post(url, json={}, headers=headers, timeout=10)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Check response structure if expected_fields provided
                if expected_fields:
                    try:
                        data = response.json()
                        if isinstance(expected_fields, list):
                            # Check if response is a list
                            if isinstance(data, list) and len(data) > 0:
                                for field in expected_fields:
                                    if field not in data[0]:
                                        print(f"⚠️  Warning: Missing field '{field}' in response")
                            elif isinstance(data, dict):
                                for field in expected_fields:
                                    if field not in data:
                                        print(f"⚠️  Warning: Missing field '{field}' in response")
                        elif isinstance(expected_fields, dict):
                            # Check specific structure
                            for key, expected_type in expected_fields.items():
                                if key in data:
                                    if expected_type == "list" and not isinstance(data[key], list):
                                        print(f"⚠️  Warning: Field '{key}' should be a list")
                                    elif expected_type == "string" and not isinstance(data[key], str):
                                        print(f"⚠️  Warning: Field '{key}' should be a string")
                                else:
                                    print(f"⚠️  Warning: Missing field '{key}' in response")
                        
                        print(f"   Response preview: {str(data)[:200]}...")
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
        """Test categories endpoint"""
        success, response = self.run_test(
            "Get Categories",
            "GET",
            "categories",
            200,
            {"categories": "list"}
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

    def test_featured_article(self):
        """Test featured article endpoint"""
        success, response = self.run_test(
            "Get Featured Article",
            "GET",
            "articles/featured",
            200,
            ["id", "title", "excerpt", "content", "category", "author", "image_url", "published_at", "is_featured"]
        )
        
        if success and "is_featured" in response:
            if response["is_featured"]:
                print(f"✅ Featured article correctly marked as featured")
            else:
                print(f"⚠️  Warning: Featured article not marked as featured")
                
        return success

    def test_spotlight_article(self):
        """Test spotlight article endpoint"""
        success, response = self.run_test(
            "Get Spotlight Article",
            "GET",
            "articles/spotlight",
            200,
            ["id", "title", "excerpt", "content", "category", "author", "image_url", "published_at", "is_spotlight"]
        )
        
        if success and "is_spotlight" in response:
            if response["is_spotlight"]:
                print(f"✅ Spotlight article correctly marked as spotlight")
            else:
                print(f"⚠️  Warning: Spotlight article not marked as spotlight")
                
        return success

    def test_sidebar_articles(self):
        """Test sidebar articles endpoint"""
        success, response = self.run_test(
            "Get Sidebar Articles",
            "GET",
            "articles/sidebar",
            200,
            ["id", "title", "excerpt", "content", "category", "author", "image_url", "published_at"]
        )
        
        if success and isinstance(response, list):
            print(f"✅ Sidebar articles returned as list with {len(response)} articles")
            if len(response) >= 3:
                print(f"✅ Sufficient articles for sidebar display")
            else:
                print(f"⚠️  Warning: Only {len(response)} sidebar articles, may need more for display")
                
        return success

    def test_bottom_articles(self):
        """Test bottom articles endpoint"""
        success, response = self.run_test(
            "Get Bottom Articles",
            "GET",
            "articles/bottom",
            200,
            ["id", "title", "excerpt", "content", "category", "author", "image_url", "published_at"]
        )
        
        if success and isinstance(response, list):
            print(f"✅ Bottom articles returned as list with {len(response)} articles")
            if len(response) >= 4:
                print(f"✅ Sufficient articles for bottom grid display")
            else:
                print(f"⚠️  Warning: Only {len(response)} bottom articles, may need more for grid")
                
        return success

    def test_opinion_articles(self):
        """Test opinion articles endpoint"""
        success, response = self.run_test(
            "Get Opinion Articles",
            "GET",
            "articles/opinions",
            200,
            ["id", "title", "excerpt", "content", "category", "author", "image_url", "published_at"]
        )
        
        if success and isinstance(response, list):
            print(f"✅ Opinion articles returned as list with {len(response)} articles")
            if len(response) >= 3:
                print(f"✅ Sufficient articles for opinions grid")
            else:
                print(f"⚠️  Warning: Only {len(response)} opinion articles, may need more for grid")
                
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
    
    # Test categories
    tester.test_categories()
    
    # Test article endpoints
    tester.test_featured_article()
    tester.test_spotlight_article()
    tester.test_sidebar_articles()
    tester.test_bottom_articles()
    tester.test_opinion_articles()

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