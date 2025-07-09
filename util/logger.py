import datetime
import logging
import os
from pathlib import Path
from tkinter import messagebox

import colorlog
from logging.handlers import RotatingFileHandler
from colorama import Fore, Style

from config.constant import LOG_FILENAME
from util.config_manager import ConfigManager


class Logger:
    def __init__(self):
        self.show_debug = None
        self.log_level = None
        self.max_file_size = None
        self.log_full_file = None
        self.log_file = None
        self.enable_log = None
        self.config_manager = ConfigManager()
        self.reload_config()

    def set_enable_logging(self, state):
        self.enable_log = state

    def reload_config(self):
        log_file_path = self.config_manager.get("log_folder")
        if not log_file_path:
            self.log_full_file = None
            return
        default_log_dir = Path(log_file_path)
        if not default_log_dir.exists():
            default_log_dir.mkdir(parents=True, exist_ok=True)
        self.enable_log = self.config_manager.get("log_state", False)
        self.log_file = LOG_FILENAME
        self.log_full_file = os.path.join(log_file_path, self.log_file)
        self.log_full_file = os.path.normpath(self.log_full_file)
        self.max_file_size = 5 * 1024 * 1024
        self.log_level = "DEBUG"
        self.show_debug = True

        if self.enable_log:
            self._setup_logging()

    def _setup_logging(self):
        if self.show_debug:
            self.log_level = 'DEBUG'

        formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'blue',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )
        handler = RotatingFileHandler(
            self.log_full_file,
            maxBytes=self.max_file_size,
            backupCount=5,  # 可选的备份文件数量
            encoding='utf-8'
        )
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.setLevel(getattr(logging, self.log_level, logging.INFO))
        self.remove_handlers(logger)

        logger.addHandler(handler)
        #logger.addHandler(console_handler)

    def remove_handlers(self, logger):
        while len(logger.handlers) > 0:
            logger.removeHandler(logger.handlers[0])

    def log(self, level, message):
        try:
            if not self.enable_log or not self.log_full_file:
                return
            if level == 'debug' and self.config_manager.get("debug_log_state", False):
                logging.debug(message)
                self.log_message(level, message)
            elif level == 'info' and self.config_manager.get("info_log_state", True):
                logging.info(message)
                self.log_message(level, message)
            elif level == 'request' and self.config_manager.get("request_log_state", True):
                logging.info(message)
                self.log_message(level, message)
            elif level == 'response' and self.config_manager.get("response_log_state", True):
                logging.info(message)
                self.log_message(level, message)
            elif level == 'warning' and self.config_manager.get("warn_log_state", True):
                logging.warning(message)
                self.log_message(level, message)
            elif level == 'error' and self.config_manager.get("error_log_state", True):
                logging.error(message)
                self.log_message(level, message)
            elif level == 'critical' and self.config_manager.get("error_log_state", False):
                logging.critical(message)
                self.log_message(level, message)
        except Exception as e:
            messagebox.showerror("错误", "日志记录异常")

    def log_message(self, level, message):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
        log_info = f"{current_time} {level.upper()} {message}"
        if level == 'debug':
            print(Fore.GREEN + log_info + Style.RESET_ALL)
        if level == 'info':
            print(Fore.BLUE + log_info + Style.RESET_ALL)
        if level == 'request':
            print(Fore.BLUE + log_info + Style.RESET_ALL)
        if level == 'response':
            print(Fore.BLUE + log_info + Style.RESET_ALL)
        if level == 'warning':
            print(Fore.YELLOW + log_info + Style.RESET_ALL)
        if level == 'error':
            print(Fore.RED + log_info + Style.RESET_ALL)
        if level == 'critical':
            print(Fore.RED + log_info + Style.RESET_ALL)



logger = Logger()
if __name__ == "__main__":
    logger = Logger()
    logger.log('debug', 'This is a debug message')
    logger.log('info', 'This is an info message')
    logger.log('warning', 'This is a warning message')
    logger.log('error', 'This is an error message')
    logger.log('critical', 'This is a critical message')