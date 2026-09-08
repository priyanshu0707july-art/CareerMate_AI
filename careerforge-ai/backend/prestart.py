import logging
from sqlalchemy.exc import OperationalError
from app.database import engine
from app.models import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    try:
        logger.info("Initializing database schema...")
        models.Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully.")
    except OperationalError as e:
        logger.error(f"Failed to connect to the database: {e}")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred during database initialization: {e}")
        raise e

if __name__ == "__main__":
    init_db()
