#!/usr/bin/env python3
"""
Test script for FastAPI backend server
Run this to test your backend server functionality
"""

import asyncio
import sys
import requests
import json
import time
from typing import Dict, Any, Optional
from app.config import settings


class BackendTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {}
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if message:
            print(f"   {message}")
        self.test_results[test_name] = success
        return success

    def test_server_health(self) -> bool:
        """Test server health endpoint"""
        print("\n🔍 Testing server health...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check successful: {data}")
                return self.log_test("Server Health", True, f"Status: {data.get('status')}")
            else:
                return self.log_test("Server Health", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Server Health", False, f"Error: {e}")

    def test_server_info(self) -> bool:
        """Test server info endpoint"""
        print("\n🔍 Testing server info...")
        
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server info: {data}")
                return self.log_test("Server Info", True, f"Title: {data.get('title')}")
            else:
                return self.log_test("Server Info", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Server Info", False, f"Error: {e}")

    def test_database_connection(self) -> bool:
        """Test database connection endpoint"""
        print("\n🔍 Testing database connection...")
        
        try:
            response = self.session.get(f"{self.base_url}/health/db")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Database health: {data}")
                return self.log_test("Database Connection", True, f"Status: {data.get('status')}")
            else:
                return self.log_test("Database Connection", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Database Connection", False, f"Error: {e}")

    def test_redis_connection(self) -> bool:
        """Test Redis connection endpoint"""
        print("\n🔍 Testing Redis connection...")
        
        try:
            response = self.session.get(f"{self.base_url}/health/redis")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Redis health: {data}")
                return self.log_test("Redis Connection", True, f"Status: {data.get('status')}")
            else:
                return self.log_test("Redis Connection", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Redis Connection", False, f"Error: {e}")

    def test_api_docs(self) -> bool:
        """Test API documentation endpoints"""
        print("\n🔍 Testing API documentation...")
        
        endpoints = [
            "/docs",
            "/redoc", 
            "/openapi.json"
        ]
        
        all_success = True
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    print(f"✅ {endpoint}: Available")
                else:
                    print(f"❌ {endpoint}: Status {response.status_code}")
                    all_success = False
                    
            except Exception as e:
                print(f"❌ {endpoint}: Error - {e}")
                all_success = False
        
        return self.log_test("API Documentation", all_success)

    def test_evaluation_endpoints(self) -> bool:
        """Test evaluation API endpoints"""
        print("\n🔍 Testing evaluation endpoints...")
        
        # Test data for evaluation
        test_evaluation = {
            "experiment_run_id": "test-run-123",
            "evaluator_configs": [
                {
                    "evaluator_type": "exact_match",
                    "config": {
                        "case_sensitive": False,
                        "strip_whitespace": True
                    }
                },
                {
                    "evaluator_type": "latency",
                    "config": {
                        "max_latency_ms": 1000
                    }
                }
            ],
            "test_cases": [
                {
                    "input": "What is the capital of France?",
                    "expected_output": "Paris",
                    "actual_output": "Paris"
                },
                {
                    "input": "What is 2+2?",
                    "expected_output": "4",
                    "actual_output": "4"
                }
            ]
        }
        
        try:
            # Test submit evaluation
            response = self.session.post(
                f"{self.base_url}/evaluations/submit",
                json=test_evaluation,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                job_id = data.get("job_id")
                print(f"✅ Submit evaluation successful: {job_id}")
                
                # Test get job status
                if job_id:
                    status_response = self.session.get(f"{self.base_url}/evaluations/jobs/{job_id}/status")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"✅ Job status: {status_data.get('status')}")
                        
                        # Test get job progress
                        progress_response = self.session.get(f"{self.base_url}/evaluations/jobs/{job_id}/progress")
                        if progress_response.status_code == 200:
                            progress_data = progress_response.json()
                            print(f"✅ Job progress: {progress_data}")
                            
                            # Test get job results (if completed)
                            if status_data.get('status') == 'completed':
                                results_response = self.session.get(f"{self.base_url}/evaluations/jobs/{job_id}/results")
                                if results_response.status_code == 200:
                                    results_data = results_response.json()
                                    print(f"✅ Job results: {len(results_data.get('results', []))} results")
                
                return self.log_test("Evaluation Endpoints", True, f"Job ID: {job_id}")
            else:
                return self.log_test("Evaluation Endpoints", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Evaluation Endpoints", False, f"Error: {e}")

    def test_websocket_connection(self) -> bool:
        """Test WebSocket connection"""
        print("\n🔍 Testing WebSocket connection...")
        
        try:
            import websocket
            
            # Test WebSocket connection
            ws_url = self.base_url.replace("http", "ws") + "/ws"
            
            def on_message(ws, message):
                print(f"✅ WebSocket message received: {message}")
                
            def on_error(ws, error):
                print(f"❌ WebSocket error: {error}")
                
            def on_close(ws, close_status_code, close_msg):
                print("🔌 WebSocket connection closed")
                
            def on_open(ws):
                print("🔌 WebSocket connection opened")
                ws.send(json.dumps({"type": "ping", "data": "test"}))
                time.sleep(1)
                ws.close()
            
            ws = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run WebSocket in a separate thread
            import threading
            wst = threading.Thread(target=ws.run_forever)
            wst.daemon = True
            wst.start()
            
            # Wait for connection
            time.sleep(2)
            
            return self.log_test("WebSocket Connection", True)
            
        except ImportError:
            return self.log_test("WebSocket Connection", False, "websocket-client not installed")
        except Exception as e:
            return self.log_test("WebSocket Connection", False, f"Error: {e}")

    def test_cors_headers(self) -> bool:
        """Test CORS headers"""
        print("\n🔍 Testing CORS headers...")
        
        try:
            response = self.session.options(f"{self.base_url}/health")
            
            cors_headers = response.headers.get("Access-Control-Allow-Origin")
            if cors_headers:
                print(f"✅ CORS headers present: {cors_headers}")
                return self.log_test("CORS Headers", True, f"Origin: {cors_headers}")
            else:
                return self.log_test("CORS Headers", False, "No CORS headers found")
                
        except Exception as e:
            return self.log_test("CORS Headers", False, f"Error: {e}")

    def test_error_handling(self) -> bool:
        """Test error handling"""
        print("\n🔍 Testing error handling...")
        
        try:
            # Test 404 endpoint
            response = self.session.get(f"{self.base_url}/nonexistent")
            
            if response.status_code == 404:
                print("✅ 404 error handling works")
                return self.log_test("Error Handling", True, "404 handled correctly")
            else:
                return self.log_test("Error Handling", False, f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            return self.log_test("Error Handling", False, f"Error: {e}")

    def test_server_performance(self) -> bool:
        """Test basic server performance"""
        print("\n🔍 Testing server performance...")
        
        try:
            start_time = time.time()
            
            # Make multiple requests
            for i in range(5):
                response = self.session.get(f"{self.base_url}/health")
                if response.status_code != 200:
                    return self.log_test("Server Performance", False, f"Request {i+1} failed")
            
            end_time = time.time()
            avg_time = (end_time - start_time) / 5
            
            print(f"✅ Average response time: {avg_time:.3f}s")
            return self.log_test("Server Performance", True, f"Avg time: {avg_time:.3f}s")
            
        except Exception as e:
            return self.log_test("Server Performance", False, f"Error: {e}")

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests"""
        print("🚀 Starting Backend Server Tests")
        print("=" * 60)
        print(f"Testing server at: {self.base_url}")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_server_health,
            self.test_server_info,
            self.test_database_connection,
            self.test_redis_connection,
            self.test_api_docs,
            self.test_evaluation_endpoints,
            self.test_cors_headers,
            self.test_error_handling,
            self.test_server_performance,
        ]
        
        # Add WebSocket test if websocket-client is available
        try:
            import websocket
            tests.append(self.test_websocket_connection)
        except ImportError:
            print("⚠️  websocket-client not installed, skipping WebSocket test")
        
        for test in tests:
            test()
        
        return self.test_results

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📋 Test Summary:")
        print("=" * 60)
        
        passed = sum(1 for success in self.test_results.values() if success)
        total = len(self.test_results)
        
        for test_name, success in self.test_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name:<25} {status}")
        
        print("-" * 60)
        print(f"Total: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed! Backend server is working correctly.")
            return True
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please check your server configuration.")
            return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test FastAPI backend server")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL of the server (default: http://localhost:8000)")
    parser.add_argument("--timeout", type=int, default=30,
                       help="Request timeout in seconds (default: 30)")
    
    args = parser.parse_args()
    
    # Create tester
    tester = BackendTester(args.url)
    tester.session.timeout = args.timeout
    
    # Run tests
    results = tester.run_all_tests()
    
    # Print summary
    success = tester.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 