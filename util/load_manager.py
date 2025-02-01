from config.constant import APP_NAME
from util.config_manager import ConfigManager
from util.global_variables import GlobalVariables


class LoadManager:

    def __init__(self):
        self.config_manager = ConfigManager(APP_NAME)
        self.load()

    def load(self):
        for key, value in self.config_manager.config.items():
            GlobalVariables.set(key, value)

    def save(self):
        for key, value in GlobalVariables.get_global_dict().items():
            self.config_manager.set(key, value)
        self.config_manager.save()