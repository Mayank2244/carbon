import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_redis():
    print("Testing Redis...")
    try:
        import redis.asyncio as redis
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        await r.ping()
        print("✅ Redis is working")
        await r.aclose()
    except Exception as e:
        print(f"❌ Redis error: {e}")

async def test_postgres():
    print("Testing PostgreSQL...")
    try:
        import asyncpg
        conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
        await conn.execute("SELECT 1")
        print("✅ PostgreSQL is working")
        await conn.close()
    except Exception as e:
        print(f"❌ PostgreSQL error: {e}")

async def test_neo4j():
    print("Testing Neo4j...")
    try:
        from neo4j import GraphDatabase
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        print("✅ Neo4j is working")
        driver.close()
    except Exception as e:
        print(f"❌ Neo4j error: {e}")

async def main():
    await test_redis()
    await test_postgres()
    await test_neo4j()

if __name__ == "__main__":
    asyncio.run(main())
