from api.chat_base_api import ChatBaseApi
from api.deepseek_api import DeepSeekApi
from api.ollama_api import OllamaApi
from api.openai_api import OpenaiApi
from config.constant import OLLAMA_SERVER_KEY, OPENAI_SERVER_KEY, DEEPSEEK_SERVER_KEY
from util.config_manager import ConfigManager


class ChatFactory:
    config_manager = ConfigManager()
    def create_model_server(self, model_server_key = None) -> ChatBaseApi:
        if not model_server_key:
            model_server_key = ChatFactory.config_manager.get("model_server_key")
            if not model_server_key:
                return ChatBaseApi()
        if model_server_key == OLLAMA_SERVER_KEY:
            return OllamaApi()
        elif model_server_key == OPENAI_SERVER_KEY:
            return OpenaiApi()
        elif model_server_key == DEEPSEEK_SERVER_KEY:
            return DeepSeekApi()
        else:
            raise ValueError(f"Unknown model server: {model_server_key}")

    def test(self, selected_model_server_key, api_input):
        model_server = self.create_model_server(selected_model_server_key)
        return model_server.test(api_input)
