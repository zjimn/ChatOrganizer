import os
from dotenv import load_dotenv
from openai import AzureOpenAI

from util.token_management import TokenManager

# Load environment variables
load_dotenv()
TOKEN_LIMIT = 8000  # Example limit for GPT-4 (8k tokens)
token_manager = TokenManager(TOKEN_LIMIT)
deployment_name = os.getenv("DALLE_DEPLOYMENT_NAME")
api_version = "2024-02-01"
azure_endpoint = os.getenv("AZURE_ENDPOINT")
api_key = os.getenv("API_KEY")

# Initialize AzureOpenAI client
client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key=api_key
)

# Initialize a list to keep track of the context
context_history = []


def create_image_from_text(text, size, n, new = False):
    if new:
        token_manager.clear_img_history()
    # Append the current prompt to the context history
    token_manager.add_img_message("Prompt", text)
    # Generate images using the context-inclusive prompt
    response = client.images.generate(
        model=deployment_name,
        prompt=token_manager.get_manage_img_history(),
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
    token_manager.add_img_message("Response", image_urls)

    return image_urls


# Example usage
if __name__ == "__main__":
    create_image_from_text("A scenic view of mountains", "1024x1024", 1)
    create_image_from_text("Add a sunset to the scene", "1024x1024", 1)
