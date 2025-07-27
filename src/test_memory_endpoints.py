#!/usr/bin/env python3
"""
Comprehensive test script for Eliza's long-term memory endpoints.
Tests all new memory API endpoints to ensure they work correctly.
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any

# Test configuration
BASE_URL = "http://localhost:5000/api/eliza"
TEST_USER_ID = "test_user_123"
TEST_SESSION_ID = "test_session_456"

class MemoryEndpointTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.stored_memory_ids = []
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()
    
    def test_store_memory_endpoint(self):
        """Test the /memory/store endpoint"""
        print("🧠 Testing Memory Store Endpoint...")
        
        # Test 1: Store a basic memory
        test_data = {
            "user_id": TEST_USER_ID,
            "content": "User prefers Python programming over JavaScript",
            "memory_type": "preference",
            "metadata": {"confidence": 0.9, "source": "conversation"}
        }
        
        try:
            response = self.session.post(f"{self.base_url}/memory/store", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data', {}).get('memory_id'):
                    memory_id = data['data']['memory_id']
                    self.stored_memory_ids.append(memory_id)
                    self.log_test("Store Basic Memory", True, f"Memory ID: {memory_id}")
                else:
                    self.log_test("Store Basic Memory", False, "No memory ID returned", data)
            else:
                self.log_test("Store Basic Memory", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Store Basic Memory", False, f"Exception: {str(e)}")
        
        # Test 2: Store memory with different types
        memory_types = ["factual", "contextual", "emotional", "temporal"]
        for mem_type in memory_types:
            test_data = {
                "user_id": TEST_USER_ID,
                "content": f"Test {mem_type} memory content about user behavior",
                "memory_type": mem_type,
                "metadata": {"test": True, "type": mem_type}
            }
            
            try:
                response = self.session.post(f"{self.base_url}/memory/store", json=test_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('data', {}).get('memory_id'):
                        memory_id = data['data']['memory_id']
                        self.stored_memory_ids.append(memory_id)
                        self.log_test(f"Store {mem_type.title()} Memory", True, f"Memory ID: {memory_id}")
                    else:
                        self.log_test(f"Store {mem_type.title()} Memory", False, "No memory ID returned", data)
                else:
                    self.log_test(f"Store {mem_type.title()} Memory", False, f"HTTP {response.status_code}", response.text)
            except Exception as e:
                self.log_test(f"Store {mem_type.title()} Memory", False, f"Exception: {str(e)}")
        
        # Test 3: Test invalid memory type
        test_data = {
            "user_id": TEST_USER_ID,
            "content": "Test invalid memory type",
            "memory_type": "invalid_type"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/memory/store", json=test_data)
            
            if response.status_code == 400:
                self.log_test("Store Invalid Memory Type", True, "Correctly rejected invalid type")
            else:
                self.log_test("Store Invalid Memory Type", False, f"Should have returned 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Store Invalid Memory Type", False, f"Exception: {str(e)}")
        
        # Test 4: Test missing content
        test_data = {
            "user_id": TEST_USER_ID,
            "memory_type": "general"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/memory/store", json=test_data)
            
            if response.status_code == 400:
                self.log_test("Store Missing Content", True, "Correctly rejected missing content")
            else:
                self.log_test("Store Missing Content", False, f"Should have returned 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Store Missing Content", False, f"Exception: {str(e)}")
    
    def test_search_memory_endpoint(self):
        """Test the /memory/search endpoint"""
        print("🔍 Testing Memory Search Endpoint...")
        
        # Test 1: Basic search
        test_data = {
            "user_id": TEST_USER_ID,
            "query": "Python programming",
            "limit": 5
        }
        
        try:
            response = self.session.post(f"{self.base_url}/memory/search", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'memories' in data.get('data', {}):
                    memories = data['data']['memories']
                    self.log_test("Basic Memory Search", True, f"Found {len(memories)} memories")
                else:
                    self.log_test("Basic Memory Search", False, "No memories in response", data)
            else:
                self.log_test("Basic Memory Search", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Basic Memory Search", False, f"Exception: {str(e)}")
        
        # Test 2: Search by memory type
        test_data = {
            "user_id": TEST_USER_ID,
            "query": "test",
            "memory_type": "preference",
            "limit": 10
        }
        
        try:
            response = self.session.post(f"{self.base_url}/memory/search", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    memories = data['data']['memories']
                    self.log_test("Search by Memory Type", True, f"Found {len(memories)} preference memories")
                else:
                    self.log_test("Search by Memory Type", False, "Search failed", data)
            else:
                self.log_test("Search by Memory Type", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Search by Memory Type", False, f"Exception: {str(e)}")
        
        # Test 3: Search with invalid memory type
        test_data = {
            "user_id": TEST_USER_ID,
            "query": "test",
            "memory_type": "invalid_type"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/memory/search", json=test_data)
            
            if response.status_code == 400:
                self.log_test("Search Invalid Memory Type", True, "Correctly rejected invalid type")
            else:
                self.log_test("Search Invalid Memory Type", False, f"Should have returned 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Search Invalid Memory Type", False, f"Exception: {str(e)}")
        
        # Test 4: Search without query
        test_data = {
            "user_id": TEST_USER_ID
        }
        
        try:
            response = self.session.post(f"{self.base_url}/memory/search", json=test_data)
            
            if response.status_code == 400:
                self.log_test("Search Missing Query", True, "Correctly rejected missing query")
            else:
                self.log_test("Search Missing Query", False, f"Should have returned 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Search Missing Query", False, f"Exception: {str(e)}")
    
    def test_associations_endpoint(self):
        """Test the /memory/associations endpoint"""
        print("🔗 Testing Memory Associations Endpoint...")
        
        if not self.stored_memory_ids:
            self.log_test("Memory Associations", False, "No stored memories to test associations")
            return
        
        memory_id = self.stored_memory_ids[0]
        
        # Test 1: Get associations for a memory
        try:
            response = self.session.get(f"{self.base_url}/memory/associations", 
                                      params={"memory_id": memory_id, "user_id": TEST_USER_ID})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'associations' in data.get('data', {}):
                    associations = data['data']['associations']
                    self.log_test("Get Memory Associations", True, f"Found {len(associations)} associations")
                else:
                    self.log_test("Get Memory Associations", False, "No associations in response", data)
            else:
                self.log_test("Get Memory Associations", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Get Memory Associations", False, f"Exception: {str(e)}")
        
        # Test 2: Get associations with specific type
        try:
            response = self.session.get(f"{self.base_url}/memory/associations", 
                                      params={"memory_id": memory_id, "association_type": "related"})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    associations = data['data']['associations']
                    self.log_test("Get Typed Associations", True, f"Found {len(associations)} related associations")
                else:
                    self.log_test("Get Typed Associations", False, "Request failed", data)
            else:
                self.log_test("Get Typed Associations", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Get Typed Associations", False, f"Exception: {str(e)}")
        
        # Test 3: Test missing memory ID
        try:
            response = self.session.get(f"{self.base_url}/memory/associations")
            
            if response.status_code == 400:
                self.log_test("Associations Missing Memory ID", True, "Correctly rejected missing memory ID")
            else:
                self.log_test("Associations Missing Memory ID", False, f"Should have returned 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Associations Missing Memory ID", False, f"Exception: {str(e)}")
        
        # Test 4: Test invalid association type
        try:
            response = self.session.get(f"{self.base_url}/memory/associations", 
                                      params={"memory_id": memory_id, "association_type": "invalid_type"})
            
            if response.status_code == 400:
                self.log_test("Invalid Association Type", True, "Correctly rejected invalid association type")
            else:
                self.log_test("Invalid Association Type", False, f"Should have returned 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Association Type", False, f"Exception: {str(e)}")
    
    def test_analytics_endpoint(self):
        """Test the /memory/analytics endpoint"""
        print("📊 Testing Memory Analytics Endpoint...")
        
        # Test 1: Get basic analytics
        try:
            response = self.session.get(f"{self.base_url}/memory/analytics", 
                                      params={"user_id": TEST_USER_ID})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    analytics = data['data']
                    expected_fields = ['total_memories', 'memory_types', 'recent_memories_30d', 
                                     'conversation_entries', 'memory_associations']
                    
                    has_all_fields = all(field in analytics for field in expected_fields)
                    if has_all_fields:
                        self.log_test("Memory Analytics", True, 
                                    f"Total memories: {analytics.get('total_memories', 0)}")
                    else:
                        missing = [f for f in expected_fields if f not in analytics]
                        self.log_test("Memory Analytics", False, f"Missing fields: {missing}", analytics)
                else:
                    self.log_test("Memory Analytics", False, "No analytics data in response", data)
            else:
                self.log_test("Memory Analytics", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Memory Analytics", False, f"Exception: {str(e)}")
        
        # Test 2: Analytics with custom days parameter
        try:
            response = self.session.get(f"{self.base_url}/memory/analytics", 
                                      params={"user_id": TEST_USER_ID, "days": 7})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Analytics with Days Parameter", True, "Successfully got 7-day analytics")
                else:
                    self.log_test("Analytics with Days Parameter", False, "Request failed", data)
            else:
                self.log_test("Analytics with Days Parameter", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Analytics with Days Parameter", False, f"Exception: {str(e)}")
    
    def test_prune_endpoint(self):
        """Test the /memory/prune endpoint"""
        print("🧹 Testing Memory Prune Endpoint...")
        
        # Test 1: Dry run prune
        test_data = {
            "user_id": TEST_USER_ID,
            "days_old": 1,  # Very recent to test without actually deleting
            "dry_run": True
        }
        
        try:
            response = self.session.post(f"{self.base_url}/memory/prune", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    prune_result = data['data']
                    self.log_test("Memory Prune Dry Run", True, 
                                f"Would prune {prune_result.get('would_prune', 0)} memories")
                else:
                    self.log_test("Memory Prune Dry Run", False, "No prune data in response", data)
            else:
                self.log_test("Memory Prune Dry Run", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Memory Prune Dry Run", False, f"Exception: {str(e)}")
        
        # Test 2: Prune with memory type filter
        test_data = {
            "user_id": TEST_USER_ID,
            "days_old": 365,
            "memory_type": "temporal",
            "dry_run": True
        }
        
        try:
            response = self.session.post(f"{self.base_url}/memory/prune", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log_test("Prune with Memory Type", True, "Successfully tested type-filtered pruning")
                else:
                    self.log_test("Prune with Memory Type", False, "Request failed", data)
            else:
                self.log_test("Prune with Memory Type", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Prune with Memory Type", False, f"Exception: {str(e)}")
        
        # Test 3: Test invalid memory type
        test_data = {
            "user_id": TEST_USER_ID,
            "memory_type": "invalid_type",
            "dry_run": True
        }
        
        try:
            response = self.session.post(f"{self.base_url}/memory/prune", json=test_data)
            
            if response.status_code == 400:
                self.log_test("Prune Invalid Memory Type", True, "Correctly rejected invalid memory type")
            else:
                self.log_test("Prune Invalid Memory Type", False, f"Should have returned 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Prune Invalid Memory Type", False, f"Exception: {str(e)}")
    
    def test_chat_endpoint_with_memory(self):
        """Test that the chat endpoint properly integrates with memory"""
        print("💬 Testing Chat Endpoint Memory Integration...")
        
        # Test 1: Send a message that should be stored in memory
        test_data = {
            "message": "I really enjoy working with machine learning algorithms, especially neural networks",
            "context": {"session_id": TEST_SESSION_ID}
        }
        
        try:
            response = self.session.post(f"{self.base_url}/chat", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('response'):
                    self.log_test("Chat with Memory Storage", True, "Chat response received")
                    
                    # Wait a moment for memory to be stored
                    time.sleep(1)
                    
                    # Search for the stored memory
                    search_data = {
                        "user_id": "eliza_user",  # Default user ID used in chat
                        "query": "machine learning",
                        "limit": 5
                    }
                    
                    search_response = self.session.post(f"{self.base_url}/memory/search", json=search_data)
                    if search_response.status_code == 200:
                        search_result = search_response.json()
                        if search_result.get('success'):
                            memories = search_result['data']['memories']
                            found_memory = any("machine learning" in str(memory).lower() for memory in memories)
                            if found_memory:
                                self.log_test("Memory Storage from Chat", True, "Chat message stored in memory")
                            else:
                                self.log_test("Memory Storage from Chat", False, "Chat message not found in memory")
                        else:
                            self.log_test("Memory Storage from Chat", False, "Memory search failed")
                    else:
                        self.log_test("Memory Storage from Chat", False, "Could not search memories")
                else:
                    self.log_test("Chat with Memory Storage", False, "No chat response", data)
            else:
                self.log_test("Chat with Memory Storage", False, f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Chat with Memory Storage", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all memory endpoint tests"""
        print("🚀 Starting Comprehensive Memory Endpoint Tests")
        print("=" * 60)
        
        # Test all endpoints
        self.test_store_memory_endpoint()
        self.test_search_memory_endpoint()
        self.test_associations_endpoint()
        self.test_analytics_endpoint()
        self.test_prune_endpoint()
        self.test_chat_endpoint_with_memory()
        
        # Summary
        print("📋 Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details']}")
        
        return passed_tests, failed_tests
    
    def save_test_report(self, filename: str = "memory_test_report.json"):
        """Save detailed test report to file"""
        report = {
            'test_run_timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'test_user_id': TEST_USER_ID,
            'total_tests': len(self.test_results),
            'passed_tests': sum(1 for r in self.test_results if r['success']),
            'failed_tests': sum(1 for r in self.test_results if not r['success']),
            'test_results': self.test_results
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed test report saved to: {filename}")


def main():
    """Main test execution"""
    print("🧠 Eliza Long-Term Memory Endpoint Tester")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=5)
        if response.status_code != 200:
            print("❌ Error: Eliza server is not responding properly")
            print("Please make sure the Flask application is running on localhost:5000")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Error: Cannot connect to Eliza server")
        print("Please make sure the Flask application is running on localhost:5000")
        sys.exit(1)
    
    print("✅ Server is running, starting tests...\n")
    
    # Run tests
    tester = MemoryEndpointTester(BASE_URL)
    passed, failed = tester.run_all_tests()
    
    # Save report
    tester.save_test_report()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()

