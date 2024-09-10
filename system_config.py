# system_config.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from db.config_data_access import ConfigDataAccess


class SystemConfig:
    """A class to manage system configuration variables stored in a database."""

    CONFIGS = {
        'image_dir_path':  str(Path("data") / "images")
    }

    def __init__(self):
        self.config_data_access = ConfigDataAccess()
        # Initialize default configs if the table is empty
        self.initialize_default_configs()

    def initialize_default_configs(self):
        """Initialize default configuration values if not already present."""
        configs = self.config_data_access.get_all_configs()
        existing_keys = {config.key for config in configs}
        for key, value in self.CONFIGS.items():
            if key not in existing_keys:
                self.config_data_access.insert_config(key, value)

        for item in configs:
            self.CONFIGS[item.key] = item.value

    def get(self, key: str, default=None):
        return self.CONFIGS[key] if self.CONFIGS else default

    def set(self, key: str, value: str) -> None:
        self.CONFIGS[key] = value
        self.config_data_access.insert_config(key, value)

    def delete(self, key: str) -> None:
        del self.CONFIGS[key]
