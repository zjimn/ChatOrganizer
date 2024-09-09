from typing import Optional, List
from db.database import Session
from db.database import init_db
from db.models import ContentData, OperationConfig  # 导入 OperationConfig 模型
from enums import ContentType


class ConfigDataAccess:
    def __init__(self):
        # init_db()  # 如果需要初始化数据库，请解注释
        self.session = Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def insert_operation_config(self, key: str, value: str) -> None:
        """Insert a new configuration into the OperationConfig table."""
        new_config = OperationConfig(key=key, value=value)
        try:
            self.session.add(new_config)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")

    def get_operation_config_value_by_key(self, key: str, default) -> Optional[OperationConfig]:
        """Retrieve a configuration by its key."""
        try:
            config = self.session.query(OperationConfig).filter(OperationConfig.key == key).one_or_none()
            return config.value if config and config.value else default
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_all_operation_configs(self) -> List[OperationConfig]:
        """Retrieve all configurations."""
        try:
            config_list = self.session.query(OperationConfig).all()
            return config_list
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def update_operation_config(self, key: str, new_value: str) -> None:
        """Update a configuration by its key."""
        try:
            config = self.session.query(OperationConfig).filter(OperationConfig.key == key).one_or_none()
            if config:
                config.value = new_value
                self.session.commit()
            else:
                print("No configuration found with the provided key.")
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")

    def delete_operation_config(self, key: str) -> None:
        """Delete a configuration by its key."""
        try:
            config = self.session.query(OperationConfig).filter(OperationConfig.key == key).one_or_none()
            if config:
                self.session.delete(config)
                self.session.commit()
            else:
                print("No configuration found with the provided key.")
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred: {e}")

# Example usage:
if __name__ == "__main__":
    with ConfigDataAccess() as cda:
        cda.insert_operation_config("example_key", "example_value")
        config = cda.get_operation_config_by_key("example_key")
        print(config)
