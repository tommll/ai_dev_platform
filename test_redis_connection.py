#!/usr/bin/env python3
"""
Test script for Redis connection
Run this to test your Redis connection
"""

import asyncio
import sys
import redis
import redis.asyncio as redis_async
from app.config import settings


def test_sync_connection():
    """Test synchronous Redis connection"""
    print("🔍 Testing synchronous Redis connection...")
    
    try:
        # Create Redis client
        r = redis.from_url(settings.redis_url)
        
        # Test basic connection
        result = r.ping()
        print(f"✅ Sync connection successful! Ping result: {result}")
        
        # Test basic operations
        r.set("test_key", "test_value")
        value = r.get("test_key")
        print(f"✅ Set/Get test successful: {value.decode()}")
        
        # Clean up
        r.delete("test_key")
        
        return True
        
    except Exception as e:
        print(f"❌ Sync connection failed: {e}")
        return False


async def test_async_connection():
    """Test asynchronous Redis connection"""
    print("\n🔍 Testing asynchronous Redis connection...")
    
    try:
        # Create async Redis client
        r = redis_async.from_url(settings.redis_url)
        
        # Test basic connection
        result = await r.ping()
        print(f"✅ Async connection successful! Ping result: {result}")
        
        # Test basic operations
        await r.set("async_test_key", "async_test_value")
        value = await r.get("async_test_key")
        print(f"✅ Async Set/Get test successful: {value.decode()}")
        
        # Clean up
        await r.delete("async_test_key")
        
        # Close connection
        await r.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Async connection failed: {e}")
        return False


def test_redis_info():
    """Test and display Redis server information"""
    print("\n🔍 Testing Redis server information...")
    
    try:
        r = redis.from_url(settings.redis_url)
        
        # Get Redis info
        info = r.info()
        
        print(f"📊 Redis Version: {info.get('redis_version', 'Unknown')}")
        print(f"🖥️  OS: {info.get('os', 'Unknown')}")
        print(f"🏗️  Architecture: {info.get('arch_bits', 'Unknown')} bits")
        print(f"🔗 Connected Clients: {info.get('connected_clients', 'Unknown')}")
        print(f"💾 Used Memory: {info.get('used_memory_human', 'Unknown')}")
        print(f"💾 Peak Memory: {info.get('used_memory_peak_human', 'Unknown')}")
        print(f"🗄️  Database Keys: {info.get('db0', 'Unknown')}")
        
        # Get server info
        server_info = r.info('server')
        print(f"🌐 Server Port: {server_info.get('tcp_port', 'Unknown')}")
        print(f"⏰ Uptime: {server_info.get('uptime_in_seconds', 'Unknown')} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis info test failed: {e}")
        return False


def test_redis_operations():
    """Test various Redis operations"""
    print("\n🔍 Testing Redis operations...")
    
    try:
        r = redis.from_url(settings.redis_url)
        
        # Test string operations
        r.set("string_key", "hello world")
        value = r.get("string_key")
        print(f"✅ String operations: {value.decode()}")
        
        # Test list operations
        r.lpush("list_key", "item1", "item2", "item3")
        items = r.lrange("list_key", 0, -1)
        print(f"✅ List operations: {[item.decode() for item in items]}")
        
        # Test hash operations
        r.hset("hash_key", mapping={"field1": "value1", "field2": "value2"})
        hash_data = r.hgetall("hash_key")
        print(f"✅ Hash operations: {hash_data}")
        
        # Test set operations
        r.sadd("set_key", "member1", "member2", "member3")
        members = r.smembers("set_key")
        print(f"✅ Set operations: {[member.decode() for member in members]}")
        
        # Test sorted set operations
        r.zadd("zset_key", {"score1": 1.0, "score2": 2.0, "score3": 3.0})
        zset_data = r.zrange("zset_key", 0, -1, withscores=True)
        print(f"✅ Sorted set operations: {zset_data}")
        
        # Clean up
        r.delete("string_key", "list_key", "hash_key", "set_key", "zset_key")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis operations test failed: {e}")
        return False


def test_redis_pubsub():
    """Test Redis pub/sub functionality"""
    print("\n🔍 Testing Redis pub/sub...")
    
    try:
        r = redis.from_url(settings.redis_url)
        
        # Create pubsub object
        pubsub = r.pubsub()
        
        # Subscribe to a channel
        pubsub.subscribe("test_channel")
        
        # Publish a message
        r.publish("test_channel", "test message")
        
        # Get message (with timeout)
        message = pubsub.get_message(timeout=1)
        if message and message['type'] == 'message':
            print(f"✅ Pub/sub test successful: {message['data'].decode()}")
        else:
            print("⚠️  No message received in pub/sub test")
        
        # Unsubscribe and close
        pubsub.unsubscribe("test_channel")
        pubsub.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Redis pub/sub test failed: {e}")
        return False


def test_redis_pipeline():
    """Test Redis pipeline functionality"""
    print("\n🔍 Testing Redis pipeline...")
    
    try:
        r = redis.from_url(settings.redis_url)
        
        # Create pipeline
        pipe = r.pipeline()
        
        # Add commands to pipeline
        pipe.set("pipeline_key1", "value1")
        pipe.set("pipeline_key2", "value2")
        pipe.get("pipeline_key1")
        pipe.get("pipeline_key2")
        
        # Execute pipeline
        results = pipe.execute()
        
        print(f"✅ Pipeline test successful: {results}")
        
        # Clean up
        r.delete("pipeline_key1", "pipeline_key2")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis pipeline test failed: {e}")
        return False


def test_redis_connection_pool():
    """Test Redis connection pool"""
    print("\n🔍 Testing Redis connection pool...")
    
    try:
        # Create connection pool
        pool = redis.ConnectionPool.from_url(settings.redis_url, max_connections=10)
        
        # Test multiple connections
        connections = []
        for i in range(3):
            conn = redis.Redis(connection_pool=pool)
            conn.set(f"pool_key_{i}", f"value_{i}")
            value = conn.get(f"pool_key_{i}")
            print(f"🔗 Pool connection {i+1}: {value.decode()}")
            connections.append(conn)
        
        # Clean up
        for i in range(3):
            connections[i].delete(f"pool_key_{i}")
        
        print("✅ Connection pool test successful")
        return True
        
    except Exception as e:
        print(f"❌ Redis connection pool test failed: {e}")
        return False


async def test_redis_streams():
    """Test Redis streams (if available)"""
    print("\n🔍 Testing Redis streams...")
    
    try:
        r = redis_async.from_url(settings.redis_url)
        
        # Test stream operations
        stream_key = "test_stream"
        
        # Add entry to stream
        entry_id = await r.xadd(stream_key, {"field1": "value1", "field2": "value2"})
        print(f"✅ Stream add successful: {entry_id}")
        
        # Read from stream
        entries = await r.xread({stream_key: "0"}, count=1)
        if entries:
            print(f"✅ Stream read successful: {entries}")
        
        # Clean up
        await r.delete(stream_key)
        await r.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Redis streams test failed: {e}")
        return False


def main():
    """Run all Redis tests"""
    print("🚀 Starting Redis Connection Tests")
    print("=" * 50)
    
    # Test sync connection
    sync_success = test_sync_connection()
    
    # Test async connection
    async_success = asyncio.run(test_async_connection())
    
    # Test Redis info
    info_success = test_redis_info()
    
    # Test Redis operations
    ops_success = test_redis_operations()
    
    # Test Redis pub/sub
    pubsub_success = test_redis_pubsub()
    
    # Test Redis pipeline
    pipeline_success = test_redis_pipeline()
    
    # Test Redis connection pool
    pool_success = test_redis_connection_pool()
    
    # Test Redis streams
    streams_success = asyncio.run(test_redis_streams())
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"Sync Connection: {'✅ PASS' if sync_success else '❌ FAIL'}")
    print(f"Async Connection: {'✅ PASS' if async_success else '❌ FAIL'}")
    print(f"Redis Info: {'✅ PASS' if info_success else '❌ FAIL'}")
    print(f"Redis Operations: {'✅ PASS' if ops_success else '❌ FAIL'}")
    print(f"Pub/Sub: {'✅ PASS' if pubsub_success else '❌ FAIL'}")
    print(f"Pipeline: {'✅ PASS' if pipeline_success else '❌ FAIL'}")
    print(f"Connection Pool: {'✅ PASS' if pool_success else '❌ FAIL'}")
    print(f"Streams: {'✅ PASS' if streams_success else '❌ FAIL'}")
    
    if all([sync_success, async_success, info_success, ops_success, 
            pubsub_success, pipeline_success, pool_success]):
        print("\n🎉 All tests passed! Redis connection is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check your Redis configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main() 