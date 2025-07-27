#!/usr/bin/env python3
"""
Video Template Platform API Test Script
This script tests all the API endpoints with sample data.
"""

import requests
import json
import time
from typing import Dict, Any

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def print_response(self, response: requests.Response, title: str):
        """Print formatted response"""
        print(f"\n{'='*50}")
        print(f"{title}")
        print(f"{'='*50}")
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
        print(f"{'='*50}")
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.session.get(f"{self.base_url}/")
        self.print_response(response, "Root Endpoint Test")
        return response.status_code == 200
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.session.get(f"{self.base_url}/health")
        self.print_response(response, "Health Check Test")
        return response.status_code == 200
    
    def test_register_user(self, user_data: Dict[str, Any]):
        """Test user registration"""
        response = self.session.post(
            f"{self.base_url}/auth/register",
            json=user_data
        )
        self.print_response(response, "User Registration Test")
        return response.status_code == 200
    
    def test_login(self, username: str, password: str):
        """Test user login"""
        response = self.session.post(
            f"{self.base_url}/auth/login",
            data={"username": username, "password": password}
        )
        self.print_response(response, "User Login Test")
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            return True
        return False
    
    def test_get_current_user(self):
        """Test getting current user"""
        response = self.session.get(f"{self.base_url}/auth/me")
        self.print_response(response, "Get Current User Test")
        return response.status_code == 200
    
    def test_get_all_templates(self):
        """Test getting all templates"""
        response = self.session.get(f"{self.base_url}/templates/")
        self.print_response(response, "Get All Templates Test")
        return response.status_code == 200
    
    def test_get_template_categories(self):
        """Test getting template categories"""
        response = self.session.get(f"{self.base_url}/templates/categories")
        self.print_response(response, "Get Template Categories Test")
        return response.status_code == 200
    
    def test_get_templates_by_category(self, category: str):
        """Test getting templates by category"""
        response = self.session.get(f"{self.base_url}/templates/category/{category}")
        self.print_response(response, f"Get Templates by Category ({category}) Test")
        return response.status_code == 200
    
    def test_get_template_by_id(self, template_id: str):
        """Test getting template by ID"""
        response = self.session.get(f"{self.base_url}/templates/{template_id}")
        self.print_response(response, f"Get Template by ID ({template_id}) Test")
        return response.status_code == 200
    
    def test_save_template(self, template_id: str):
        """Test saving a template"""
        response = self.session.post(f"{self.base_url}/templates/{template_id}/save")
        self.print_response(response, f"Save Template ({template_id}) Test")
        return response.status_code == 200
    
    def test_get_saved_templates(self):
        """Test getting saved templates"""
        response = self.session.get(f"{self.base_url}/templates/saved/my-templates")
        self.print_response(response, "Get Saved Templates Test")
        return response.status_code == 200
    
    def test_search_templates(self, query: str):
        """Test searching templates"""
        response = self.session.get(f"{self.base_url}/templates/search/{query}")
        self.print_response(response, f"Search Templates ({query}) Test")
        return response.status_code == 200
    
    def test_create_project(self, project_data: Dict[str, Any]):
        """Test creating a project"""
        response = self.session.post(
            f"{self.base_url}/projects/",
            json=project_data
        )
        self.print_response(response, "Create Project Test")
        
        if response.status_code == 200:
            data = response.json()
            return data.get("project_id")
        return None
    
    def test_get_user_projects(self):
        """Test getting user projects"""
        response = self.session.get(f"{self.base_url}/projects/")
        self.print_response(response, "Get User Projects Test")
        return response.status_code == 200
    
    def test_get_project_by_id(self, project_id: str):
        """Test getting project by ID"""
        response = self.session.get(f"{self.base_url}/projects/{project_id}")
        self.print_response(response, f"Get Project by ID ({project_id}) Test")
        return response.status_code == 200
    
    def test_update_project(self, project_id: str, update_data: Dict[str, Any]):
        """Test updating a project"""
        response = self.session.put(
            f"{self.base_url}/projects/{project_id}",
            json=update_data
        )
        self.print_response(response, f"Update Project ({project_id}) Test")
        return response.status_code == 200
    
    def test_render_project(self, project_id: str):
        """Test rendering a project"""
        response = self.session.post(f"{self.base_url}/projects/{project_id}/render")
        self.print_response(response, f"Render Project ({project_id}) Test")
        return response.status_code == 200
    
    def test_get_render_status(self, project_id: str):
        """Test getting render status"""
        response = self.session.get(f"{self.base_url}/projects/{project_id}/status")
        self.print_response(response, f"Get Render Status ({project_id}) Test")
        return response.status_code == 200
    
    def test_get_public_projects(self):
        """Test getting public projects"""
        response = self.session.get(f"{self.base_url}/projects/public/showcase")
        self.print_response(response, "Get Public Projects Test")
        return response.status_code == 200
    
    def test_debug_activate_templates(self):
        """Test debug activate templates"""
        response = self.session.post(f"{self.base_url}/debug/activate-templates")
        self.print_response(response, "Debug Activate Templates Test")
        return response.status_code == 200
    
    def test_debug_template_status(self):
        """Test debug template status"""
        response = self.session.get(f"{self.base_url}/debug/template-status")
        self.print_response(response, "Debug Template Status Test")
        return response.status_code == 200
    
    def run_full_test(self):
        """Run complete API test suite"""
        print("Starting Video Template Platform API Test Suite")
        print("=" * 60)
        
        # Test data
        user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        project_data = {
            "template_id": "tmpl-newspaper",
            "name": "My Breaking News Video",
            "description": "A breaking news video about local events",
            "parameters": {
                "headline": "Breaking: Major Event in City",
                "subheadline": "Local authorities respond to emergency situation",
                "image_url": "https://example.com/news-image.jpg",
                "theme_color": "#FF0000",
                "reporter_name": "John Smith"
            },
            "render_quality": "1080p"
        }
        
        update_data = {
            "name": "Updated Breaking News Video",
            "description": "Updated description",
            "parameters": {
                "headline": "Updated: Major Event in City",
                "subheadline": "Updated subheadline",
                "image_url": "https://example.com/updated-image.jpg",
                "theme_color": "#FF0000",
                "reporter_name": "John Smith"
            },
            "render_quality": "4k",
            "is_public": True
        }
        
        # Test results
        results = []
        
        # 1. Test general endpoints
        results.append(("Root Endpoint", self.test_root_endpoint()))
        results.append(("Health Check", self.test_health_check()))
        
        # 2. Test debug endpoints
        results.append(("Debug Template Status", self.test_debug_template_status()))
        results.append(("Debug Activate Templates", self.test_debug_activate_templates()))
        
        # 3. Test authentication
        results.append(("User Registration", self.test_register_user(user_data)))
        results.append(("User Login", self.test_login("testuser", "testpassword123")))
        results.append(("Get Current User", self.test_get_current_user()))
        
        # 4. Test template endpoints
        results.append(("Get All Templates", self.test_get_all_templates()))
        results.append(("Get Template Categories", self.test_get_template_categories()))
        results.append(("Get Templates by Category (News)", self.test_get_templates_by_category("News")))
        results.append(("Get Template by ID", self.test_get_template_by_id("tmpl-newspaper")))
        results.append(("Save Template", self.test_save_template("tmpl-newspaper")))
        results.append(("Get Saved Templates", self.test_get_saved_templates()))
        results.append(("Search Templates", self.test_search_templates("news")))
        
        # 5. Test project endpoints
        project_id = self.test_create_project(project_data)
        if project_id:
            results.append(("Create Project", True))
            results.append(("Get User Projects", self.test_get_user_projects()))
            results.append(("Get Project by ID", self.test_get_project_by_id(project_id)))
            results.append(("Update Project", self.test_update_project(project_id, update_data)))
            results.append(("Render Project", self.test_render_project(project_id)))
            
            # Wait a bit for render to process
            print("\nWaiting 3 seconds for render to process...")
            time.sleep(3)
            
            results.append(("Get Render Status", self.test_get_render_status(project_id)))
        else:
            results.append(("Create Project", False))
        
        # 6. Test public endpoints
        results.append(("Get Public Projects", self.test_get_public_projects()))
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        return passed == total

def main():
    """Main function to run the test suite"""
    tester = APITester()
    
    try:
        success = tester.run_full_test()
        if success:
            print("\n🎉 All tests passed!")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 