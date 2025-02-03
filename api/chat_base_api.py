from util.config_manager import ConfigManager
from util.logger import logger
from util.token_management import TokenManager
from abc import abstractmethod

class ChatBaseApi:
    def __init__(self):
        self.token_manager = TokenManager()
        self.config_manager = ConfigManager()
        self.model_name = ""
        self.reload_config()

    def reload_config(self):
        max_token = self.config_manager.get("max_token", 0)
        max_history_count = self.config_manager.get("max_history_count", 0)
        if max_token is not None:
            self.token_manager.set_token_limit(max_token)
        if max_history_count is not None:
            self.token_manager.set_history_limit(max_history_count)

    def reload_model(self, model):
        self.model_name = model

    def clear_history(self):
        self.token_manager.clear_txt_history()

    def add_history_message(self, role, message):
        self.token_manager.add_txt_message(role, message)

    @abstractmethod
    def test(self, api_input):
        raise NotImplementedError("The subclass must implement the test method")

    @abstractmethod
    def generate_gpt_completion(self, user_input, sys_messages=None):
        raise NotImplementedError("模型未实现对话交互")

    @abstractmethod
    def create_image_from_text(self, prompt, size, n=1):
        raise NotImplementedError("模型未实现文生图")