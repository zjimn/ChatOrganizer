import logging
from datetime import datetime
from typing import Optional, List
from db.database import Session
from db.models import Config


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
            print(f"An error occurred: {e}")

    def get_config_value_by_key(self, key: str, default) -> Optional[Config]:
        try:
            config = self.session.query(Config).filter(Config.key == key, Config.delete_time.is_(None)).first()
            return config.value if config and config.value else default
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_all_configs(self) -> List[Config]:
        try:
            config_list = self.session.query(Config).filter(Config.delete_time.is_(None)).all()
            return config_list
        except Exception as e:
            print(f"An error occurred: {e}")
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
            logging.error(f"Failed to upsert configuration for key {key}: {e}")
            raise e

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
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    with ConfigDataAccess() as cda:
        cda.insert_config("example_key", "example_value")
