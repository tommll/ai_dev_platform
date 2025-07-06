#!/usr/bin/env python3
"""
Simple backend server test
Quick test to verify your FastAPI backend server
"""

import requests
import sys
from app.config import settings


def test_server_health():
    """Test server health endpoint"""
    print("🔍 Testing server health...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy: {data}")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_server_info():
    """Test server info endpoint"""
    print("\n🔍 Testing server info...")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server info: {data.get('title', 'Unknown')}")
            return True
        else:
            print(f"❌ Server info failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Server info error: {e}")
        return False


def test_database_health():
    """Test database health endpoint"""
    print("\n🔍 Testing database health...")
    
    try:
        response = requests.get("http://localhost:8000/health/db", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database is healthy: {data.get('status', 'Unknown')}")
            return True
        else:
            print(f"❌ Database health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Database health error: {e}")
        return False


def test_redis_health():
    """Test Redis health endpoint"""
    print("\n🔍 Testing Redis health...")
    
    try:
        response = requests.get("http://localhost:8000/health/redis", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Redis is healthy: {data.get('status', 'Unknown')}")
            return True
        else:
            print(f"❌ Redis health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Redis health error: {e}")
        return False


def test_api_docs():
    """Test API documentation"""
    print("\n🔍 Testing API documentation...")
    
    try:
        response = requests.get("http://localhost:8000/docs", timeout=10)
        
        if response.status_code == 200:
            print("✅ API documentation is available")
            return True
        else:
            print(f"❌ API documentation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API docs error: {e}")
        return False


def test_basic_evaluation():
    """Test basic evaluation endpoint"""
    print("\n🔍 Testing evaluation endpoint...")
    
    test_data = {
        "experiment_run_id": "test-run-123",
        "evaluator_configs": [
            {
                "evaluator_type": "exact_match",
                "config": {"case_sensitive": False}
            }
        ],
        "test_cases": [
            {
                "input": "Hello",
                "expected_output": "Hello",
                "actual_output": "Hello"
            }
        ]
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/evaluations/submit",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get("job_id")
            print(f"✅ Evaluation submitted successfully: {job_id}")
            return True
        else:
            print(f"❌ Evaluation submission failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Evaluation error: {e}")
        return False


def main():
    """Run all quick tests"""
    print("🚀 Quick Backend Server Tests")
    print("=" * 50)
    print("Testing server at: http://localhost:8000")
    print("=" * 50)
    
    tests = [
        ("Server Health", test_server_health),
        ("Server Info", test_server_info),
        ("Database Health", test_database_health),
        ("Redis Health", test_redis_health),
        ("API Documentation", test_api_docs),
        ("Evaluation Endpoint", test_basic_evaluation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Quick Test Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if success:
            passed += 1
    
    print("-" * 50)
    print(f"Total: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Backend server is working correctly.")
        print("\n💡 Next steps:")
        print("1. Visit http://localhost:8000/docs for API documentation")
        print("2. Run the comprehensive test: python test_backend_server.py")
        print("3. Start your frontend application")
        sys.exit(0)
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed.")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure the server is running: uvicorn app.main:app --reload")
        print("2. Check if PostgreSQL is running on port 5433")
        print("3. Check if Redis is running on port 6378")
        print("4. Verify your .env file configuration")
        print("5. Check server logs for errors")
        sys.exit(1)


if __name__ == "__main__":
    main() 