from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from app.config import settings
import asyncpg

# Convert sync URL to async URL
async_database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
engine = create_async_engine(
    async_database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create sync engine for testing
sync_engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database and create tables"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Enable TimescaleDB extension if enabled
        if settings.timescale_enabled:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))


async def close_db():
    """Close database connections"""
    await engine.dispose()


def test_sync_connection():
    """Test synchronous database connection"""
    try:
        with sync_engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Database connection successful: {row[0]}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_async_connection():
    """Test asynchronous database connection"""
    try:
        async with engine.begin() as connection:
            result = await connection.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Async database connection successful: {row[0]}")
            return True
    except Exception as e:
        print(f"❌ Async database connection failed: {e}")
        return False


def test_database_info():
    """Test and display database information"""
    try:
        with sync_engine.connect() as connection:
            # Test basic connection
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"📊 PostgreSQL Version: {version}")
            
            # Test database name
            result = connection.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"🗄️  Database Name: {db_name}")
            
            # Test current user
            result = connection.execute(text("SELECT current_user"))
            user = result.fetchone()[0]
            print(f"👤 Current User: {user}")
            
            # Test TimescaleDB extension
            result = connection.execute(text("SELECT * FROM pg_extension WHERE extname = 'timescaledb'"))
            timescale = result.fetchone()
            if timescale:
                print("⏰ TimescaleDB extension is installed")
            else:
                print("⚠️  TimescaleDB extension is not installed")
                
            return True
    except Exception as e:
        print(f"❌ Database info test failed: {e}")
        return False 