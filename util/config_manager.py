
from pathlib import Path
import json
import os
from tkinter import messagebox


class ConfigManager:
    def __init__(self, app_name, config_filename="config.json"):
        self.config_path = Path(os.getenv("APPDATA")) / app_name / config_filename
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()

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

