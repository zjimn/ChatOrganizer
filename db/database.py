# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db.config import DATABASE_URL

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, echo=True,
    pool_size=30,  # Default is 5
    max_overflow=20,  # Default is 10
    pool_timeout=30,  # Default is 30 seconds
    pool_recycle=1800  # Recycle connections after 30 minutes
)
# Create the base class for our models
Base = declarative_base()

# Create a session factory
Session = sessionmaker(bind=engine)

def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(engine)
