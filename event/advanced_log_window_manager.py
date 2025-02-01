from pathlib import Path
from tkinter import font, messagebox, filedialog
import tkinter as tk

from exceptiongroup import catch

from api.openai_text_api import OpenaiTextApi
from config.app_config import AppConfig
from config.constant import APP_NAME, LOG_FOLDER
from event.event_bus import event_bus
from util.file_util import get_documents_directory
from util.global_variables import GlobalVariables
from util.load_manager import load_manager
from util.logger import Logger, logger
from util.window_util import center_window


class AdvancedLogWindowManager:
    def __init__(self, main_window):
        self.advanced_log_window = main_window.advanced_log_window
        self.app_config = AppConfig()
        self.root = main_window.root
        self.main_window = self.advanced_log_window.main_window
        self.bind_events()


    def bind_events(self):
        self.advanced_log_window.main_window.protocol("WM_DELETE_WINDOW", self.on_cancel)
        event_bus.subscribe("OpenAdvancedLogWindow", self.open_advanced_log_window)
        self.advanced_log_window.cancel_button.config(command = self.on_cancel)
        self.advanced_log_window.confirm_button.config(command = self.on_confirm)

    def open_advanced_log_window(self):
        self.root.after(100, self.open)

    def open(self):
        center_window(self.main_window, self.root,self.advanced_log_window.win_width, self.advanced_log_window.win_height)
        self.main_window.deiconify()
        self.main_window.grab_set()
        self.load_setting()

    def load_setting(self):
        info_log_state = GlobalVariables.get("info_log_state", True)
        warn_log_state = GlobalVariables.get("warn_log_state", True)
        error_log_state = GlobalVariables.get("error_log_state", True)
        sql_log_state = GlobalVariables.get("sql_log_state", True)
        request_log_state = GlobalVariables.get("request_log_state", True)
        response_log_state = GlobalVariables.get("response_log_state", True)

        self.advanced_log_window.info_log_toggle_button.set_state(info_log_state)
        self.advanced_log_window.warn_log_toggle_button.set_state(warn_log_state)
        self.advanced_log_window.error_log_toggle_button.set_state(error_log_state)
        self.advanced_log_window.sql_log_toggle_button.set_state(sql_log_state)
        self.advanced_log_window.request_log_toggle_button.set_state(request_log_state)
        self.advanced_log_window.response_log_toggle_button.set_state(response_log_state)

    def on_apply(self):
        self.set_setting()

    def set_setting(self):
        info_log_state = self.advanced_log_window.info_log_toggle_button.get_state()
        warn_log_state = self.advanced_log_window.warn_log_toggle_button.get_state()
        error_log_state = self.advanced_log_window.error_log_toggle_button.get_state()
        sql_log_state = self.advanced_log_window.sql_log_toggle_button.get_state()
        request_log_state = self.advanced_log_window.request_log_toggle_button.get_state()
        response_log_state = self.advanced_log_window.response_log_toggle_button.get_state()

        GlobalVariables.set("info_log_state", info_log_state)
        GlobalVariables.set("warn_log_state", warn_log_state)
        GlobalVariables.set("error_log_state", error_log_state)
        GlobalVariables.set("sql_log_state", sql_log_state)
        GlobalVariables.set("request_log_state", request_log_state)
        GlobalVariables.set("response_log_state", response_log_state)

        logger.reload_config()

    def on_confirm(self):
        self.set_setting()
        load_manager.save()
        self.main_window.grab_release()
        self.main_window.withdraw()

    def on_cancel(self):
        self.main_window.grab_release()
        self.main_window.withdraw()