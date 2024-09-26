from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL, echo=True,
    pool_size=30,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)
Base = declarative_base()
Session = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)
