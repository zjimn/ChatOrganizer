from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db.config import DATABASE_URL
from util.config_manager import ConfigManager

config_manager =  ConfigManager()
engine = create_engine(
    DATABASE_URL,
    echo=config_manager.get("sql_log_state", True),
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

Base = declarative_base()
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
