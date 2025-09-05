#!/usr/bin/env python3
"""
Comprehensive Backend Test Suite for URL Screenshot API
Tests all backend functionality including API key management, authentication, and screenshot capture.
"""

import requests
import json
import base64
import time
from datetime import datetime
import sys
import os

# Get backend URL from environment
BACKEND_URL = "https://webshot-api.preview.emergentagent.com/api"

class ScreenshotAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.api_key = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def test_api_health(self):
        """Test basic API health check"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "status" in data:
                    self.log_test("API Health Check", True, "API is responding correctly")
                    return True
                else:
                    self.log_test("API Health Check", False, "API response missing expected fields", data)
                    return False
            else:
                self.log_test("API Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Connection failed: {str(e)}")
            return False
    
    def test_create_api_key(self):
        """Test API key creation"""
        try:
            payload = {"name": "Test API Key"}
            response = requests.post(f"{self.base_url}/api-keys", json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "key", "name", "created_at", "is_active", "usage_count"]
                
                if all(field in data for field in required_fields):
                    self.api_key = data["key"]  # Store for later tests
                    self.log_test("Create API Key", True, f"API key created successfully: {data['key'][:8]}...")
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Create API Key", False, f"Missing fields: {missing}", data)
                    return False
            else:
                self.log_test("Create API Key", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Create API Key", False, f"Request failed: {str(e)}")
            return False
    
    def test_list_api_keys(self):
        """Test listing API keys"""
        try:
            response = requests.get(f"{self.base_url}/api-keys", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        # Check if our created key is in the list
                        key_found = any(key.get("key") == self.api_key for key in data if self.api_key)
                        if key_found or not self.api_key:
                            self.log_test("List API Keys", True, f"Retrieved {len(data)} API keys")
                            return True
                        else:
                            self.log_test("List API Keys", False, "Created API key not found in list")
                            return False
                    else:
                        self.log_test("List API Keys", True, "No API keys found (empty list)")
                        return True
                else:
                    self.log_test("List API Keys", False, "Response is not a list", data)
                    return False
            else:
                self.log_test("List API Keys", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("List API Keys", False, f"Request failed: {str(e)}")
            return False
    
    def test_screenshot_without_auth(self):
        """Test screenshot endpoint without authentication"""
        try:
            payload = {
                "url": "https://example.com",
                "options": {"width": 1280, "height": 720}
            }
            response = requests.post(f"{self.base_url}/v1/screenshot", json=payload, timeout=30)
            
            if response.status_code == 401:
                self.log_test("Screenshot Without Auth", True, "Correctly rejected unauthenticated request")
                return True
            else:
                self.log_test("Screenshot Without Auth", False, f"Expected 401, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Screenshot Without Auth", False, f"Request failed: {str(e)}")
            return False
    
    def test_screenshot_invalid_auth(self):
        """Test screenshot endpoint with invalid authentication"""
        try:
            payload = {
                "url": "https://example.com",
                "options": {"width": 1280, "height": 720}
            }
            headers = {"Authorization": "Bearer invalid-key-12345"}
            response = requests.post(f"{self.base_url}/v1/screenshot", json=payload, headers=headers, timeout=30)
            
            if response.status_code == 401:
                self.log_test("Screenshot Invalid Auth", True, "Correctly rejected invalid API key")
                return True
            else:
                self.log_test("Screenshot Invalid Auth", False, f"Expected 401, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Screenshot Invalid Auth", False, f"Request failed: {str(e)}")
            return False
    
    def test_basic_screenshot(self):
        """Test basic screenshot capture with PNG format"""
        if not self.api_key:
            self.log_test("Basic Screenshot", False, "No API key available for testing")
            return False
            
        try:
            payload = {
                "url": "https://example.com",
                "options": {
                    "width": 1280,
                    "height": 720,
                    "format": "png",
                    "fullPage": False
                }
            }
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(f"{self.base_url}/v1/screenshot", json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["status", "image", "format", "timestamp", "url"]
                
                if all(field in data for field in required_fields):
                    # Verify image data
                    if data["image"].startswith("data:image/png;base64,"):
                        # Try to decode base64 to verify it's valid
                        try:
                            base64_data = data["image"].split(",")[1]
                            base64.b64decode(base64_data)
                            self.log_test("Basic Screenshot", True, f"PNG screenshot captured successfully ({len(base64_data)} chars)")
                            return True
                        except Exception as decode_error:
                            self.log_test("Basic Screenshot", False, f"Invalid base64 image data: {str(decode_error)}")
                            return False
                    else:
                        self.log_test("Basic Screenshot", False, "Image data format incorrect", data["image"][:100])
                        return False
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_test("Basic Screenshot", False, f"Missing fields: {missing}", data)
                    return False
            else:
                self.log_test("Basic Screenshot", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Basic Screenshot", False, f"Request failed: {str(e)}")
            return False
    
    def test_jpeg_screenshot(self):
        """Test JPEG screenshot with quality setting"""
        if not self.api_key:
            self.log_test("JPEG Screenshot", False, "No API key available for testing")
            return False
            
        try:
            payload = {
                "url": "https://httpbin.org/html",
                "options": {
                    "width": 1920,
                    "height": 1080,
                    "format": "jpeg",
                    "quality": 85,
                    "fullPage": False
                }
            }
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(f"{self.base_url}/v1/screenshot", json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("format") == "jpeg" and data["image"].startswith("data:image/jpeg;base64,"):
                    try:
                        base64_data = data["image"].split(",")[1]
                        base64.b64decode(base64_data)
                        self.log_test("JPEG Screenshot", True, f"JPEG screenshot captured with quality 85 ({len(base64_data)} chars)")
                        return True
                    except Exception as decode_error:
                        self.log_test("JPEG Screenshot", False, f"Invalid base64 image data: {str(decode_error)}")
                        return False
                else:
                    self.log_test("JPEG Screenshot", False, "Incorrect format or image data", data.get("format"))
                    return False
            else:
                self.log_test("JPEG Screenshot", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("JPEG Screenshot", False, f"Request failed: {str(e)}")
            return False
    
    def test_full_page_screenshot(self):
        """Test full page screenshot"""
        if not self.api_key:
            self.log_test("Full Page Screenshot", False, "No API key available for testing")
            return False
            
        try:
            payload = {
                "url": "https://httpbin.org/html",
                "options": {
                    "width": 1280,
                    "height": 720,
                    "format": "png",
                    "fullPage": True
                }
            }
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(f"{self.base_url}/v1/screenshot", json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                if data["image"].startswith("data:image/png;base64,"):
                    base64_data = data["image"].split(",")[1]
                    self.log_test("Full Page Screenshot", True, f"Full page screenshot captured ({len(base64_data)} chars)")
                    return True
                else:
                    self.log_test("Full Page Screenshot", False, "Invalid image data format")
                    return False
            else:
                self.log_test("Full Page Screenshot", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Full Page Screenshot", False, f"Request failed: {str(e)}")
            return False
    
    def test_screenshot_with_delay(self):
        """Test screenshot with delay"""
        if not self.api_key:
            self.log_test("Screenshot with Delay", False, "No API key available for testing")
            return False
            
        try:
            start_time = time.time()
            payload = {
                "url": "https://httpbin.org/delay/2",
                "options": {
                    "width": 1280,
                    "height": 720,
                    "format": "png",
                    "delay": 3000  # 3 seconds
                }
            }
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(f"{self.base_url}/v1/screenshot", json=payload, headers=headers, timeout=90)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                duration = end_time - start_time
                if data["image"].startswith("data:image/png;base64,") and duration >= 3:
                    self.log_test("Screenshot with Delay", True, f"Screenshot with 3s delay completed in {duration:.1f}s")
                    return True
                else:
                    self.log_test("Screenshot with Delay", False, f"Delay not respected or invalid image (duration: {duration:.1f}s)")
                    return False
            else:
                self.log_test("Screenshot with Delay", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Screenshot with Delay", False, f"Request failed: {str(e)}")
            return False
    
    def test_invalid_url(self):
        """Test screenshot with invalid URL"""
        if not self.api_key:
            self.log_test("Invalid URL Test", False, "No API key available for testing")
            return False
            
        try:
            payload = {
                "url": "not-a-valid-url",
                "options": {"width": 1280, "height": 720}
            }
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(f"{self.base_url}/v1/screenshot", json=payload, headers=headers, timeout=30)
            
            if response.status_code == 422:  # Validation error
                self.log_test("Invalid URL Test", True, "Correctly rejected invalid URL format")
                return True
            else:
                self.log_test("Invalid URL Test", False, f"Expected 422, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Invalid URL Test", False, f"Request failed: {str(e)}")
            return False
    
    def test_viewport_sizes(self):
        """Test different viewport sizes"""
        if not self.api_key:
            self.log_test("Viewport Sizes Test", False, "No API key available for testing")
            return False
            
        test_sizes = [
            (800, 600),   # Small
            (1920, 1080), # Full HD
            (2560, 1440)  # 2K
        ]
        
        success_count = 0
        for width, height in test_sizes:
            try:
                payload = {
                    "url": "https://example.com",
                    "options": {
                        "width": width,
                        "height": height,
                        "format": "png"
                    }
                }
                headers = {"Authorization": f"Bearer {self.api_key}"}
                response = requests.post(f"{self.base_url}/v1/screenshot", json=payload, headers=headers, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    if data["image"].startswith("data:image/png;base64,"):
                        success_count += 1
                        print(f"   ✓ {width}x{height} viewport successful")
                    else:
                        print(f"   ✗ {width}x{height} viewport failed - invalid image")
                else:
                    print(f"   ✗ {width}x{height} viewport failed - HTTP {response.status_code}")
            except Exception as e:
                print(f"   ✗ {width}x{height} viewport failed - {str(e)}")
        
        if success_count == len(test_sizes):
            self.log_test("Viewport Sizes Test", True, f"All {len(test_sizes)} viewport sizes worked correctly")
            return True
        else:
            self.log_test("Viewport Sizes Test", False, f"Only {success_count}/{len(test_sizes)} viewport sizes worked")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting URL Screenshot API Backend Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Test sequence
        tests = [
            self.test_api_health,
            self.test_create_api_key,
            self.test_list_api_keys,
            self.test_screenshot_without_auth,
            self.test_screenshot_invalid_auth,
            self.test_basic_screenshot,
            self.test_jpeg_screenshot,
            self.test_full_page_screenshot,
            self.test_screenshot_with_delay,
            self.test_invalid_url,
            self.test_viewport_sizes
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ FAIL: {test.__name__} - Unexpected error: {str(e)}")
                failed += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"Total Tests: {passed + failed}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        if self.api_key:
            print(f"🔑 API Key Used: {self.api_key[:8]}...")
        
        return passed, failed, self.test_results

if __name__ == "__main__":
    tester = ScreenshotAPITester()
    passed, failed, results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    sys.exit(0 if failed == 0 else 1)