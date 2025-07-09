import os
import threading
from pathlib import Path
from tkinter import font, filedialog, messagebox
import tkinter as tk

from config.constant import APP_NAME, LOG_FOLDER, IMG_FOLDER, DEEPBRICKS_OPENAI_SERVER_KEY, OLLAMA_SERVER_KEY
from event.event_bus import event_bus
from exception.chat_request_error import ChatRequestError
from service.dialog_model_service import DialogueModelService
from service.model_server_detail_service import ModelServerDetailService
from service.model_server_service import ModelServerService
from util.chat_factory import ChatFactory
from util.config_manager import ConfigManager
from util.file_util import get_documents_directory
from util.logger import logger
from util.window_util import center_window
from widget.custom_confirm_dialog import CustomConfirmDialog
from widget.loading_spinner import LoadingSpinner


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
        self.dialogue_model_service = DialogueModelService()
        self.model_server_service = ModelServerService()
        self.model_server_detail_service = ModelServerDetailService()
        self.model_server_keys = []
        self.model_server_names = []
        self.test_request_thread_ids = []
        self.loading_spinner = LoadingSpinner(self.main_window)
        self.init_model_servers()
        self.open_setting_if_api_key_is_none()


    def bind_events(self):
        self.setting_window.main_window.protocol("WM_DELETE_WINDOW", self.on_cancel)
        event_bus.subscribe("OpenSettingWindow", self.open_setting_window)
        self.setting_window.confirm_button.config(command = self.on_confirm)
        self.setting_window.cancel_button.config(command = self.on_cancel)
        self.setting_window.test_api_key_button.config(command = self.on_click_test_api_key_button)
        self.setting_window.api_url_input_text.bind("<Key>", self.check_input_text)
        self.setting_window.api_url_input_text.bind("<KeyRelease>", self.check_input_text)
        self.setting_window.api_key_input_text.bind("<Key>", self.check_input_text)
        self.setting_window.api_key_input_text.bind("<KeyRelease>", self.check_input_text)
        self.setting_window.test_model_text.bind("<KeyRelease>", self.check_input_text)
        self.setting_window.max_token_toggle_button.bind("<<CheckboxToggled>>", self.on_max_token_toggle_change)
        self.setting_window.select_log_folder_button.bind("<Button-1>", lambda e: self.select_log_folder_directory(e))
        self.setting_window.select_img_folder_button.bind("<Button-1>", lambda e: self.select_img_folder_directory(e))
        self.setting_window.advanced_button.bind("<Button-1>", lambda e: self.open_advanced_window(e))

        self.setting_window.model_server_combobox.bind("<<ComboboxSelected>>", self.change_model_server)
        self.setting_window.help_button.bind("<Button-1>", lambda e: self.open_help_window(e))

    def init_model_servers(self):
        keys, names = self.model_server_service.get_all_list()
        self.model_server_keys = keys
        self.model_server_names = names
        self.setting_window.model_server_combobox['values'] = names
        model_server_index = self.config_manager.get("model_server_index")
        inited = True
        if model_server_index is None:
            self.config_manager.set("stream_response", True)
            model_server_index = 1
            inited = False
        model_server_key = self.model_server_keys[model_server_index]
        self.config_manager.set("model_server_index", model_server_index)
        self.config_manager.set("model_server_key", model_server_key)
        if not inited:
            self.change_model_server(update_config = True, model_server_key = model_server_key)

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
        model_server_index = self.config_manager.get("model_server_index", 1)
        model_server_key = self.model_server_keys[model_server_index]
        data = self.model_server_service.get_data_by_key(model_server_key)
        need_api_url = data.need_api_url
        need_api_key = data.need_api_key
        data = self.model_server_detail_service.get_data_by_server_key(model_server_key)
        api_key = ''
        api_url = ''
        test_model_name = ''
        if data:
            api_key = data.api_key
            api_url = data.api_url
            txt_model_id = data.txt_model_id
            if txt_model_id:
                data = self.dialogue_model_service.get_data_by_id(txt_model_id)
                test_model_name = data.name
                self.setting_window.test_model_text_var.set(value=test_model_name)
        check_result = True
        if not test_model_name:
            check_result = False
        if not api_url:
            if need_api_url:
                check_result = False
        if not api_key:
            if need_api_key:
                check_result = False
        if not check_result:
            self.root.after(500, self.open)
        logger.log("debug", f"config: {self.config_manager.config}")

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
        stream_response = self.config_manager.get("stream_response", True)
        current_log_folder = self.config_manager.get("log_folder")
        current_img_folder = self.config_manager.get("img_folder")
        current_log_state = self.config_manager.get("log_state", False)
        self.setting_window.model_var.set(self.model_server_names[model_server_index])
        self.change_model_server(update_config=True)
        self.setting_window.max_token_toggle_button.set_state(max_token != 0)
        self.setting_window.img_entry.delete(0, tk.END)
        if current_img_folder:
            self.setting_window.img_entry.insert(0, current_img_folder)
        self.setting_window.log_entry.delete(0, tk.END)
        if current_log_folder:
            self.setting_window.log_entry.insert(0, current_log_folder)
        self.display_max_token_slider(max_token != 0, max_token)
        self.setting_window.log_toggle_button.set_state(current_log_state)
        self.setting_window.stream_response.set_state(stream_response)

    def open_advanced_window(self, event):
        self.stop_test_threads()
        self.main_window.grab_set()
        event_bus.publish("OpenAdvancedLogWindow")

    def open_help_window(self, event):
        self.stop_test_threads()
        self.main_window.grab_set()
        event_bus.publish("OpenHelpWindow")


    def change_model_server(self, event = None, update_config = False, model_server_key = None):
        self.stop_test_threads()
        if not model_server_key:
            selected_model_server_index = self.setting_window.model_server_combobox.current()
            model_server_key = self.model_server_keys[selected_model_server_index]
        data = self.model_server_detail_service.get_data_by_server_key(model_server_key)
        api_key = ''
        api_url = ''
        if data:
            api_key = data.api_key
            api_url = data.api_url
        if not api_key: api_key = ""
        if not api_url: api_url = ""
        self.setting_window.api_key_input_text_var.set(value=api_key)
        self.setting_window.api_url_input_text_var.set(value=api_url)
        test_model_name = ''
        txt_model_id = None
        img_model_id = None
        if data:
            txt_model_id = data.txt_model_id
            img_model_id = data.img_model_id
            data = self.dialogue_model_service.get_data_by_id(txt_model_id)
            if data:
                test_model_name = data.name
        self.setting_window.test_model_text_var.set(value=test_model_name)
        self.check_input_text()
        if update_config:
            self.config_manager.set("api_key", api_key)
            self.config_manager.set("api_url", api_url)
            self.config_manager.set("txt_model_id", txt_model_id)
            self.config_manager.set("img_model_id", img_model_id)


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
        center_window(top, None, width=0,height=0)
        top.iconbitmap("res/icon/app_logo_small.ico")
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
        api_key_input = self.setting_window.api_key_input_text_var.get()
        api_url_input = self.setting_window.api_url_input_text_var.get()
        max_token = self.setting_window.max_token_slider.get()
        current_log_folder = self.setting_window.log_entry.get()
        current_img_folder = self.setting_window.img_entry.get()
        max_token_state = self.settings_window.max_token_toggle_button.get_state()
        if not max_token_state:
            max_token = 0
        stream_response = self.setting_window.stream_response.get_state()
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
        self.model_server_detail_service.update_or_insert_data(current_model_server_key, api_key = api_key_input, api_url = api_url_input)
        self.config_manager.set("api_key", api_key_input)
        self.config_manager.set("api_url", api_url_input)
        self.config_manager.set("max_token", max_token)
        self.config_manager.set("stream_response", stream_response)
        self.config_manager.set("img_folder", current_img_folder)
        self.config_manager.set("log_folder", current_log_folder)
        self.config_manager.set("log_state", log_state)
        logger.log("debug", f"config: {self.config_manager.config}")
        logger.reload_config()
        event_bus.publish("DialogSettingChanged")
        return True

    def check_input_text(self, event=None):
        selected_model_server_index = self.setting_window.model_server_combobox.current()
        model_server_key = self.model_server_keys[selected_model_server_index]
        data = self.model_server_service.get_data_by_key(model_server_key)
        need_api_url = data.need_api_url
        need_api_key = data.need_api_key
        api_key_input = self.setting_window.api_key_input_text_var.get()
        api_url_input = self.setting_window.api_url_input_text_var.get()
        test_model_name = self.setting_window.test_model_text_var.get()
        check_result = True
        if not test_model_name:
            check_result = False
        if not api_url_input:
            if need_api_url:
                check_result = False
        if not api_key_input:
            if need_api_key:
                check_result = False
        if self.test_request_thread_ids:
            check_result = False
        if check_result:
            self.setting_window.test_api_key_button.config(state=tk.NORMAL)
        else:
            self.setting_window.test_api_key_button.config(state=tk.DISABLED)
        return check_result


    def on_click_test_api_key_button(self, event=None):
        if self.test_request_thread_ids:
            return
        self.stop_test_threads()
        self.setting_window.test_api_key_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=lambda: self.check_api_request())
        thread.start()
        thread_id = thread.ident
        self.test_request_thread_ids.append(thread_id)


    def check_api_request(self):
        api_key_input = self.setting_window.api_key_input_text_var.get()
        api_url_input = self.setting_window.api_url_input_text_var.get()
        test_model_name = self.setting_window.test_model_text_var.get()
        selected_model_server_index = self.setting_window.model_server_combobox.current()
        selected_model_server_key = self.model_server_keys[selected_model_server_index]
        self.main_window.grab_set()
        success = False
        try:
            self.loading_spinner.start()
            self.chat_factory.test(selected_model_server_key, api_url_input, api_key_input, test_model_name)
            success = True
        except ChatRequestError as cre:
            if not self.cancel_request_check():
                CustomConfirmDialog(parent= self.main_window, title="错误", message=cre, width = 300)
        except Exception as e:
            logger.log('error', e)
            if not self.cancel_request_check():
                messagebox.showerror("错误", f"请求错误:\n{e}", parent= self.main_window)
        if success:
            if not self.cancel_request_check():
                CustomConfirmDialog(parent= self.main_window, title="测试", message="通信正常", width = 200)
        self.loading_spinner.stop()
        thread_id = threading.get_ident()
        if thread_id in self.test_request_thread_ids:
            self.test_request_thread_ids.remove(thread_id)
        self.setting_window.test_api_key_button.config(state=tk.NORMAL)
        #self.main_window.grab_set()

    def on_confirm(self):
        self.stop_test_threads()
        result = self.set_setting()
        if not result:
            return
        self.config_manager.save()
        self.main_window.grab_release()
        self.main_window.withdraw()

    def stop_test_threads(self):
        self.loading_spinner.stop()
        self.test_request_thread_ids.clear()
        self.check_input_text()

    def cancel_request_check(self):
        thread_id = threading.get_ident()
        return not thread_id in self.test_request_thread_ids

    def on_cancel(self):
        self.stop_test_threads()
        self.main_window.grab_release()
        self.main_window.withdraw()