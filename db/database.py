# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db.config import DATABASE_URL

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create the base class for our models
Base = declarative_base()

# Create a session factory
Session = sessionmaker(bind=engine)

def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(engine)
