
from pathlib import Path
import json
import os
from tkinter import messagebox

from config.constant import APP_NAME, LOG_FOLDER, IMG_FOLDER, CONFIG_FILENAME
from util.file_util import get_documents_directory
from util.global_variables import GlobalVariables


class ConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.config_path = Path(get_documents_directory()) / APP_NAME / CONFIG_FILENAME
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
        self._init_default()
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
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value

    def save(self):
        previous_config = self._load_config()  # fetch the current saved config
        success = True
        with self.config_path.open("w", encoding="utf-8") as file:
            try:
                json.dump(self.config, file, ensure_ascii=False, indent=4)
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

    def _init_default(self):
        default_log_folder = Path(get_documents_directory()) / APP_NAME / LOG_FOLDER
        default_img_folder = Path(get_documents_directory()) / APP_NAME / IMG_FOLDER
        default_log_folder = os.path.normpath(default_log_folder)
        default_img_folder = os.path.normpath(default_img_folder)
        log_folder =  self.get("log_folder", default_log_folder)
        self.config["log_folder"] = log_folder
        img_folder = self.get("img_folder", default_img_folder)
        self.config["img_folder"] = img_folder