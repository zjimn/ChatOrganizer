from datetime import datetime
from typing import Optional, List

from sqlalchemy.exc import SQLAlchemyError

from db.database import Session
from db.models import ModelServer
from util.logger import logger


class ModelServerAccess:
    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def insert(self, key: str, name: str) -> None:
        data = ModelServer(key=key, name=name)
        try:
            self.session.add(data)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)

    def get_value_by_key(self, key: str, default) -> Optional[ModelServer]:
        try:
            data = self.session.query(ModelServer).filter(ModelServer.key == key, ModelServer.delete_time.is_(None)).first()
            return data.value if data and data.value else default
        except Exception as e:
            logger.log('error', e)
            return None

    def get_all(self) -> List[ModelServer]:
        try:
            return self.session.query(ModelServer).filter(ModelServer.delete_time.is_(None)).all()
        except Exception as e:
            logger.log('error', e)
            return []

    def upsert(self, key: str, name: str) -> None:
        try:
            list = self.session.query(ModelServer).filter(ModelServer.key == key, ModelServer.delete_time.is_(None)).all()
            if len(list) == 0:
                new = ModelServer(key=key, name=name)
                self.session.add(new)
                self.session.commit()
            else:
                for item in list:
                    item.name = name
                    self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.log('error', f"Failed to upsert configuration for key {key}: {e}")

    def delete(self, key: str) -> None:
        try:
            list = self.session.query(ModelServer).filter(ModelServer.key == key, ModelServer.delete_time.is_(None)).one_or_none()
            for item in list:
                if item:
                    item.delete_time = datetime.now()
                    self.session.add(item)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)


    def has_data(self) -> bool:
        try:
            exists = self.session.query(ModelServer).filter(
                ModelServer.delete_time.is_(None)
            ).first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.log('error', e)
            return False