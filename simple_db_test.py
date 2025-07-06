#!/usr/bin/env python3
"""
Simple PostgreSQL connection test with SQLAlchemy
Quick test to verify your database connection
"""

from sqlalchemy import create_engine, text
from app.config import settings


def quick_test():
    """Quick database connection test"""
    print("🔍 Quick PostgreSQL Connection Test")
    print("-" * 40)
    
    # Display connection info
    print(f"Database URL: {settings.database_url}")
    print(f"Host: localhost:5433")
    print(f"Database: llm_platform")
    print(f"User: llm_user")
    print()
    
    try:
        # Create engine
        engine = create_engine(settings.database_url)
        
        # Test connection
        with engine.connect() as connection:
            # Simple test query
            result = connection.execute(text("SELECT 1 as test"))
            value = result.fetchone()[0]
            print(f"✅ Connection successful! Test result: {value}")
            
            # Get database info
            result = connection.execute(text("SELECT current_database(), current_user"))
            db_info = result.fetchone()
            print(f"🗄️  Connected to: {db_info[0]} as {db_info[1]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure PostgreSQL is running on port 5433")
        print("2. Check if database 'llm_platform' exists")
        print("3. Verify user 'llm_user' has access")
        print("4. Check your .env file configuration")
        return False


if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 Database connection is working!")
    else:
        print("\n⚠️  Please fix the connection issues above.") 