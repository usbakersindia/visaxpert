#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class VisaXpertAPITester:
    def __init__(self, base_url="https://visacheck-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_email = "admin@visaxpert.com"
        self.admin_password = "VisaXpert@2024"

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, params=params, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 500:
                        print(f"   Response: {response_data}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test API health endpoint"""
        return self.run_test("Health Check", "GET", "health", 200)

    def test_dashboard_login(self):
        """Test dashboard login"""
        login_data = {
            "email": self.admin_email,
            "password": self.admin_password
        }
        success, response = self.run_test("Dashboard Login", "POST", "dashboard/login", 200, data=login_data)
        return success, response

    def test_dashboard_stats(self):
        """Test dashboard stats"""
        params = {
            "email": self.admin_email,
            "password": self.admin_password
        }
        return self.run_test("Dashboard Stats", "GET", "dashboard/stats", 200, params=params)

    def test_dashboard_leads(self):
        """Test dashboard leads listing"""
        params = {
            "email": self.admin_email,
            "password": self.admin_password,
            "page": 1,
            "per_page": 10
        }
        return self.run_test("Dashboard Leads", "GET", "dashboard/leads", 200, params=params)

    def test_reviews_api(self):
        """Test reviews API endpoints"""
        # Test getting reviews for main page
        success1, response1 = self.run_test("Get Reviews (Main Page)", "GET", "reviews", 200, params={"page": "main"})
        
        # Test getting all reviews
        success2, response2 = self.run_test("Get All Reviews", "GET", "reviews", 200)
        
        return success1 and success2, {"main_reviews": response1, "all_reviews": response2}

    def test_dashboard_reviews(self):
        """Test dashboard reviews management"""
        params = {
            "email": self.admin_email,
            "password": self.admin_password
        }
        return self.run_test("Dashboard Reviews", "GET", "dashboard/reviews", 200, params=params)

    def test_create_review(self):
        """Test creating a new review"""
        review_data = {
            "name": "Test Student",
            "country": "Canada",
            "content": "This is a test review for the testing purposes. VisaXpert helped me a lot!",
            "image_url": "https://via.placeholder.com/150",
            "rating": 5,
            "page": "main"
        }
        params = {
            "email": self.admin_email,
            "password": self.admin_password
        }
        return self.run_test("Create Review", "POST", "dashboard/reviews", 200, data=review_data, params=params)

    def test_germany_fair_lead_submission(self):
        """Test Germany Fair lead submission"""
        lead_data = {
            "name": "Test Germany Fair User",
            "email": f"test_germany_{datetime.now().strftime('%H%M%S')}@example.com",
            "phone": "9876543210",
            "city": "Test City",
            "country": "Germany",
            "source": "germany_fair",
            "campaign": "Germany Fair 2026 - Ludhiana",
            "platform": "germany_fair_landing"
        }
        return self.run_test("Germany Fair Lead", "POST", "webhook/lead", 200, data=lead_data)

    def test_main_enquiry_submission(self):
        """Test main landing page enquiry submission"""
        enquiry_data = {
            "name": "Test Main User",
            "email": f"test_main_{datetime.now().strftime('%H%M%S')}@example.com",
            "phone": "9876543210",
            "city": "Test City",
            "country_of_interest": "Canada"
        }
        return self.run_test("Main Enquiry", "POST", "enquiry", 200, data=enquiry_data)

    def test_source_filter_germany_fair(self):
        """Test that Germany Fair leads appear in dashboard with correct source"""
        params = {
            "email": self.admin_email,
            "password": self.admin_password,
            "source": "germany_fair",
            "page": 1,
            "per_page": 5
        }
        return self.run_test("Germany Fair Source Filter", "GET", "dashboard/leads", 200, params=params)

def main():
    print("🚀 Starting VisaXpert API Tests...")
    print("=" * 60)
    
    tester = VisaXpertAPITester()
    
    # Basic API tests
    print("\n📋 BASIC API TESTS")
    print("-" * 30)
    tester.test_health_check()
    
    # Authentication tests
    print("\n🔐 AUTHENTICATION TESTS")
    print("-" * 30)
    login_success, login_response = tester.test_dashboard_login()
    if not login_success:
        print("❌ Login failed, stopping dashboard tests")
        return 1
    
    # Dashboard tests
    print("\n📊 DASHBOARD TESTS")
    print("-" * 30)
    tester.test_dashboard_stats()
    tester.test_dashboard_leads()
    
    # Reviews tests
    print("\n⭐ REVIEWS TESTS")
    print("-" * 30)
    tester.test_reviews_api()
    tester.test_dashboard_reviews()
    tester.test_create_review()
    
    # Lead submission tests
    print("\n📝 LEAD SUBMISSION TESTS")
    print("-" * 30)
    tester.test_main_enquiry_submission()
    tester.test_germany_fair_lead_submission()
    
    # Source filtering tests
    print("\n🔍 SOURCE FILTERING TESTS")
    print("-" * 30)
    tester.test_source_filter_germany_fair()
    
    # Print results
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Overall: GOOD - Most tests passed")
        return 0
    elif success_rate >= 60:
        print("⚠️  Overall: FAIR - Some issues found")
        return 1
    else:
        print("❌ Overall: POOR - Major issues found")
        return 1

if __name__ == "__main__":
    sys.exit(main())