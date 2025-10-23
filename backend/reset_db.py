#!/usr/bin/env python3
"""
Quick script to drop and recreate database tables
"""
import asyncio
import asyncpg
from app.core.config import get_settings

async def reset_database():
    settings = get_settings()
    
    # Connect to database
    conn = await asyncpg.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME
    )
    
    try:
        # Drop all tables and types
        print("🗑️  Dropping existing tables and types...")
        await conn.execute("DROP SCHEMA public CASCADE;")
        await conn.execute("CREATE SCHEMA public;")
        print("✅ Database reset complete!")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(reset_database())