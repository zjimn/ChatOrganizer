from config.constant import APP_NAME, IMAGE_DIR_PATH
from util.config_manager import ConfigManager
from util.global_variables import GlobalVariables


def _init_default():
    image_dir_path =  GlobalVariables.get("image_dir_path", IMAGE_DIR_PATH)
    GlobalVariables.set("image_dir_path", image_dir_path)


class LoadManager:

    def __init__(self):
        self.config_manager = ConfigManager(APP_NAME)
        self.load()

    def load(self):
        for key, value in self.config_manager.config.items():
            GlobalVariables.set(key, value)
        _init_default()

    def save(self):
        for key, value in GlobalVariables.get_global_dict().items():
            self.config_manager.set(key, value)
        self.config_manager.save()