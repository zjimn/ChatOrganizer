import os
from dotenv import load_dotenv
from openai import AzureOpenAI

from config import TOKEN_LIMIT
from util.token_management import TokenManager

# Load environment variables

class ImageGenerator:
    def __init__(self):
        load_dotenv()
        self.token_manager = TokenManager(TOKEN_LIMIT)
        self.deployment_name = os.getenv("DALLE_DEPLOYMENT_NAME")
        self.api_version = "2024-02-01"
        self.azure_endpoint = os.getenv("AZURE_ENDPOINT")
        self.api_key = os.getenv("API_KEY")
        self.cancel = False

        # Initialize AzureOpenAI client
        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key
        )

    def clear_history(self):
        self.token_manager.clear_img_history()

    def add_history_message(self,action, content):
        self.token_manager.add_img_message(action, content)

    def cancel_request(self):
        self.cancel = True

    def create_image_from_text(self, text, size, n, new=False):
        self.cancel = False
        # Append the current prompt to the context history
        self.token_manager.add_img_message("Prompt", text)
        # Generate images using the context-inclusive prompt
        response = self.client.images.generate(
            model=self.deployment_name,
            prompt=self.token_manager.get_manage_img_history(),
            size=size,
            quality="standard",
            n=n,
        )

        # Extract response data
        response_data = response.data
        image_urls = []

        # Check if response contains multiple images
        if isinstance(response_data, list):
            for image in response_data:
                image_url = image.url
                image_urls.append(image_url)
        image_urls_string = ', '.join(image_urls)
        self.token_manager.add_img_message("Response", image_urls_string)
        if self.cancel:
            return None
        return image_urls



# Example usage
if __name__ == "__main__":
    img_generator = ImageGenerator()
    img_generator.create_image_from_text("A scenic view of mountains", "1024x1024", 1)
    img_generator.create_image_from_text("Add a sunset to the scene", "1024x1024", 1)