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

    def test(self, api_url):
        error_message = "无法通信, 请检查请求地址与网络"
        try:
            result = check_ollama_connection(api_url)
            if not result:
                raise ChatRequestError(error_message)
        except Exception as e:
            logger.log('error', e)
            raise ChatRequestError(error_message)

    def generate_gpt_completion(self, user_input, sys_messages = None, stream = False):
        model_name = self.config_manager.get("txt_model_name")
        self.token_manager.add_txt_message(constant.USER_NAME, user_input)
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
            }
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
            stream = stream
        )
        logger.log('response', f"API返回文本: {response}")
        if 'message' in response and 'content' in response.message:
            content = response.message.content
            self.token_manager.add_txt_message(constant.ASSISTANT_NAME, content)
        else:
            logger.log('error', f"返回数据结构异常\n返回数据: {response}")
            raise ChatRequestError("返回数据结构异常")
        thread_id = threading.get_ident()
        running_state = CancelManager.check_running_state(thread_id)
        if not running_state:
            logger.log('debug', f"the canceled request response thread_id: {thread_id}")
            self.token_manager.remove_a_pair_history()
            return None
        return content


if __name__ == "__main__":
    txt_generator = OllamaApi()
    response1 = txt_generator.generate_gpt_completion("Tell me a joke.")
    print(f"Assistant: {response1}")
    response2 = txt_generator.generate_gpt_completion("What is the weather like?")
    print(f"Assistant: {response2}")
