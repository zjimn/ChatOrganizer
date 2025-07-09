import json
import threading
from tkinter import messagebox

from openai import base_url

from api.chat_base_api import ChatBaseApi
from config import constant
from exception.chat_request_error import ChatRequestError
from exception.chat_request_warn import ChatRequestWarn
from util.cancel_manager import CancelManager
from util.logger import logger
import requests

from widget.custom_confirm_dialog import CustomConfirmDialog


class DeepBricksOpenai(ChatBaseApi):
    def __init__(self):
        super().__init__()
        self.text_chat_api = "/chat/completions"
        self.img_chat_api = "/images/generations"

    def test(self, api_url, api_key, test_model_name):
        txt_chat_url = api_url + self.text_chat_api
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            data = {
                "model": test_model_name,
                "messages": [{"role": constant.USER_NAME, "content": "test"}],
                "stream": False
            }
            response = requests.post(txt_chat_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
        except Exception as e:
            logger.log('error', e)
            raise ChatRequestError("无法通信, 请检查API Key和模型与网络")


    def create_image_from_text(self, prompt, size, n = 1):
        model_name = self.config_manager.get("img_model_name")
        api_key = self.config_manager.get("api_key")
        if not api_key:
            logger.log('warning', "需要配置Api Key")
            raise ChatRequestWarn("需要配置Api Key")
        if not model_name:
            logger.log('warning', "请先设置模型")
            raise ChatRequestWarn("请先设置模型")
        body = {
            "model": model_name,
            "prompt": prompt,
            "size": size,
            "quality": "hd"
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        logger.log('request', f"请求API文本: {body}")
        api_url = self.config_manager.get("api_url")
        img_chat_url = api_url + self.img_chat_api
        response = requests.post(img_chat_url, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        logger.log('response', f"API返回文本: {data}")
        image_urls = []
        if 'data' in data and len(data['data']) > 0:
            for item in data['data']:
                image_url = item.get('url', '')
                image_urls.append(image_url)
        thread_id = threading.get_ident()
        running_state = CancelManager.check_running_state(thread_id)
        if not running_state:
            logger.log('debug', f"the canceled request response thread_id: {thread_id}")
            return None
        return image_urls

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
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        api_url = self.config_manager.get("api_url")
        txt_chat_url = api_url + self.text_chat_api
        data = {
            "base_url": txt_chat_url,
            "model": model_name,
            "messages": messages,
            "stream": stream_output
        }
        logger.log('request', f"请求API文本: {data}")
        response = requests.post(txt_chat_url, headers=headers, json=data, timeout=120, stream = False)
        # if stream_output:
        return response

if __name__ == "__main__":
    txt_generator = DeepBricksOpenai()
    response1 = txt_generator.generate_gpt_completion("Tell me a joke.")
    print(f"Assistant: {response1}")
    response2 = txt_generator.generate_gpt_completion("What is the weather like?")
    print(f"Assistant: {response2}")
