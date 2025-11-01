"""MongoDB connection management."""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import sys
from pathlib import Path

# Add apps/api to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings


class Database:
    """Database connection manager."""
    client: Optional[AsyncIOMotorClient] = None
    database = None


db = Database()


async def get_database():
    """Get database instance."""
    if db.database is None:
        await init_database()
    return db.database


async def init_database():
    """Initialize database connection."""
    db.client = AsyncIOMotorClient(settings.mongodb_uri)
    db.database = db.client[settings.mongodb_db_name]
    
    # Create indexes
    await create_indexes()
    return db.database


async def create_indexes():
    """Create database indexes."""
    database = db.database
    
    # Users
    await database.users.create_index("email", unique=True)
    await database.users.create_index("aad_sub")
    
    # Sessions
    await database.sessions.create_index("userId")
    await database.sessions.create_index([("userId", 1), ("createdAt", -1)])
    
    # Messages
    await database.messages.create_index("sessionId")
    await database.messages.create_index([("sessionId", 1), ("createdAt", 1)])
    
    # KB Chunks - Vector Search index (created via Atlas UI or CLI)
    await database.kb_chunks.create_index("docId")
    await database.kb_chunks.create_index([("docId", 1), ("chunkIndex", 1)])
    
    # Tickets
    await database.tickets.create_index([("system", 1), ("externalId", 1)], unique=True)
    await database.tickets.create_index("openedBy")
    
    # Audit Logs
    await database.audit_logs.create_index("sessionId")
    await database.audit_logs.create_index("userId")
    await database.audit_logs.create_index([("userId", 1), ("createdAt", -1)])


async def close_database():
    """Close database connection."""
    if db.client:
        db.client.close()
        db.database = None

