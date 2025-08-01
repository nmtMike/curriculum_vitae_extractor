# Curriculum Vitae Reader

This simple app is designed for information extraction from CVs.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install libraries.

```
pip install requirements.txt
```

## Environment preparation
This app needs LLM from Azure OpenAI to be called via API.

Create a file .env to provide prerequisites

**AZURE_OPENAI_TEMPERATURE** and **AZURE_OPENAI_TOP_P** are set to be default, feel free to change and explore

```AZURE_OPENAI_KEY=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_VERSION=
AZURE_OPENAI_DEPLOYMENT_NAME=
AZURE_OPENAI_TEMPERATURE=0
AZURE_OPENAI_TOP_P=1.0
```
## Run the application

run the app.py and get result in terminal or monitor them in app_log file