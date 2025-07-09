import threading
from tkinter import messagebox

from openai import OpenAI, base_url

from api.chat_base_api import ChatBaseApi
from config import constant
from exception.chat_request_error import ChatRequestError
from exception.chat_request_warn import ChatRequestWarn
from util.cancel_manager import CancelManager
from util.logger import logger
import requests

from widget.custom_confirm_dialog import CustomConfirmDialog


class OpenaiApi(ChatBaseApi):
    def __init__(self):
        super().__init__()

    def test(self, api_url, api_key, test_model_name):
        error_message = "无法通信, 请检查API Key和模型与网络"
        try:
            client = OpenAI(api_key=api_key, base_url= api_url)

            response = client.chat.completions.create(
                model=test_model_name,
                messages=[
                    {"role": "user", "content": "test"}
                ],
                stream=False
            )
            content = response.choices[0].message.content
            if not content:
                raise ChatRequestError(error_message)
        except Exception as e:
            logger.log('error', e)
            raise ChatRequestError(error_message)

    def generate_gpt_completion(self, user_input, sys_messages = None, stream_output = False):
        model_name = self.config_manager.get("txt_model_name")
        messages = self.token_manager.conversation_txt_history[:]
        if len(messages) == 0:
            logger.log('warning', "输入内容超出限制, 请重新输入")
            raise ChatRequestWarn("输入内容超出限制, 请重新输入")
        api_key = self.config_manager.get("api_key")
        if not api_key:
            logger.log('warning', "请先配置Api Key")
            raise ChatRequestWarn("请先配置Api Key")
        if not model_name:
            logger.log('warning', "请先设置模型")
            raise ChatRequestWarn("请先设置模型")
        sys_message_list = []
        if sys_messages:
            for message in sys_messages:
                sys_message_list.append({"role": constant.SYSTEM_NAME, "content": message})
            messages = sys_message_list + messages
        data = {
            "model": model_name,
            "messages": messages,
            "stream": stream_output
        }
        api_url = self.config_manager.get("api_url")
        client = OpenAI(api_key=api_key, base_url=api_url)
        logger.log('request', f"请求API文本: {data} base_url: {api_url}")
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=stream_output
        )
        return response


if __name__ == "__main__":
    txt_generator = OpenaiApi()
    response1 = txt_generator.generate_gpt_completion("Tell me a joke.")
    print(f"Assistant: {response1}")
    response2 = txt_generator.generate_gpt_completion("What is the weather like?")
    print(f"Assistant: {response2}")
