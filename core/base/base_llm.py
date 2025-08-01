""" Base class to implement a new LLM

This is the base class to integrate the various LLMs API

Example:

    ```
    from .base import BaseOpenAI

    class CustomLLM(BaseOpenAI):

        Custom Class Starts here!!
    ```
"""
import os
import openai

from abc import abstractmethod
from packaging.version import parse
from importlib.metadata import version
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Tuple, Union, Callable
from ..helper.error_exception.error_exception import NoCodeFoundError, MethodNotImplementedError

class APIKeyNotFoundError(Exception):
    """
    Raised when the API key is not defined/declared.

    Args:
        Exception (Exception): APIKeyNotFoundError
    """

def is_openai_v1() -> bool:
    _version = parse(version("openai"))
    return _version.major >= 1


class LLM:
    """Base class to implement a new LLM."""

    last_prompt: Optional[str] = None

    @property
    def type(self) -> str:
        """
        Return type of LLM.

        Raises:
            APIKeyNotFoundError: Type has not been implemented

        Returns:
            str: Type of LLM a string

        """
        raise APIKeyNotFoundError("Type has not been implemented")

    def prepend_system_prompt(self):
        pass

    def get_system_prompt(self) -> Any:
        pass

    def get_messages(self) -> Any:
        pass

    def _extract_tag_text(self) -> Any:
        pass

    def completion(self) -> Any:
        pass

    @abstractmethod
    def chat_completion(self) -> Any:
        pass

class BaseOpenAI(LLM):
    """Base class to implement a new OpenAI LLM.

    LLM base class, this class is extended to be used with OpenAI API.

    """

    api_token: str
    api_base: str = "https://api.openai.com/v1"
    temperature: float = 0
    max_tokens: int = 1000
    top_p: float = 1
    frequency_penalty: float = 0
    presence_penalty: float = 0.6
    best_of: int = 1
    n: int = 1
    stop: Optional[str] = None
    request_timeout: Union[float, Tuple[float, float], Any, None] = None
    max_retries: int = 2
    seed: Optional[int] = None
    # support explicit proxy for OpenAI
    openai_proxy: Optional[str] = None
    default_headers: Union[Mapping[str, str], None] = None
    default_query: Union[Mapping[str, object], None] = None
    # Configure a custom httpx client. See the
    # [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
    http_client: Union[Any, None] = None
    client: Any
    _is_chat_model: bool

    def _set_params(self, **kwargs):
        """
        Set Parameters
        Args:
            **kwargs: ["model", "deployment_name", "temperature","max_tokens",
            "top_p", "frequency_penalty", "presence_penalty", "stop", "seed"]

        Returns:
            None.

        """

        valid_params = [
            "model",
            "deployment_name",
            "temperature",
            "max_tokens",
            "top_p",
            "frequency_penalty",
            "presence_penalty",
            "stop",
            "seed",
        ]
        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self, key, value)

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        params: Dict[str, Any] = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "seed": self.seed,
            "stop": self.stop,
            "n": self.n,
        }

        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens

        # Azure gpt-35-turbo doesn't support best_of
        # don't specify best_of if it is 1
        if self.best_of > 1:
            params["best_of"] = self.best_of

        return params

    @property
    def _invocation_params(self) -> Dict[str, Any]:
        """Get the parameters used to invoke the model."""
        openai_creds: Dict[str, Any] = {}
        if not is_openai_v1():
            openai_creds |= {
                "api_key": self.api_token,
                "api_base": self.api_base,
            }

        return {**openai_creds, **self._default_params}

    @property
    def _client_params(self) -> Dict[str, any]:
        return {
            "api_key": self.api_token,
            "base_url": self.api_base,
            "timeout": self.request_timeout,
            "max_retries": self.max_retries,
            "default_headers": self.default_headers,
            "default_query": self.default_query,
            "http_client": self.http_client,
        }

    def chat_completion(self, value: str) -> str:
        """
        Query the chat completion API

        Args:
            value (str): Prompt

        Returns:
            str: LLM response.

        """
        messages = []

        # adding current prompt as latest query message
        messages.append(
            {
                "role": "user",
                "content": value,
            },
        )

        params = {
            **self._invocation_params,
            "messages": messages,
        }

        if self.stop is not None:
            params["stop"] = [self.stop]

        response = self.client.create(**params)

        return response.choices[0].message.content


class AzureOpenAI(BaseOpenAI):
    """OpenAI LLM via Microsoft Azure
    This class uses `BaseOpenAI` class to support Azure OpenAI features.
    """

    azure_endpoint: Union[str, None] = None
    """Your Azure Active Directory token.
        Automatically inferred from env var `AZURE_OPENAI_AD_TOKEN` if not provided.
        For more: 
        https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id.
    """
    azure_ad_token: Union[str, None] = None
    """A function that returns an Azure Active Directory token.
        Will be invoked on every request.
    """
    azure_ad_token_provider: Union[Callable[[], str], None] = None
    deployment_name: str
    api_version: str = ""
    """Legacy, for openai<1.0.0 support."""
    api_base: str
    """Legacy, for openai<1.0.0 support."""
    api_type: str = "azure"

    def __init__(
        self,
        api_token: Optional[str] = None,
        azure_endpoint: Union[str, None] = None,
        azure_ad_token: Union[str, None] = None,
        azure_ad_token_provider: Union[Callable[[], str], None] = None,
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
        deployment_name: str = None,
        is_chat_model: bool = True,
        **kwargs,
    ):
        """
        __init__ method of AzureOpenAI Class.

        Args:
            api_token (str): Azure OpenAI API token.
            azure_endpoint (str): Azure endpoint.
                It should look like the following:
                <https://YOUR_RESOURCE_NAME.openai.azure.com/>
            azure_ad_token (str): Your Azure Active Directory token.
                Automatically inferred from env var `AZURE_OPENAI_AD_TOKEN` if not provided.
                For more: https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id.
            azure_ad_token_provider (str): A function that returns an Azure Active Directory token.
                Will be invoked on every request.
            api_version (str): Version of the Azure OpenAI API.
                Be aware the API version may change.
            api_base (str): Legacy, kept for backward compatibility with openai < 1.0.
                Ignored for openai >= 1.0.
            deployment_name (str): Custom name of the deployed model
            is_chat_model (bool): Whether ``deployment_name`` corresponds to a Chat
                or a Completion model.
            **kwargs: Inference Parameters.
        """

        self.api_token = (
            api_token
            or os.getenv("AZURE_OPENAI_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_base = api_base or os.getenv("OPENAI_API_BASE")
        self.api_version = api_version or os.getenv("OPENAI_API_VERSION")
        if self.api_token is None:
            raise APIKeyNotFoundError(
                "Azure OpenAI key is required. Please add an environment variable "
                "`AZURE_OPENAI_API_KEY` or `OPENAI_API_KEY` or pass `api_token` as a named parameter"
            )
        if is_openai_v1():
            if self.azure_endpoint is None:
                raise APIKeyNotFoundError(
                    "Azure endpoint is required. Please add an environment variable "
                    "`AZURE_OPENAI_API_ENDPOINT` or pass `azure_endpoint` as a named parameter"
                )
        elif self.api_base is None:
            raise APIKeyNotFoundError(
                "Azure OpenAI base is required. Please add an environment variable "
                "`OPENAI_API_BASE` or pass `api_base` as a named parameter"
            )

        if self.api_version is None:
            raise APIKeyNotFoundError(
                "Azure OpenAI version is required. Please add an environment variable "
                "`OPENAI_API_VERSION` or pass `api_version` as a named parameter"
            )

        if deployment_name is None:
            raise MissingModelError(
                "No deployment name provided.",
                "Please include deployment name from Azure dashboard.",
            )
        self.azure_ad_token = azure_ad_token or os.getenv("AZURE_OPENAI_AD_TOKEN")
        self.azure_ad_token_provider = azure_ad_token_provider
        self._is_chat_model = is_chat_model
        self.deployment_name = deployment_name

        self.openai_proxy = kwargs.get("openai_proxy") or os.getenv("OPENAI_PROXY")
        if self.openai_proxy:
            openai.proxy = {"http": self.openai_proxy, "https": self.openai_proxy}

        self._set_params(**kwargs)
        # set the client
        if self._is_chat_model:
            self.client = (
                openai.AzureOpenAI(**self._client_params).chat.completions
                if is_openai_v1()
                else openai.ChatCompletion
            )
        else:
            self.client = (
                openai.AzureOpenAI(**self._client_params).completions
                if is_openai_v1()
                else openai.Completion
            )

    @property
    def _default_params(self) -> Dict[str, Any]:
        """
        Get the default parameters for calling OpenAI API.

        Returns:
            dict: A dictionary containing Default Params.

        """
        return {
            **super()._default_params,
            "model" if is_openai_v1() else "engine": self.deployment_name,
        }

    @property
    def _invocation_params(self) -> Dict[str, Any]:
        """Get the parameters used to invoke the model."""
        if is_openai_v1():
            return super()._invocation_params
        else:
            return {
                **super()._invocation_params,
                "api_type": self.api_type,
                "api_version": self.api_version,
            }

    @property
    def _client_params(self) -> Dict[str, any]:
        client_params = {
            "api_version": self.api_version,
            "azure_endpoint": self.azure_endpoint,
            "azure_deployment": self.deployment_name,
            "azure_ad_token": self.azure_ad_token,
            "azure_ad_token_provider": self.azure_ad_token_provider,
        }
        return {**client_params, **super()._client_params}

    @property
    def type(self) -> str:
        return "azure-openai"
