
from pathlib import Path
import json
import os
from tkinter import messagebox

from config.constant import APP_NAME, IMAGE_DIR_PATH
from util.global_variables import GlobalVariables


class ConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self, app_name = APP_NAME, config_filename="config.json"):
        if self.__initialized:
            return
        self.config_path = Path(os.getenv("APPDATA")) / app_name / config_filename
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
        GlobalVariables.set_variables(self.config)
        _init_default()
        self.__initialized = True

    def _load_config(self):
        if not self.config_path.exists():
            return {}
        with self.config_path.open("r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except Exception as e:
                messagebox.showerror("错误", f"获取配置文件失败: {e}")
        return {}

    def get(self, key, default=None):
        return GlobalVariables.get(key, default)

    def set(self, key, value):
        GlobalVariables.set(key, value)

    def save(self):
        previous_config = self._load_config()  # fetch the current saved config
        success = True
        with self.config_path.open("w", encoding="utf-8") as file:
            try:
                json.dump(GlobalVariables.get_variables(), file, ensure_ascii=False, indent=4)
            except Exception as e:
                success = False
                messagebox.showerror("错误", f"配置文件保存失败: {e}")
                print(f"Error: save file error{e}")
        if not success:
            with self.config_path.open("w", encoding="utf-8") as file:
                try:
                    json.dump(previous_config, file, ensure_ascii=False, indent=4)
                except Exception as e:
                    success = False
                    messagebox.showerror("错误", f"恢复配置文件失败: {e}")
                    print(f"Error: save file error{e}")

def _init_default():
    image_dir_path =  GlobalVariables.get("image_dir_path", IMAGE_DIR_PATH)
    GlobalVariables.set("image_dir_path", image_dir_path)
    image_dir_path =  GlobalVariables.get("image_dir_path", IMAGE_DIR_PATH)
    GlobalVariables.set("image_dir_path", image_dir_path)