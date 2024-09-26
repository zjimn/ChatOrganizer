import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from config import constant
from util.token_management import TokenManager


class OpenaiTextApi:
    def __init__(self):
        self.cancel = None
        load_dotenv()
        self.token_manager = TokenManager(constant.TOKEN_LIMIT)
        self.deployment_name = os.getenv("DEPLOYMENT_NAME")
        self.api_version = os.getenv("API_VERSION")
        self.azure_endpoint = os.getenv("AZURE_ENDPOINT")
        self.api_key = os.getenv("API_KEY")
        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key
        )

    def clear_history(self):
        self.token_manager.clear_txt_history()

    def add_history_message(self, role, message):
        self.token_manager.add_txt_message(role, message)

    def cancel_request(self):
        self.cancel = True

    def generate_gpt_completion(self, user_input, new=False):
        self.cancel = False
        self.token_manager.add_txt_message(constant.DISPLAY_USER_NAME, user_input)
        try:
            completion = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=self.token_manager.conversation_txt_history
            )
            response_content = completion.choices[0].message.content
            self.token_manager.add_txt_message(constant.DISPLAY_ASSISTANT_NAME, response_content)
            if self.cancel:
                return None
            return response_content
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


if __name__ == "__main__":
    txt_generator = OpenaiTextApi()
    response1 = txt_generator.generate_gpt_completion("Tell me a joke.")
    print(f"Assistant: {response1}")
    response2 = txt_generator.generate_gpt_completion("What is the weather like?")
    print(f"Assistant: {response2}")
