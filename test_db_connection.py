#!/usr/bin/env python3
"""
Test script for SQLAlchemy PostgreSQL connection
Run this to test your database connection
"""

import asyncio
import sys
from sqlalchemy import create_engine, text
from app.config import settings


def test_basic_connection():
    """Test basic SQLAlchemy connection to PostgreSQL"""
    print("🔍 Testing basic SQLAlchemy connection...")
    
    try:
        # Create engine
        engine = create_engine(
            settings.database_url,
            echo=False,  # Set to True to see SQL queries
            pool_pre_ping=True
        )
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test_value"))
            row = result.fetchone()
            print(f"✅ Connection successful! Test value: {row[0]}")
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_database_details():
    """Test and display database details"""
    print("\n🔍 Testing database details...")
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as connection:
            # Get PostgreSQL version
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"📊 PostgreSQL Version: {version}")
            
            # Get current database
            result = connection.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"🗄️  Current Database: {db_name}")
            
            # Get current user
            result = connection.execute(text("SELECT current_user"))
            user = result.fetchone()[0]
            print(f"👤 Current User: {user}")
            
            # Get connection info
            result = connection.execute(text("SELECT inet_server_addr(), inet_server_port()"))
            server_info = result.fetchone()
            print(f"🌐 Server: {server_info[0]}:{server_info[1]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database details test failed: {e}")
        return False


def test_timescaledb_extension():
    """Test if TimescaleDB extension is available"""
    print("\n🔍 Testing TimescaleDB extension...")
    
    try:
        engine = create_engine(settings.database_url)
        
        with engine.connect() as connection:
            # Check if TimescaleDB extension exists
            result = connection.execute(text("""
                SELECT extname, extversion 
                FROM pg_extension 
                WHERE extname = 'timescaledb'
            """))
            
            timescale_info = result.fetchone()
            if timescale_info:
                print(f"⏰ TimescaleDB extension found: version {timescale_info[1]}")
                
                # Test TimescaleDB functionality
                result = connection.execute(text("SELECT timescaledb_version()"))
                ts_version = result.fetchone()[0]
                print(f"📈 TimescaleDB version: {ts_version}")
                return True
            else:
                print("⚠️  TimescaleDB extension not found")
                return False
                
    except Exception as e:
        print(f"❌ TimescaleDB test failed: {e}")
        return False


def test_connection_pool():
    """Test connection pool functionality"""
    print("\n🔍 Testing connection pool...")
    
    try:
        engine = create_engine(
            settings.database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
        
        # Test multiple connections
        connections = []
        for i in range(3):
            conn = engine.connect()
            result = conn.execute(text(f"SELECT {i+1} as connection_test"))
            value = result.fetchone()[0]
            print(f"🔗 Connection {i+1}: {value}")
            connections.append(conn)
        
        # Close connections
        for conn in connections:
            conn.close()
            
        print("✅ Connection pool test successful")
        return True
        
    except Exception as e:
        print(f"❌ Connection pool test failed: {e}")
        return False


async def test_async_connection():
    """Test async SQLAlchemy connection"""
    print("\n🔍 Testing async SQLAlchemy connection...")
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        
        # Create async engine
        async_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
        async_engine = create_async_engine(async_url)
        
        # Test async connection
        async with async_engine.begin() as connection:
            result = await connection.execute(text("SELECT 'async_test' as test_value"))
            row = result.fetchone()
            print(f"✅ Async connection successful: {row[0]}")
            
        await async_engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Async connection failed: {e}")
        return False


def main():
    """Run all database tests"""
    print("🚀 Starting PostgreSQL Connection Tests")
    print("=" * 50)
    
    # Test basic connection
    basic_success = test_basic_connection()
    
    # Test database details
    details_success = test_database_details()
    
    # Test TimescaleDB
    timescale_success = test_timescaledb_extension()
    
    # Test connection pool
    pool_success = test_connection_pool()
    
    # Test async connection
    async_success = asyncio.run(test_async_connection())
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"Basic Connection: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"Database Details: {'✅ PASS' if details_success else '❌ FAIL'}")
    print(f"TimescaleDB: {'✅ PASS' if timescale_success else '❌ FAIL'}")
    print(f"Connection Pool: {'✅ PASS' if pool_success else '❌ FAIL'}")
    print(f"Async Connection: {'✅ PASS' if async_success else '❌ FAIL'}")
    
    if all([basic_success, details_success, timescale_success, pool_success, async_success]):
        print("\n🎉 All tests passed! Database connection is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check your database configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main() 