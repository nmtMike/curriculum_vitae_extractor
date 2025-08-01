import os
from ..base.base_llm import AzureOpenAI

AZURE_OPENAI_KEY = os.environ.get("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://pas-gpt-eastus2.openai.azure.com/")
AZURE_OPENAI_API_VERSION=os.environ.get("AZURE_OPENAI_API_VERSION", "2023-06-01-preview")
AZURE_OPENAI_DEPLOYMENT_NAME=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-eastus2")
AZURE_OPENAI_TEMPERATURE = os.environ.get("AZURE_OPENAI_TEMPERATURE", 0)
AZURE_OPENAI_TOP_P = os.environ.get("AZURE_OPENAI_TOP_P", 1.0)

class OpenAIClient:
    pandas_openai_chat_client = None

    @classmethod
    def create_azure_openai_chat_client(cls,
            api_token=AZURE_OPENAI_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version = AZURE_OPENAI_API_VERSION,
            deployment_name = AZURE_OPENAI_DEPLOYMENT_NAME,
            temperature=AZURE_OPENAI_TEMPERATURE,
            top_p=AZURE_OPENAI_TOP_P,
            presence_penalty = 0,
            max_tokens = 1500,
            is_chat_model = True):
        if not cls.pandas_openai_chat_client:
            cls.pandas_openai_chat_client = AzureOpenAI(
                api_token = api_token,
                azure_endpoint = azure_endpoint,
                api_version = api_version,
                deployment_name = deployment_name,
                temperature = float(temperature),
                presence_penalty = presence_penalty,
                top_p = float(top_p),
                max_tokens = max_tokens,
                is_chat_model = is_chat_model)
        return cls.pandas_openai_chat_client