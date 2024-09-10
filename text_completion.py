import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from util.token_management import TokenManager

# Load environment variables
load_dotenv()
TOKEN_LIMIT = 8000  # Example limit for GPT-4 (8k tokens)
token_manager = TokenManager(TOKEN_LIMIT)
# Get configuration from environment variables
deployment_name = os.getenv("DEPLOYMENT_NAME")
api_version = os.getenv("API_VERSION")
azure_endpoint = os.getenv("AZURE_ENDPOINT")
api_key = os.getenv("API_KEY")

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key=api_key
)

conversation_history =[]


# Define the token limit (adjust based on the model's context window)

# Initialize a list to keep track of the conversation history


def generate_gpt_completion(user_input):
    # Append the user input to the conversation history
    token_manager.add_txt_message("user", user_input)

    # Manage and trim the conversation history if necessary
    #manage_history()

    try:
        # Generate a completion using the trimmed conversation history
        completion = client.chat.completions.create(
            model=deployment_name,
            messages=token_manager.conversation_txt_history
        )

        # Extract the model's response
        response_content = completion.choices[0].message.content

        # Append the model's response to the conversation history
        token_manager.add_txt_message("assistant", response_content)

        return response_content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



# Example usage
if __name__ == "__main__":
    response1 = generate_gpt_completion("Tell me a joke.")
    print(f"Assistant: {response1}")

    response2 = generate_gpt_completion("What is the weather like?")
    print(f"Assistant: {response2}")
