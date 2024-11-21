import os
from logging import exception
from tkinter import messagebox

from dotenv import load_dotenv

from util.token_management import TokenManager
import requests
import json

class OpenaiImageApi:
    def __init__(self):
        load_dotenv()
        self.token_manager = TokenManager()
        self.model_name = os.getenv("IMAGE_MODEL_NAME")
        self.api_key = os.getenv("API_KEY")
        self.cancel = False


    def clear_history(self):
        self.token_manager.clear_img_history()

    def add_history_message(self, action, content):
        self.token_manager.add_img_message(action, content)

    def cancel_request(self):
        self.cancel = True

    def create_image_from_text(self, prompt, size, n = 1):
        self.cancel = False
        self.token_manager.add_img_message("Prompt", prompt)
        url = "https://api.deepbricks.ai/v1/images/generations"

        if not self.api_key:
            return
        body = {
            "model": self.model_name,
            "prompt": prompt,
            "size": size,
            "quality": "hd"
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()  # 检查请求是否成功

            # 解析 JSON 响应
            data = response.json()

            image_urls = []
            if 'data' in data and len(data['data']) > 0:
                for item in data['data']:
                    image_url = item.get('url', '')
                    image_urls.append(image_url)
            image_urls_string = ', '.join(image_urls)
            self.token_manager.add_img_message("Response", image_urls_string)
            if self.cancel:
                return None
            return image_urls
        except Exception as e:
            print(f"请求失败: {e}")
            self.token_manager.conversation_txt_history.pop()
            self.token_manager.conversation_txt_history.pop()
            messagebox.showwarning("错误", str(e))


if __name__ == "__main__":
    img_generator = OpenaiImageApi()
    img_generator.create_image_from_text("A scenic ui of mountains", "1024x1024")
