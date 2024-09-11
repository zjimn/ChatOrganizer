from datetime import datetime
from typing import Optional, List
from db.database import Session
from db.database import init_db
from db.models import ContentData, Config  # 导入 OperationConfig 模型
from enums import ContentType


class ConfigDataAccess:
    def __init__(self):
        # init_db()  # 如果需要初始化数据库，请解注释
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def insert_config(self, key: str, value: str) -> None:
        """Insert a new configuration into the OperationConfig table."""
        new_config = Config(key=key, value=value)
        try:
            self.session.add(new_config)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")

    def get_config_value_by_key(self, key: str, default) -> Optional[Config]:
        """Retrieve a configuration by its key."""
        try:
            config = self.session.query(Config).filter(Config.key == key, Config.delete_time is not None).first()
            return config.value if config and config.value else default
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_all_configs(self) -> List[Config]:
        """Retrieve all configurations."""
        try:
            config_list = self.session.query(Config).filter(Config.delete_time is not None).all()
            return config_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def upsert_config(self, key: str, value: str) -> None:
        """Update an existing configuration or insert a new one."""
        try:
            config = self.session.query(Config).filter(Config.key == key, Config.delete_time is not None).one_or_none()
            if config:
                # Update the existing configuration
                config.value = value
            else:
                # Insert a new configuration
                config = Config(key=key, value=value)
                self.session.add(config)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")

    def delete_config(self, key: str) -> None:
        """Delete a configuration by its key."""
        try:
            config = self.session.query(Config).filter(Config.key == key, Config.delete_time is not None).one_or_none()
            if config:
                config.delete_time = datetime.utcnow()
                self.session.commit()
            else:
                print("No configuration found with the provided key.")
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")

# Example usage:
if __name__ == "__main__":
    with ConfigDataAccess() as cda:
        cda.insert_config("example_key", "example_value")
        config = cda.get_config_value_by_key("example_key")
        print(config)
