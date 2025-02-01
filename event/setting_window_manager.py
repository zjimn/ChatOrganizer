from pathlib import Path
from tkinter import font, filedialog
import tkinter as tk


from api.openai_text_api import OpenaiTextApi
from config.constant import APP_NAME, LOG_FOLDER
from event.event_bus import event_bus
from util.config_manager import ConfigManager
from util.file_util import get_documents_directory
from util.logger import Logger, logger
from util.window_util import center_window
from widget.confirm_dialog import ConfirmDialog
from widget.custom_confirm_dialog import CustomConfirmDialog


class SettingWindowManager:
    def __init__(self, main_window):
        self.selected_log_directory = None
        self.settings_window = main_window.settings_window
        self.config_manager = ConfigManager()
        self.root = self.settings_window.root
        self.main_window = self.settings_window.main_window
        self.setting_window = self.settings_window
        self.openai_text_api = OpenaiTextApi()
        self.bind_events()
        self.open_setting_if_api_key_is_none()


    def bind_events(self):
        self.setting_window.main_window.protocol("WM_DELETE_WINDOW", self.on_cancel)
        event_bus.subscribe("UpdateSettingWidget", self.update_setting_widget)
        event_bus.subscribe("OpenSettingWindow", self.open_setting_window)
        self.setting_window.confirm_button.config(command = self.on_confirm)
        self.setting_window.cancel_button.config(command = self.on_cancel)
        self.setting_window.test_api_key_button.config(command = self.on_click_test_api_key_button)
        self.setting_window.api_key_input_text.bind("<KeyRelease>", self.check_input_text)
        self.setting_window.max_token_toggle_button.bind("<<CheckboxToggled>>", self.on_max_token_toggle_change)
        self.setting_window.select_folder_button.bind("<Button-1>", lambda e: self.select_directory(e))
        self.setting_window.advanced_button.bind("<Button-1>", lambda e: self.open_advanced_window(e))


    def display_max_token_slider(self, state, max_token_count):
        if state:
            if max_token_count == '0' or max_token_count == 0:
                self.settings_window.max_token_slider.set(1000)
            else:
                self.settings_window.max_token_slider.set(max_token_count)
            self.settings_window.max_token_slider.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=5, anchor=tk.E)
            self.settings_window.max_token_express_label.pack_forget()
        else:
            self.settings_window.max_token_slider.pack_forget()
            self.settings_window.max_token_express_label.pack(side = tk.LEFT, padx=(10, 10), pady=5)

    def on_max_token_toggle_change(self, event):
        state = self.settings_window.max_token_toggle_button.get_state()
        self.display_max_token_slider(state, self.setting_window.max_token_slider.get())

    def open_setting_window(self):
        self.open()

    def open_setting_if_api_key_is_none(self):
        api_key = self.config_manager.get("api_key")
        if not api_key:
            self.root.after(500,  self.open)

    def get_system_fonts(self):
        values = font.families()
        return values

    def open(self):
        center_window(self.main_window, self.root,self.setting_window.win_width, self.setting_window.win_height)
        self.main_window.deiconify()
        self.main_window.grab_set()
        self.load_setting()

    def load_setting(self):
        api_key = self.config_manager.get("api_key")
        max_token = self.config_manager.get("max_token", 0)
        typewriter_effect_state = self.config_manager.get("typewriter_effect", True)
        current_log_folder = self.config_manager.get("log_folder")
        current_log_state = self.config_manager.get("log_state", False)
        self.setting_window.api_key_input_text_var.set(value="")
        if api_key:
            self.setting_window.api_key_input_text_var.set(value=api_key)
        self.setting_window.max_token_toggle_button.set_state(max_token != 0)
        self.setting_window.log_entry.delete(0, tk.END)
        if current_log_folder:
            self.setting_window.log_entry.insert(0, current_log_folder)
        self.display_max_token_slider(max_token != 0, max_token)
        self.setting_window.log_toggle_button.set_state(current_log_state)

        self.setting_window.type_effect_toggle_button.set_state(typewriter_effect_state)
        self.check_input_text()

    def open_advanced_window(self, event):
        event_bus.publish("OpenAdvancedLogWindow")


    def select_directory(self, event):
        current_log_folder = self.setting_window.log_entry.get()
        default_log_folder = Path(get_documents_directory())/APP_NAME/LOG_FOLDER
        if not current_log_folder:
            default_log_dir = Path(default_log_folder)
            default_log_dir.mkdir(parents=True, exist_ok=True)
            current_log_folder = default_log_folder
        # 创建根窗口并隐藏
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口

        # 创建一个顶层窗口
        top = tk.Toplevel(root)
        top.overrideredirect(True)
        top.title("选择目录")
        top.geometry("0x0")
        top.attributes("-topmost", True)  # 设置顶层窗口始终在最前
        #center_window(top, self.root, 10, 10)
        # 调用 askdirectory，选中文件夹
        directory = filedialog.askdirectory(parent=top, title="选择目录", initialdir=current_log_folder)

        # 销毁顶层窗口
        top.destroy()
        if not directory:
            directory = current_log_folder
        self.setting_window.log_entry.delete(0, tk.END)
        self.setting_window.log_entry.insert(0, directory)


    def set_setting(self):
        api_key = self.setting_window.api_key_input_text_var.get()
        max_token = self.setting_window.max_token_slider.get()
        current_log_folder = self.setting_window.log_entry.get()
        max_token_state = self.settings_window.max_token_toggle_button.get_state()
        if not max_token_state:
            max_token = 0
        typewriter_effect_state = self.setting_window.type_effect_toggle_button.get_state()
        log_state = self.setting_window.log_toggle_button.get_state()

        if log_state and not current_log_folder:
            CustomConfirmDialog(title="警告", message="请选择日志保存目录")
            return False

        self.config_manager.set("api_key", api_key)
        self.config_manager.set("max_token", max_token)
        self.config_manager.set("typewriter_effect", typewriter_effect_state)
        self.config_manager.set("log_folder", current_log_folder)
        self.config_manager.set("log_state", log_state)
        logger.reload_config()
        event_bus.publish("DialogSettingChanged")
        return True

    def check_input_text(self, event=None):
        api_key = self.setting_window.api_key_input_text_var.get()
        if api_key:
            self.setting_window.test_api_key_button.config(state=tk.NORMAL)
        else:
            self.setting_window.test_api_key_button.config(state=tk.DISABLED)


    def on_click_test_api_key_button(self, event=None):
        success = True
        try:
            api_key = self.setting_window.api_key_input_text_var.get()
            self.openai_text_api.test(api_key)
        except Exception as e:
            CustomConfirmDialog(parent=self.main_window, title="错误", message= "无法通信, 请检查Api Key与网络")
            success = False
        if success:
            CustomConfirmDialog(parent=self.main_window, title="提示", message= "通信正常")
        self.main_window.grab_set()

    def update_setting_widget(self):
        pass

    def on_click_reset_button(self, event):
        dialog = ConfirmDialog(self.main_window, title="确认重置", message="确定要重置吗？")
        if dialog.result:
            event_bus.publish("ResetSetting")

    def on_confirm(self):
        result = self.set_setting()
        if not result:
            return
        self.main_window.grab_release()
        self.main_window.withdraw()

    def on_cancel(self):
        self.main_window.grab_release()
        self.main_window.withdraw()