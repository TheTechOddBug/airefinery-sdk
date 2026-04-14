"""Clients for the ``/governance`` models endpoints."""

from __future__ import annotations

import urllib.parse
from typing import Any, Dict, Literal, Union

import aiohttp
import requests
from air import BASE_URL
from air.auth.token_provider import TokenProvider
from air.governance._http import raise_for_status_async, raise_for_status_sync
from air.governance.exceptions import UnprocessableContentError
from air.types.governance import (
    CLIENT_CONFIG_REGISTRY,
    EmbeddingClientConfig,
    LLMClientConfig,
    Model,
)
from air.utils import get_base_headers, get_base_headers_async
from pydantic import BaseModel

ENDPOINT_CREATE_MODEL = "{base_url}/governance/models/create"
ENDPOINT_UPDATE_MODEL = "{base_url}/governance/models/update"
ENDPOINT_LIST_MODELS = "{base_url}/governance/models/list"
ENDPOINT_REMOVE_MODEL = "{base_url}/governance/models/delete"


class ModelsClient:
    """Synchronous client for model registry operations."""

    def __init__(
        self,
        api_key: str | TokenProvider,
        *,
        base_url: str = BASE_URL,
        default_headers: dict[str, str] | None = None,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.default_headers = default_headers or {}

    def create(
        self,
        *,
        model_name: str,
        model_type: Literal["llm", "embedding"],
        config: Union[LLMClientConfig, EmbeddingClientConfig],
        status: bool = True,
        description: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Dict[str, Any]:
        """Create a private model.

        Args:
            model_name: Name of the private model.
            model_type: Type of the model ("llm" or "embedding").
            config: Configuration dictionary for the private model.
            status: Whether the private model is active.
            description: Description of the private model.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The created Model response.
        """
        endpoint = ENDPOINT_CREATE_MODEL.format(base_url=self.base_url)
        try:
            validated_config = CLIENT_CONFIG_REGISTRY[model_type].model_validate(config)
        except KeyError as e:
            raise UnprocessableContentError(
                f"Unsupported model type: {model_type}"
            ) from e
        except Exception as e:
            raise UnprocessableContentError("Invalid model configuration") from e

        payload = {
            "model_name": model_name,
            "model_type": model_type,
            "config": validated_config.model_dump(),
            "status": status,
            "description": description,
        }

        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=timeout if timeout is not None else 60,
        )
        raise_for_status_sync(response)
        return response.json()

    def update(
        self,
        *,
        model_name: str,
        status: bool | None = None,
        description: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Dict[str, Any]:
        """Update a private model.

        Args:
            model_name: Name of the private model.
            status: Whether the private model is active.
            description: Description of the private model.
            base_url: Base URL to update in the model's configuration.
            api_key: API Key to update in the model's configuration.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The updated Model response.
        """
        endpoint = ENDPOINT_UPDATE_MODEL.format(base_url=self.base_url)
        payload: Dict[str, Any] = {"model_name": model_name}

        if status is not None:
            payload["status"] = status
        if description is not None:
            payload["description"] = description
        if base_url is not None:
            payload["base_url"] = base_url
        if api_key is not None:
            payload["api_key"] = api_key

        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=timeout if timeout is not None else 60,
        )
        raise_for_status_sync(response)
        return response.json()

    def list(
        self,
        *,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[Model]:
        """List all available private models.

        Args:
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            List of model dictionaries.
        """
        endpoint = ENDPOINT_LIST_MODELS.format(base_url=self.base_url)

        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.get(
            endpoint,
            headers=headers,
            timeout=timeout if timeout is not None else 60,
        )
        raise_for_status_sync(response)
        return [Model.model_validate(item) for item in response.json()]

    def delete(
        self,
        *,
        model_name: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Dict[str, Any]:
        """Delete an existing private model.

        Args:
            model_name: Name of the private model to delete.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            Response dictionary.
        """
        encoded_model_name = urllib.parse.quote(model_name, safe="")
        endpoint = ENDPOINT_REMOVE_MODEL.format(base_url=self.base_url)
        params = {"model_name": encoded_model_name}

        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.delete(
            endpoint,
            params=params,
            headers=headers,
            timeout=timeout if timeout is not None else 60,
        )
        raise_for_status_sync(response)
        return response.json()


class AsyncModelsClient:
    """Asynchronous client for model registry operations."""

    def __init__(
        self,
        api_key: str | TokenProvider,
        *,
        base_url: str = BASE_URL,
        default_headers: dict[str, str] | None = None,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.default_headers = default_headers or {}

    async def create(
        self,
        *,
        model_name: str,
        model_type: Literal["llm", "embedding"],
        config: Union[LLMClientConfig, EmbeddingClientConfig],
        status: bool = True,
        description: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Dict[str, Any]:
        """Create a private model.

        Args:
            model_name: Name of the private model.
            model_type: Type of the model ("llm" or "embedding").
            config: Configuration dictionary for the private model.
            status: Whether the private model is active.
            description: Description of the private model.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The created Model response.
        """
        endpoint = ENDPOINT_CREATE_MODEL.format(base_url=self.base_url)
        try:
            validated_config = CLIENT_CONFIG_REGISTRY[model_type].model_validate(config)
        except KeyError as e:
            raise UnprocessableContentError(
                f"Unsupported model type: {model_type}"
            ) from e
        except Exception as e:
            raise UnprocessableContentError("Invalid model configuration") from e

        payload = {
            "model_name": model_name,
            "model_type": model_type,
            "config": validated_config.model_dump(),
            "status": status,
            "description": description,
        }

        headers = await get_base_headers_async(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        client_timeout = aiohttp.ClientTimeout(
            total=timeout if timeout is not None else 60,
        )
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.post(endpoint, json=payload, headers=headers) as resp:
                await raise_for_status_async(resp)
                return await resp.json()

    async def update(
        self,
        *,
        model_name: str,
        status: bool | None = None,
        description: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Dict[str, Any]:
        """Update a private model.

        Args:
            model_name: Name of the private model.
            status: Whether the private model is active.
            description: Description of the private model.
            base_url: Base URL to update in the model's configuration.
            api_key: API Key to update in the model's configuration.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The updated Model response.
        """
        endpoint = ENDPOINT_UPDATE_MODEL.format(base_url=self.base_url)
        payload: Dict[str, Any] = {"model_name": model_name}

        if status is not None:
            payload["status"] = status
        if description is not None:
            payload["description"] = description
        if base_url is not None:
            payload["base_url"] = base_url
        if api_key is not None:
            payload["api_key"] = api_key

        headers = await get_base_headers_async(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        client_timeout = aiohttp.ClientTimeout(
            total=timeout if timeout is not None else 60,
        )
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.post(endpoint, json=payload, headers=headers) as resp:
                await raise_for_status_async(resp)
                return await resp.json()

    async def list(
        self,
        *,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[Model]:
        """List all available private models.

        Args:
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            List of model dictionaries.
        """
        endpoint = ENDPOINT_LIST_MODELS.format(base_url=self.base_url)

        headers = await get_base_headers_async(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        client_timeout = aiohttp.ClientTimeout(
            total=timeout if timeout is not None else 60,
        )
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.get(endpoint, headers=headers) as resp:
                await raise_for_status_async(resp)
                return [Model.model_validate(item) for item in await resp.json()]

    async def delete(
        self,
        *,
        model_name: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Dict[str, Any]:
        """Delete an existing private model.

        Args:
            model_name: Name of the private model to delete.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            Response dictionary.
        """
        encoded_model_name = urllib.parse.quote(model_name, safe="")
        endpoint = ENDPOINT_REMOVE_MODEL.format(base_url=self.base_url)
        params = {"model_name": encoded_model_name}

        headers = await get_base_headers_async(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        client_timeout = aiohttp.ClientTimeout(
            total=timeout if timeout is not None else 60,
        )
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.delete(endpoint, params=params, headers=headers) as resp:
                await raise_for_status_async(resp)
                return await resp.json()
