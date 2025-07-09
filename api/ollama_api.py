import threading
from tkinter import messagebox

from api.chat_base_api import ChatBaseApi
from config import constant
from exception.chat_request_error import ChatRequestError
from exception.chat_request_warn import ChatRequestWarn
from util.cancel_manager import CancelManager
from util.logger import logger
import requests

from util.ollama_util import check_ollama_connection
from widget.custom_confirm_dialog import CustomConfirmDialog
from ollama import Client


class OllamaApi(ChatBaseApi):

    def __init__(self):
        super().__init__()

    def test(self, api_url, api_key, test_model_name):
        error_message = "无法通信, 请检查请求地址和模型与网络"
        try:

            client = Client(
                host=api_url,
                headers={'x-some-header': 'some-value'}
            )
            response = client.chat(
                model=test_model_name,
                messages=[
                    {"role": "user", "content": "test"}
                ],
                stream=False
            )
            content = ''
            if 'message' in response and 'content' in response.message:
                content = response.message.content
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
        api_url = self.config_manager.get("api_url")
        if not api_url:
            logger.log('warning', "请先配置请求地址")
            raise ChatRequestWarn("请先配置请求地址")
        if not model_name:
            logger.log('warning', "请先设置模型")
            raise ChatRequestWarn("请先设置模型")
        sys_message_list = []
        if sys_messages:
            for message in sys_messages:
                sys_message_list.append({"role": constant.SYSTEM_NAME, "content": message})
            messages = sys_message_list + messages
        data = {
            "host" : api_url,
            "model" : model_name,
            "messages" : messages,
            "options" : {
                # 'num_predict': 128,
                'temperature': 0,
                'top_p': 0.9,  # 与 temperature 类似，较低的 top_p 值会让模型更加保守，较高的值会增加生成内容的多样性。
                'stop': ['<EOT>'],
            },
            "stream" : stream_output
        }
        logger.log('request', f"请求API文本: {data}")
        client = Client(
            host= api_url,
            headers={'x-some-header': 'some-value'}
        )
        response = client.chat(
            model=model_name,
            messages=messages,
            options = {
                # 'num_predict': 128,
                'temperature': 0,
                'top_p': 0.9,
                'stop': ['<EOT>']
            },
            stream = stream_output
        )
        return response


if __name__ == "__main__":
    txt_generator = OllamaApi()
    response1 = txt_generator.generate_gpt_completion("Tell me a joke.")
    print(f"Assistant: {response1}")
    response2 = txt_generator.generate_gpt_completion("What is the weather like?")
    print(f"Assistant: {response2}")
