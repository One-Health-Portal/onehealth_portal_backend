from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError, ArgumentError
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load .env file
load_dotenv()

def get_database_url():
    # Try primary MySQL connection first
    primary_url = os.getenv("DATABASE_URL")
    
    try:
        # Test primary connection
        engine = create_engine(primary_url)
        with engine.connect() as conn:
            inspector = inspect(conn)
            print("Connected to primary MySQL database. Tables:", inspector.get_table_names())
        return primary_url
        
    except OperationalError as e:
        logger.warning(f"Primary MySQL connection failed: {str(e)}")
        logger.info("Attempting to connect to phpMyAdmin...")
        
        # phpMyAdmin connection without password
        phpmyadmin_url = "mysql+pymysql://root@localhost/onehealthportal"
        
        try:
            # Test phpMyAdmin connection
            engine = create_engine(phpmyadmin_url)
            with engine.connect() as conn:
                inspector = inspect(conn)
                print("Connected to phpMyAdmin database. Tables:", inspector.get_table_names())
            return phpmyadmin_url
            
        except OperationalError as e:
            logger.error(f"Both MySQL and phpMyAdmin connections failed: {str(e)}")
            raise RuntimeError("Could not establish database connection. Please check your configuration.")

try:
    # Get working database URL
    DATABASE_URL = get_database_url()
    print(f"Using database URL: {DATABASE_URL}")
    
    # Initialize database engine
    engine = create_engine(DATABASE_URL)
    
    # Create SessionLocal class
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Declare Base
    Base = declarative_base()
    
except Exception as e:
    logger.error(f"Failed to initialize database connection: {str(e)}")
    raise

# Dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error during database session: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()