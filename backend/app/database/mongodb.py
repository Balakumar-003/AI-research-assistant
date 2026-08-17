from pymongo import MongoClient
from pymongo.database import Database
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: MongoClient = None
    db: Database = None

db_instance = MongoDB()

def connect_to_mongo():
    """Establish connection to MongoDB."""
    try:
        db_instance.client = MongoClient(settings.MONGODB_URI)
        db_instance.db = db_instance.client[settings.DATABASE_NAME]
        
        # Create indexes
        db_instance.db.projects.create_index([("user_id", 1)])
        
        logger.info(f"Connected to MongoDB database: {settings.DATABASE_NAME}")
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise

def close_mongo_connection():
    """Close MongoDB connection."""
    if db_instance.client:
        db_instance.client.close()
        logger.info("Closed MongoDB connection.")

def get_database() -> Database:
    """
    Dependency to get the MongoDB database instance.
    """
    return db_instance.db
