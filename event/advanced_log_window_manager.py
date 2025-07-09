from db.database import set_sql_logging
from event.event_bus import event_bus
from util.config_manager import ConfigManager
from util.logger import Logger, logger
from util.window_util import center_window


class AdvancedLogWindowManager:
    def __init__(self, main_window):
        self.advanced_log_window = main_window.advanced_log_window
        self.config_manager = ConfigManager()
        self.root = main_window.root
        self.setting_window = main_window.settings_window.main_window
        self.main_window = self.advanced_log_window.main_window
        self.bind_events()


    def bind_events(self):
        self.advanced_log_window.main_window.protocol("WM_DELETE_WINDOW", self.on_cancel)
        event_bus.subscribe("OpenAdvancedLogWindow", self.open_advanced_log_window)
        self.advanced_log_window.cancel_button.config(command = self.on_cancel)
        self.advanced_log_window.confirm_button.config(command = self.on_confirm)

    def open_advanced_log_window(self):
        self.open()

    def open(self):
        center_window(self.main_window, self.setting_window,self.advanced_log_window.win_width, self.advanced_log_window.win_height)
        self.main_window.deiconify()
        self.load_setting()
        self.setting_window.attributes("-topmost", False)
        self.main_window.grab_set()

    def load_setting(self):
        debug_log_state = self.config_manager.get("debug_log_state", False)
        info_log_state = self.config_manager.get("info_log_state", True)
        warn_log_state = self.config_manager.get("warn_log_state", True)
        error_log_state = self.config_manager.get("error_log_state", True)
        sql_log_state = self.config_manager.get("sql_log_state", True)
        request_log_state = self.config_manager.get("request_log_state", True)
        response_log_state = self.config_manager.get("response_log_state", True)

        self.advanced_log_window.debug_log_toggle_button.set_state(debug_log_state)
        self.advanced_log_window.info_log_toggle_button.set_state(info_log_state)
        self.advanced_log_window.warn_log_toggle_button.set_state(warn_log_state)
        self.advanced_log_window.error_log_toggle_button.set_state(error_log_state)
        self.advanced_log_window.sql_log_toggle_button.set_state(sql_log_state)
        self.advanced_log_window.request_log_toggle_button.set_state(request_log_state)
        self.advanced_log_window.response_log_toggle_button.set_state(response_log_state)

    def on_apply(self):
        self.set_setting()

    def set_setting(self):
        debug_log_state = self.advanced_log_window.debug_log_toggle_button.get_state()
        info_log_state = self.advanced_log_window.info_log_toggle_button.get_state()
        warn_log_state = self.advanced_log_window.warn_log_toggle_button.get_state()
        error_log_state = self.advanced_log_window.error_log_toggle_button.get_state()
        sql_log_state = self.advanced_log_window.sql_log_toggle_button.get_state()
        request_log_state = self.advanced_log_window.request_log_toggle_button.get_state()
        response_log_state = self.advanced_log_window.response_log_toggle_button.get_state()

        self.config_manager.set("debug_log_state", debug_log_state)
        self.config_manager.set("info_log_state", info_log_state)
        self.config_manager.set("warn_log_state", warn_log_state)
        self.config_manager.set("error_log_state", error_log_state)
        self.config_manager.set("sql_log_state", sql_log_state)
        self.config_manager.set("request_log_state", request_log_state)
        self.config_manager.set("response_log_state", response_log_state)
        set_sql_logging(sql_log_state)
        logger.reload_config()

    def on_confirm(self):
        self.set_setting()
        self.config_manager.save()
        self.main_window.grab_release()
        self.main_window.withdraw()
        self.setting_window.attributes("-topmost", True)
        self.setting_window.grab_set()

    def on_cancel(self):
        self.main_window.grab_release()
        self.main_window.withdraw()
        self.setting_window.attributes("-topmost", True)
        self.setting_window.grab_set()