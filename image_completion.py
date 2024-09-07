# rabiee.sadjad@gmail.com

import webbrowser

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()
deployment_name = os.getenv("DALLE3_DEPLOYMENT_NAME")
api_version="2024-02-01"
azure_endpoint = os.getenv("AZURE_ENDPOINT")
api_key = os.getenv("API_KEY")
client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key=api_key
)

def AI_CreateImage(text, size, n):
    response = client.images.generate(
        model=deployment_name,
        prompt=text,
        size=size,
        quality="standard",
        n=1,
    )
    print(response.data)
    return response.data