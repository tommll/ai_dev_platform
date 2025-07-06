#!/usr/bin/env python3
"""
Simple Redis connection test
Quick test to verify your Redis connection
"""

import redis
import redis.asyncio as redis_async
import asyncio
from app.config import settings


def quick_sync_test():
    """Quick synchronous Redis connection test"""
    print("🔍 Quick Redis Connection Test (Sync)")
    print("-" * 40)
    
    # Display connection info
    print(f"Redis URL: {settings.redis_url}")
    print(f"Host: localhost:6378")
    print()
    
    try:
        # Create Redis client
        r = redis.from_url(settings.redis_url)
        
        # Test ping
        ping_result = r.ping()
        print(f"✅ Ping successful: {ping_result}")
        
        # Test basic operations
        r.set("test_key", "hello redis")
        value = r.get("test_key")
        print(f"✅ Set/Get test: {value.decode()}")
        
        # Clean up
        r.delete("test_key")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure Redis is running on port 6378")
        print("2. Check if Redis server is accessible")
        print("3. Verify your .env file configuration")
        return False


async def quick_async_test():
    """Quick asynchronous Redis connection test"""
    print("\n🔍 Quick Redis Connection Test (Async)")
    print("-" * 40)
    
    try:
        # Create async Redis client
        r = redis_async.from_url(settings.redis_url)
        
        # Test ping
        ping_result = await r.ping()
        print(f"✅ Async ping successful: {ping_result}")
        
        # Test basic operations
        await r.set("async_test_key", "hello async redis")
        value = await r.get("async_test_key")
        print(f"✅ Async Set/Get test: {value.decode()}")
        
        # Clean up
        await r.delete("async_test_key")
        await r.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Async connection failed: {e}")
        return False


def test_redis_info():
    """Test Redis server information"""
    print("\n🔍 Redis Server Information")
    print("-" * 40)
    
    try:
        r = redis.from_url(settings.redis_url)
        
        # Get basic info
        info = r.info()
        
        print(f"📊 Redis Version: {info.get('redis_version', 'Unknown')}")
        print(f"🖥️  OS: {info.get('os', 'Unknown')}")
        print(f"🔗 Connected Clients: {info.get('connected_clients', 'Unknown')}")
        print(f"💾 Used Memory: {info.get('used_memory_human', 'Unknown')}")
        print(f"🌐 Server Port: {info.get('tcp_port', 'Unknown')}")
        print(f"⏰ Uptime: {info.get('uptime_in_seconds', 'Unknown')} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis info failed: {e}")
        return False


def main():
    """Run quick Redis tests"""
    print("🚀 Quick Redis Connection Tests")
    print("=" * 50)
    
    # Test sync connection
    sync_success = quick_sync_test()
    
    # Test async connection
    async_success = asyncio.run(quick_async_test())
    
    # Test Redis info
    info_success = test_redis_info()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Quick Test Summary:")
    print(f"Sync Connection: {'✅ PASS' if sync_success else '❌ FAIL'}")
    print(f"Async Connection: {'✅ PASS' if async_success else '❌ FAIL'}")
    print(f"Redis Info: {'✅ PASS' if info_success else '❌ FAIL'}")
    
    if all([sync_success, async_success, info_success]):
        print("\n🎉 Redis connection is working!")
    else:
        print("\n⚠️  Some tests failed. Please check your Redis configuration.")


if __name__ == "__main__":
    main() 