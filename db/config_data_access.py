from datetime import datetime
from typing import Optional, List

from sqlalchemy.exc import SQLAlchemyError

from db.database import Session
from db.models import Config
from util.logger import logger


class ConfigDataAccess:
    def __init__(self):
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def insert_config(self, key: str, value: str) -> None:
        new_config = Config(key=key, value=value)
        try:
            self.session.add(new_config)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)

    def get_config_value_by_key(self, key: str, default) -> Optional[Config]:
        try:
            config = self.session.query(Config).filter(Config.key == key, Config.delete_time.is_(None)).first()
            return config.value if config and config.value else default
        except Exception as e:
            logger.log('error', e)
            return None

    def get_all_configs(self) -> List[Config]:
        try:
            config_list = self.session.query(Config).filter(Config.delete_time.is_(None)).all()
            return config_list
        except Exception as e:
            logger.log('error', e)
            return []

    def upsert_config(self, key: str, value: str) -> None:
        try:
            configs = self.session.query(Config).filter(Config.key == key, Config.delete_time.is_(None)).all()
            if len(configs) == 0:
                new_config = Config(key=key, value=value)
                self.session.add(new_config)
                self.session.commit()
            else:
                for conf in configs:
                    conf.value = value
                    self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.log('error', f"Failed to upsert configuration for key {key}: {e}")

    def delete_config(self, key: str) -> None:
        try:
            configs = self.session.query(Config).filter(Config.key == key, Config.delete_time.is_(None)).one_or_none()
            for conf in configs:
                if conf:
                    conf.delete_time = datetime.now()
                    self.session.add(conf)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.log('error', e)


    def has_data(self) -> bool:
        try:
            exists = self.session.query(Config).filter(
                Config.delete_time.is_(None)
            ).first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.log('error', e)
            return False