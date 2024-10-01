from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db.config import DB_NAME

DATA_DIR = Path('data')
DATABASE_FILE = DATA_DIR / DB_NAME
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f'sqlite:///{DATABASE_FILE}'

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

Base = declarative_base()
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
