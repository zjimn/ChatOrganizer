from pathlib import Path
from db.config_data_access import ConfigDataAccess


class AppConfig:
    CONFIGS = {
        'image_dir_path': str(Path("../data") / "images")
    }
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppConfig, cls).__new__(cls, *args, **kwargs)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.initialize_default_configs()
        self.__initialized = True

    def initialize_default_configs(self):
        with ConfigDataAccess() as cda:
            configs = cda.get_all_configs()
        existing_keys = {config.key for config in configs}
        for key, value in self.CONFIGS.items():
            if key not in existing_keys:
                self.set(key, value, True)
        for item in configs:
            self.CONFIGS[item.key] = item.value

    def get(self, key: str, default=None):
        return self.CONFIGS.get(key, default)

    def set(self, key: str, value: str, update_db=False) -> None:
        self.CONFIGS[key] = value
        if update_db:
            with ConfigDataAccess() as cda:
                cda.upsert_config(key, value)

    def save_all(self) -> None:
        for key, value in self.CONFIGS.items():
            self.set(key, value, True)

    def delete(self, key: str) -> None:
        if key in self.CONFIGS:
            del self.CONFIGS[key]
