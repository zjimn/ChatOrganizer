import os
from dotenv import load_dotenv
from openai import AzureOpenAI

import config
from util.token_management import TokenManager

# Load environment variables

class TextGenerator:
    def __init__(self):
        load_dotenv()
        self.token_manager = TokenManager(config.TOKEN_LIMIT)
        # Get configuration from environment variables
        self.deployment_name = os.getenv("DEPLOYMENT_NAME")
        self.api_version = os.getenv("API_VERSION")
        self.azure_endpoint = os.getenv("AZURE_ENDPOINT")
        self.api_key = os.getenv("API_KEY")

        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key
        )

    def generate_gpt_completion(self, user_input, new=False):
        # Append the user input to the conversation history
        self.token_manager.add_txt_message(config.USER_NAME, user_input)

        # Manage and trim the conversation history if necessary
        # manage_history()

        try:
            # Generate a completion using the trimmed conversation history
            completion = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=self.token_manager.conversation_txt_history
            )

            # Extract the model's response
            response_content = completion.choices[0].message.content

            # Append the model's response to the conversation history
            self.token_manager.add_txt_message(config.ASSISTANT_NAME, response_content)

            return response_content
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


# Example usage
if __name__ == "__main__":
    txt_generator = TextGenerator()
    response1 = txt_generator.generate_gpt_completion("Tell me a joke.")
    print(f"Assistant: {response1}")
    response2 = txt_generator.generate_gpt_completion("What is the weather like?")
    print(f"Assistant: {response2}")
