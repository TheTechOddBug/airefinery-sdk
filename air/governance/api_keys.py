"""Clients for the ``/authentication`` API key lifecycle endpoints."""

from __future__ import annotations

import json

import aiohttp
import requests

from air import BASE_URL
from air.auth.token_provider import TokenProvider
from air.governance._http import raise_for_status_async, raise_for_status_sync
from air.types.governance import APIKeyCreated, APIKeyInfo
from air.utils import get_base_headers, get_base_headers_async

ENDPOINT_CREATE = "{base_url}/authentication/create"
ENDPOINT_VALIDATE = "{base_url}/authentication/validate"
ENDPOINT_INSPECT = "{base_url}/authentication/inspect"
ENDPOINT_REVOKE = "{base_url}/authentication/revoke"
ENDPOINT_LIST = "{base_url}/authentication/list"


class APIKeysClient:
    """Synchronous client for API key lifecycle operations.

    Note:
        The ``create`` method requires Studio JWT authentication (not an
        API key). Use a :class:`~air.auth.TokenProvider` for the client's
        ``api_key`` parameter when calling ``create``.
    """

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
        organization_id: str,
        tenant_id: str = "00000000-0000-0000-0000-000000000000",
        label: str = "default",
        lifespans: int = 90,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> APIKeyCreated:
        """Create a new API key.

        Args:
            organization_id: UUID of the target organization. The caller
                must be a member of this organization.
            tenant_id: User UUID. Ignored when governance is enabled (the
                server uses the authenticated caller's identity). Retained
                for backward compatibility with the server schema.
            label: Human-readable label for the key.
            lifespans: Validity period in days (30, 60, 90, 180, or 365;
                default 90).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            APIKeyCreated containing the full key (shown once).
        """
        endpoint = ENDPOINT_CREATE.format(base_url=self.base_url)
        payload = {
            "tenant_id": tenant_id,
            "organization_id": organization_id,
            "label": label,
            "lifespans": lifespans,
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
        return APIKeyCreated.model_validate(response.json())

    def validate(
        self,
        *,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> dict:
        """Validate the current API key and return organization context.

        Args:
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            Dict with ``message`` and ``organization_id``.
        """
        endpoint = ENDPOINT_VALIDATE.format(base_url=self.base_url)

        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.post(
            endpoint,
            headers=headers,
            timeout=timeout if timeout is not None else 60,
        )
        raise_for_status_sync(response)
        return response.json()

    def inspect(
        self,
        *,
        api_key: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> APIKeyInfo:
        """Inspect an API key's metadata.

        Args:
            api_key: The API key to inspect.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            APIKeyInfo with key metadata.
        """
        endpoint = ENDPOINT_INSPECT.format(base_url=self.base_url)
        payload = {"api_key": api_key}

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
        return APIKeyInfo.model_validate(response.json())

    def revoke(
        self,
        *,
        api_key: str | None = None,
        api_key_id: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """Revoke an API key.

        Exactly one of ``api_key`` or ``api_key_id`` must be provided.

        Args:
            api_key: The full API key to revoke.
            api_key_id: UUID of the API key to revoke.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.
        """
        endpoint = ENDPOINT_REVOKE.format(base_url=self.base_url)
        payload: dict[str, str] = {}
        if api_key:
            payload["api_key"] = api_key
        if api_key_id:
            payload["api_key_id"] = api_key_id

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

    def list(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[APIKeyInfo]:
        """List all API keys for the current user.

        Args:
            offset: Number of items to skip (server-side pagination).
            limit: Maximum number of items to return.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            List of APIKeyInfo objects.
        """
        endpoint = ENDPOINT_LIST.format(base_url=self.base_url)
        params = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit

        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.get(
            endpoint,
            params=params,
            headers=headers,
            timeout=timeout if timeout is not None else 60,
        )
        raise_for_status_sync(response)
        return [APIKeyInfo.model_validate(item) for item in response.json()]


class AsyncAPIKeysClient:
    """Asynchronous client for API key lifecycle operations.

    Note:
        The ``create`` method requires Studio JWT authentication (not an
        API key). Use a :class:`~air.auth.TokenProvider` for the client's
        ``api_key`` parameter when calling ``create``.
    """

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
        organization_id: str,
        tenant_id: str = "00000000-0000-0000-0000-000000000000",
        label: str = "default",
        lifespans: int = 90,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> APIKeyCreated:
        """Create a new API key.

        Args:
            organization_id: UUID of the target organization. The caller
                must be a member of this organization.
            tenant_id: User UUID. Ignored when governance is enabled (the
                server uses the authenticated caller's identity). Retained
                for backward compatibility with the server schema.
            label: Human-readable label for the key.
            lifespans: Validity period in days (30, 60, 90, 180, or 365;
                default 90).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            APIKeyCreated containing the full key (shown once).
        """
        endpoint = ENDPOINT_CREATE.format(base_url=self.base_url)
        payload = {
            "tenant_id": tenant_id,
            "organization_id": organization_id,
            "label": label,
            "lifespans": lifespans,
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
                if resp.content_type == "application/json":
                    return APIKeyCreated.model_validate(await resp.json())
                else:
                    return APIKeyCreated.model_validate(json.loads(await resp.text()))

    async def validate(
        self,
        *,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> dict:
        """Validate the current API key and return organization context.

        Args:
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            Dict with ``message`` and ``organization_id``.
        """
        endpoint = ENDPOINT_VALIDATE.format(base_url=self.base_url)

        headers = await get_base_headers_async(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        client_timeout = aiohttp.ClientTimeout(
            total=timeout if timeout is not None else 60,
        )
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.post(endpoint, headers=headers) as resp:
                await raise_for_status_async(resp)
                return await resp.json()

    async def inspect(
        self,
        *,
        api_key: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> APIKeyInfo:
        """Inspect an API key's metadata.

        Args:
            api_key: The API key to inspect.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            APIKeyInfo with key metadata.
        """
        endpoint = ENDPOINT_INSPECT.format(base_url=self.base_url)
        payload = {"api_key": api_key}

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
                return APIKeyInfo.model_validate(await resp.json())

    async def revoke(
        self,
        *,
        api_key: str | None = None,
        api_key_id: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """Revoke an API key.

        Exactly one of ``api_key`` or ``api_key_id`` must be provided.

        Args:
            api_key: The full API key to revoke.
            api_key_id: UUID of the API key to revoke.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.
        """
        endpoint = ENDPOINT_REVOKE.format(base_url=self.base_url)
        payload: dict[str, str] = {}
        if api_key:
            payload["api_key"] = api_key
        if api_key_id:
            payload["api_key_id"] = api_key_id

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

    async def list(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[APIKeyInfo]:
        """List all API keys for the current user.

        Args:
            offset: Number of items to skip (server-side pagination).
            limit: Maximum number of items to return.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            List of APIKeyInfo objects.
        """
        endpoint = ENDPOINT_LIST.format(base_url=self.base_url)
        params = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit

        headers = await get_base_headers_async(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        client_timeout = aiohttp.ClientTimeout(
            total=timeout if timeout is not None else 60,
        )
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.get(endpoint, params=params, headers=headers) as resp:
                await raise_for_status_async(resp)
                return [APIKeyInfo.model_validate(item) for item in await resp.json()]
