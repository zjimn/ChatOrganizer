import os
from logging import exception
from tkinter import messagebox

from dotenv import load_dotenv
from config import constant
from util.config_manager import ConfigManager
from util.logger import Logger, logger
from util.resource_util import resource_path
from util.token_management import TokenManager
import requests
import json

from widget.custom_confirm_dialog import CustomConfirmDialog


class OpenaiTextApi:
    def __init__(self):
        self.cancel = None
        self.token_manager = TokenManager()
        dotenv_path = resource_path('.env')
        load_dotenv(dotenv_path)
        self.config_manager = ConfigManager()
        self.model_name = ""
        self.api_key =""
        self.reload_config()
        self.chat_url = "https://api.deepbricks.ai/v1/chat/completions"

    def reload_config(self):
        api_key = self.config_manager.get("api_key")
        max_token = self.config_manager.get("max_token", 0)
        max_history_count = self.config_manager.get("max_history_count", 0)
        model_name = self.config_manager.get("text_model_name")
        if model_name is not None:
            self.model_name = model_name
        if api_key is not None:
            self.api_key = api_key
        if max_token is not None:
            self.token_manager.set_token_limit(max_token)
        if max_history_count is not None:
            self.token_manager.set_history_limit(max_history_count)

    def reload_model(self, model):
        if model:
            self.model_name = model

    def test(self, api_key):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role":constant.USER_NAME, "content":"test"}],
            "stream": False
        }
        response = requests.post(self.chat_url, headers=headers, json=data, timeout=10)
        response.raise_for_status()


    def clear_history(self):
        self.token_manager.clear_txt_history()

    def add_history_message(self, role, message):
        self.token_manager.add_txt_message(role, message)

    def cancel_request(self):
        self.cancel = True


    def generate_gpt_completion(self, user_input, sys_messages = None):
        self.cancel = False
        self.token_manager.add_txt_message(constant.USER_NAME, user_input)
        messages = self.token_manager.conversation_txt_history[:]
        if len(messages) == 0:
            CustomConfirmDialog(title="警告", message="输入内容超出限制, 请重新输入")
            logger.log('warning', "输入内容超出限制, 请重新输入")
            return
        if not self.api_key:
            CustomConfirmDialog(title="警告", message="需要配置Api Key")
            logger.log('warning', "需要配置Api Key")
            return
        if not self.model_name:
            CustomConfirmDialog(title="警告", message="请先选择模型")
            logger.log('warning', "请先选择模型")
            return
        sys_message_list = []
        if sys_messages:
            for message in sys_messages:
                sys_message_list.append({"role": constant.SYSTEM_NAME, "content": message})
            messages = sys_message_list + messages
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model_name,
            "messages": messages,
            "stream": False
        }
        logger.log('request', f"请求API文本: {data}")
        try:
            response = requests.post(self.chat_url, headers=headers, json=data, timeout=120)
            response.raise_for_status()

            response_data = response.json()
            logger.log('response', f"API返回文本: {response_data}")

            content = ""
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0].get('message', {}).get('content', '')

                self.token_manager.add_txt_message(constant.ASSISTANT_NAME, content)
            else:
                CustomConfirmDialog(title="错误", message="返回数据结构异常")
                logger.log('error', f"返回数据结构异常\n返回数据: {response_data}")
            if self.cancel:
                self.token_manager.remove_a_pair_history()
                return None
            return content
        except Exception as e:
            logger.log('error', e)
            CustomConfirmDialog(title="错误", message="请求异常，稍后重试")
            return None


if __name__ == "__main__":
    txt_generator = OpenaiTextApi()
    response1 = txt_generator.generate_gpt_completion("Tell me a joke.")
    print(f"Assistant: {response1}")
    response2 = txt_generator.generate_gpt_completion("What is the weather like?")
    print(f"Assistant: {response2}")
