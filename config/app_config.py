# app_config.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from db.config_data_access import ConfigDataAccess


class AppConfig:
    """A class to manage system configuration variables stored in a database."""

    CONFIGS = {
        'image_dir_path':  str(Path("../data") / "images")
    }

    def __init__(self):
        # Initialize default config if the table is empty
        self.initialize_default_configs()

    def initialize_default_configs(self):
        """Initialize default configuration values if not already present."""
        with ConfigDataAccess() as cda:
            configs = cda.get_all_configs()
        existing_keys = {config.key for config in configs}
        for key, value in self.CONFIGS.items():
            if key not in existing_keys:
                with ConfigDataAccess() as cda:
                    cda.upsert_config(key, value)


        for item in configs:
            self.CONFIGS[item.key] = item.value

    def get(self, key: str, default=None):
        return self.CONFIGS.get(key) if self.CONFIGS else default

    def set(self, key: str, value: str, update_db = False) -> None:
        self.CONFIGS[key] = value
        if update_db:
            with ConfigDataAccess() as cda:
                cda.upsert_config(key, value)

    def delete(self, key: str) -> None:
        del self.CONFIGS[key]
