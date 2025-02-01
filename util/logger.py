import datetime
import logging
import os
from pathlib import Path
import colorlog
from logging.handlers import RotatingFileHandler
from config.app_config import AppConfig
from colorama import Fore, Style, init

class Logger:
    def __init__(self):
        self.show_debug = None
        self.log_level = None
        self.max_file_size = None
        self.log_full_file = None
        self.log_file = None
        self.logging_enabled = None
        self.enable_log = None
        self.app_config = AppConfig()
        self.reload_config()


    def set_enable_logging(self, state):
        self.enable_log = state

    def reload_config(self):
        log_file_path = self.app_config.get("log_folder")
        if not log_file_path:
            self.log_full_file = None
            return
        default_log_dir = Path(log_file_path)
        if not default_log_dir.exists():
            default_log_dir.mkdir(parents=True, exist_ok=True)
        self.enable_log = True if self.app_config.get("log_state", '0') == '1' else False
        self.logging_enabled = False if self.enable_log == '0' else True
        self.log_file = "log.log"
        self.log_full_file = os.path.join(log_file_path, self.log_file)
        self.log_full_file = os.path.normpath(self.log_full_file)
        self.max_file_size = 5 * 1024 * 1024
        self.log_level = "INFO"
        self.show_debug = True

        if self.logging_enabled:
            self._setup_logging()
            self.log('info', "Logging is enabled.")
        else:
            self.log('info', "Logging is disabled.")

    def _setup_logging(self):
        if self.show_debug:
            self.log_level = 'INFO'

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
        if not self.enable_log or not self.log_full_file:
            return
        if level == 'debug' and self.app_config.get("debug_log_state", '0') == '1':
            logging.debug(message)
        elif level == 'info' and self.app_config.get("info_log_state", '1') == '1':
            logging.info(message)
        elif level == 'request' and self.app_config.get("request_log_state", '1') == '1':
            logging.info(message)
        elif level == 'response' and self.app_config.get("response_log_state", '1') == '1':
            logging.info(message)
        elif level == 'warning' and self.app_config.get("warn_log_state", '1') == '1':
            logging.warning(message)
        elif level == 'error' and self.app_config.get("error_log_state", '1') == '1':
            logging.error(message)
        elif level == 'critical' and self.app_config.get("critical_log_state", '0') == '1':
            logging.critical(message)
        #else:
            #logging.error(f"Unknown log level: {level}: {message}")
        self.log_message(level, message)

    def log_message(self, level, message):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
        log_info = f"{current_time} {level.upper()} {message}"
        if level == 'debug':
            print(Fore.GREEN + log_info + Style.RESET_ALL)
        if level == 'info':
            print(Fore.BLUE + log_info + Style.RESET_ALL)
        if level == 'warning':
            print(Fore.YELLOW + log_info + Style.RESET_ALL)
        if level == 'error':
            print(Fore.RED + log_info + Style.RESET_ALL)



logger = Logger()
if __name__ == "__main__":
    logger = Logger()
    logger.log('debug', 'This is a debug message')
    logger.log('info', 'This is an info message')
    logger.log('warning', 'This is a warning message')
    logger.log('error', 'This is an error message')
    logger.log('critical', 'This is a critical message')