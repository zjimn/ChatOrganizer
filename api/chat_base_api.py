import threading

from util.cancel_manager import CancelManager
from util.config_manager import ConfigManager
from util.logger import logger
from util.token_management import TokenManager
from abc import abstractmethod

class ChatBaseApi:
    def __init__(self):
        if self.__initialized:
            return
        self.token_manager = TokenManager()
        self.config_manager = ConfigManager()
        self.model_name = ""
        self.reload_config()
        self.__initialized = True


    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ChatBaseApi, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def reload_config(self):
        max_token = self.config_manager.get("max_token", 0)
        max_history_count = self.config_manager.get("max_history_count", 0)
        if max_token is not None:
            self.token_manager.set_token_limit(max_token)
        if max_history_count is not None:
            self.token_manager.set_history_limit(max_history_count)

    def reload_model(self, model):
        self.model_name = model

    def cancel_request_history(self):
        self.token_manager.remove_recent_history()

    def sign_history_recent_false(self):
        self.token_manager.sign_history_recent_false()

    def cancel_request_check(self):
        thread_id = threading.get_ident()
        running_state = CancelManager.check_running_state(thread_id)
        if not running_state:
            logger.log('debug', f"the canceled request response thread_id: {thread_id}")
            self.cancel_request_history()
            return True
        return False

    def clear_history(self):
        self.token_manager.clear_txt_history()

    def add_history_message(self, role, message, recent = False):
        self.token_manager.add_txt_message(role, message, recent)

    @abstractmethod
    def test(self, api_url, api_key, test_model_name):
        raise NotImplementedError("The subclass must implement the test method")

    @abstractmethod
    def generate_gpt_completion(self, user_input, sys_messages=None, stream_output = False):
        raise NotImplementedError("模型未实现对话交互")

    @abstractmethod
    def create_image_from_text(self, prompt, size, n=1):
        raise NotImplementedError("模型未实现文生图")