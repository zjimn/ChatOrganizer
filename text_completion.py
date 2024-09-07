import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# 加载 .env 文件
load_dotenv()

# 从环境变量中获取配置
deployment_name = os.getenv("DEPLOYMENT_NAME")
api_version = os.getenv("API_VERSION")
azure_endpoint = os.getenv("AZURE_ENDPOINT")
api_key = os.getenv("API_KEY")

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key=api_key
)

def GPT_Completion(texts):
    completion = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "user", "content": texts}
        ]
    )
    return completion.choices[0].message.content
