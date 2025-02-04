import os
from pathlib import Path
from tkinter import font, filedialog, messagebox
import tkinter as tk

from config.constant import APP_NAME, LOG_FOLDER, IMG_FOLDER, OPENAI_SERVER_KEY, OLLAMA_SERVER_KEY
from event.event_bus import event_bus
from exception.chat_request_error import ChatRequestError
from service.model_server_detail_service import ModelServerDetailService
from service.model_server_service import ModelServerService
from util.chat_factory import ChatFactory
from util.config_manager import ConfigManager
from util.file_util import get_documents_directory
from util.logger import logger
from util.window_util import center_window
from widget.custom_confirm_dialog import CustomConfirmDialog


class SettingWindowManager:
    def __init__(self, main_window):
        self.selected_log_directory = None
        self.settings_window = main_window.settings_window
        self.config_manager = ConfigManager()
        self.root = self.settings_window.root
        self.main_window = self.settings_window.main_window
        self.setting_window = self.settings_window
        self.chat_factory = ChatFactory()
        self.chat_text_api = None
        self.bind_events()
        self.open_setting_if_api_key_is_none()
        self.model_server_service = ModelServerService()
        self.model_server_detail_service = ModelServerDetailService()
        self.model_server_keys = []
        self.model_server_names = []
        self.init_model_servers()


    def bind_events(self):
        self.setting_window.main_window.protocol("WM_DELETE_WINDOW", self.on_cancel)
        event_bus.subscribe("OpenSettingWindow", self.open_setting_window)
        self.setting_window.confirm_button.config(command = self.on_confirm)
        self.setting_window.cancel_button.config(command = self.on_cancel)
        self.setting_window.test_api_key_button.config(command = self.on_click_test_api_key_button)
        self.setting_window.api_input_text.bind("<Key>", self.check_input_text)
        self.setting_window.api_input_text.bind("<KeyRelease>", self.check_input_text)
        self.setting_window.api_input_text.bind("<<UpdatePlaceholder>>", self.check_input_text)
        self.setting_window.max_token_toggle_button.bind("<<CheckboxToggled>>", self.on_max_token_toggle_change)
        self.setting_window.select_log_folder_button.bind("<Button-1>", lambda e: self.select_log_folder_directory(e))
        self.setting_window.select_img_folder_button.bind("<Button-1>", lambda e: self.select_img_folder_directory(e))
        self.setting_window.advanced_button.bind("<Button-1>", lambda e: self.open_advanced_window(e))

        self.setting_window.model_server_combobox.bind("<<ComboboxSelected>>", self.update_api_input_text)

    def init_model_servers(self):
        keys, names = self.model_server_service.get_all_list()
        self.model_server_keys = keys
        self.model_server_names = names
        self.setting_window.model_server_combobox['values'] = names

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
        model_server_index = self.config_manager.get("model_server_index", 0)
        model_server_key = self.model_server_keys[model_server_index]
        logger.log("debug", f"model server: {model_server_key}")
        max_token = self.config_manager.get("max_token", 0)
        typewriter_effect_state = self.config_manager.get("typewriter_effect", True)
        current_log_folder = self.config_manager.get("log_folder")
        current_img_folder = self.config_manager.get("img_folder")
        current_log_state = self.config_manager.get("log_state", False)
        self.setting_window.model_var.set(self.model_server_names[model_server_index])
        self.update_api_input_text(update_config=True)
        self.setting_window.max_token_toggle_button.set_state(max_token != 0)
        self.setting_window.img_entry.delete(0, tk.END)
        if current_img_folder:
            self.setting_window.img_entry.insert(0, current_img_folder)
        self.setting_window.log_entry.delete(0, tk.END)
        if current_log_folder:
            self.setting_window.log_entry.insert(0, current_log_folder)
        self.display_max_token_slider(max_token != 0, max_token)
        self.setting_window.log_toggle_button.set_state(current_log_state)

        self.setting_window.type_effect_toggle_button.set_state(typewriter_effect_state)

    def open_advanced_window(self, event):
        event_bus.publish("OpenAdvancedLogWindow")


    def update_api_input_text(self, event = None, update_config = False):
        api_key = ""
        api_url = ""
        selected_model_server_index = self.setting_window.model_server_combobox.current()
        model_server_key = self.model_server_keys[selected_model_server_index]
        data = self.model_server_detail_service.get_data_by_server_key(model_server_key)
        if data:
            api_key = data.api_key
            api_url = data.api_url
        if api_key is None:
            api_key = ""
        if api_url is None:
            api_url = ""
        if self.is_api_key():
            self.setting_window.api_label.config(text="API Key ")
            self.setting_window.api_input_text_var.set(value=api_key)
        else:
            self.setting_window.api_label.config(text="请求地址")
            self.setting_window.api_input_text_var.set(value=api_url)
        self.check_input_text()
        if update_config:
            self.config_manager.set("api_key", api_key)
            self.config_manager.set("api_url", api_url)

    def is_api_key(self):
        selected_model_server_index = self.setting_window.model_server_combobox.current()
        return not self.model_server_keys[selected_model_server_index] in [OLLAMA_SERVER_KEY]

    def select_img_folder_directory(self, event):
        current_img_folder = self.setting_window.img_entry.get()
        default_img_folder = Path(get_documents_directory())/APP_NAME/IMG_FOLDER
        if not current_img_folder:
            default_img_save_dir = Path(default_img_folder)
            default_img_save_dir.mkdir(parents=True, exist_ok=True)
            current_img_folder = default_img_folder
        directory = self.get_directory(default_img_folder)
        if not directory:
            directory = current_img_folder
        self.setting_window.img_entry.delete(0, tk.END)
        self.setting_window.img_entry.insert(0, directory)

    def get_directory(self, initialdir = None):
        root = tk.Tk()
        root.withdraw()
        top = tk.Toplevel(root)
        top.overrideredirect(True)
        top.title("选择目录")
        top.geometry("0x0")
        top.attributes("-topmost", True)
        directory = filedialog.askdirectory(parent=top, title="选择目录", initialdir=initialdir)
        top.destroy()
        if directory:
            directory = os.path.normpath(directory)
        return directory

    def select_log_folder_directory(self, event):
        current_log_folder = self.setting_window.log_entry.get()
        default_log_folder = Path(get_documents_directory())/APP_NAME/LOG_FOLDER
        if not current_log_folder:
            default_log_dir = Path(default_log_folder)
            default_log_dir.mkdir(parents=True, exist_ok=True)
            current_log_folder = default_log_folder
        directory = self.get_directory(default_log_folder)
        if not directory:
            directory = current_log_folder
        self.setting_window.log_entry.delete(0, tk.END)
        self.setting_window.log_entry.insert(0, directory)


    def set_setting(self):
        selected_model_server_index = self.setting_window.model_server_combobox.current()
        api_input = self.setting_window.api_input_text_var.get()
        max_token = self.setting_window.max_token_slider.get()
        current_log_folder = self.setting_window.log_entry.get()
        current_img_folder = self.setting_window.img_entry.get()
        max_token_state = self.settings_window.max_token_toggle_button.get_state()
        if not max_token_state:
            max_token = 0
        typewriter_effect_state = self.setting_window.type_effect_toggle_button.get_state()
        log_state = self.setting_window.log_toggle_button.get_state()

        if log_state and not current_log_folder:
            CustomConfirmDialog(parent=self.main_window, title="警告", message="请选择日志保存目录")
            return False
        current_model_server_key = self.model_server_keys[selected_model_server_index]
        self.config_manager.set("model_server_index", selected_model_server_index)
        self.config_manager.set("model_server_key", current_model_server_key)
        data = self.model_server_detail_service.get_data_by_server_key(current_model_server_key)
        txt_model_id = None
        img_model_id = None
        if data:
            txt_model_id = data.txt_model_id
            img_model_id = data.img_model_id
        self.config_manager.set("txt_model_id", txt_model_id)
        self.config_manager.set("img_model_id", img_model_id)
        if txt_model_id is None:
            self.config_manager.set("txt_model_name", None)
        if img_model_id is None:
            self.config_manager.set("img_model_name", None)
        event_bus.publish("ModelServerChange")
        api_key = api_input
        api_url = api_input
        if self.is_api_key():
            api_url = None
        else:
            api_key = None
        self.model_server_detail_service.update_or_insert_data(current_model_server_key, api_key = api_key, api_url = api_url)
        self.config_manager.set("api_key", api_key)
        self.config_manager.set("api_url", api_url)
        self.config_manager.set("max_token", max_token)
        self.config_manager.set("typewriter_effect", typewriter_effect_state)
        self.config_manager.set("img_folder", current_img_folder)
        self.config_manager.set("log_folder", current_log_folder)
        self.config_manager.set("log_state", log_state)
        logger.log("debug", f"config: {self.config_manager.config}")
        logger.reload_config()
        event_bus.publish("DialogSettingChanged")
        return True

    def check_input_text(self, event=None):
        api_key = self.setting_window.api_input_text_var.get()
        if api_key:
            self.setting_window.test_api_key_button.config(state=tk.NORMAL)
        else:
            self.setting_window.test_api_key_button.config(state=tk.DISABLED)


    def on_click_test_api_key_button(self, event=None):
        api_input = self.setting_window.api_input_text_var.get()
        selected_model_server_index = self.setting_window.model_server_combobox.current()
        selected_model_server_key = self.model_server_keys[selected_model_server_index]
        self.main_window.grab_set()
        success = False
        try:
            self.chat_factory.test(selected_model_server_key, api_input)
            success = True
        except ChatRequestError as cre:
            CustomConfirmDialog(parent= self.main_window, title="错误", message="无法通信, 请检查API Key与网络")
        except Exception as e:
            logger.log('error', e)
            messagebox.showerror("错误", f"请求异常:\n{e}")
        if success:
            CustomConfirmDialog(parent= self.main_window, title="提示", message="通信正常")

    def on_confirm(self):
        result = self.set_setting()
        if not result:
            return
        self.main_window.grab_release()
        self.main_window.withdraw()

    def on_cancel(self):
        self.main_window.grab_release()
        self.main_window.withdraw()