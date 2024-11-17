import os
from logging import exception
from tkinter import messagebox

from dotenv import load_dotenv
from config import constant
from util.resource_util import resource_path
from util.token_management import TokenManager
import requests
import json

class OpenaiTextApi:
    def __init__(self):
        self.cancel = None
        self.token_manager = TokenManager()
        dotenv_path = resource_path('.env')
        load_dotenv(dotenv_path)
        self.model_name = os.getenv("MODEL_NAME")
        self.api_key = os.getenv("API_KEY")


    def clear_history(self):
        self.token_manager.clear_txt_history()

    def add_history_message(self, role, message):
        self.token_manager.add_txt_message(role, message)

    def cancel_request(self):
        self.cancel = True


    def generate_gpt_completion(self, user_input):
        self.cancel = False
        self.token_manager.add_txt_message(constant.USER_NAME, user_input)
        url = "https://api.deepbricks.ai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": self.model_name,

            "messages": self.token_manager.conversation_txt_history,
            "stream": False
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # 检查请求是否成功

            # 解析完整的 JSON 响应
            response_data = response.json()

            # 根据 API 的具体响应格式提取 'content'
            # 假设 'choices' 列表中包含生成的内容
            content = ""
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0].get('message', {}).get('content', '')
                self.token_manager.add_txt_message(constant.ASSISTANT_NAME, content)

                print(content)
            else:
                print("未找到生成的内容。")
            if self.cancel:
                return None
            return content
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            messagebox.showwarning("错误", str(e))
            return None
        except json.JSONDecodeError as e:
            print("响应内容不是有效的 JSON 格式。")
            messagebox.showwarning("错误", str(e))
            return None
        except exception as e:
            print("响应内容不是有效的 JSON 格式。")
            messagebox.showwarning("错误", str(e))
            return None


if __name__ == "__main__":
    txt_generator = OpenaiTextApi()
    response1 = txt_generator.generate_gpt_completion("Tell me a joke.")
    print(f"Assistant: {response1}")
    response2 = txt_generator.generate_gpt_completion("What is the weather like?")
    print(f"Assistant: {response2}")
