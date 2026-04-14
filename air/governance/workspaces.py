"""Clients for the ``/governance/workspaces`` endpoints."""

from __future__ import annotations

import aiohttp
import requests

from air import BASE_URL
from air.auth.token_provider import TokenProvider
from air.governance._http import raise_for_status_async, raise_for_status_sync
from air.types.governance import Workspace
from air.utils import get_base_headers, get_base_headers_async

ENDPOINT_WORKSPACES = "{base_url}/governance/workspaces"
ENDPOINT_WORKSPACE_BY_ID = "{base_url}/governance/workspaces/{workspace_id}"


class WorkspacesClient:
    """Synchronous client for workspace operations."""

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
        name: str,
        description: str | None = None,
        org_id: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Workspace:
        """Create a workspace in the caller's organization.

        Args:
            name: Workspace name (must be unique within the org).
            description: Optional workspace description.
            org_id: Override organization UUID (SUPER_ADMIN only).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The newly created Workspace.
        """
        endpoint = ENDPOINT_WORKSPACES.format(base_url=self.base_url)
        payload: dict = {"name": name}
        if description is not None:
            payload["description"] = description
        params = {}
        if org_id is not None:
            params["org_id"] = org_id

        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.post(
            endpoint,
            json=payload,
            params=params,
            headers=headers,
            timeout=timeout if timeout is not None else 60,
        )
        raise_for_status_sync(response)
        return Workspace.model_validate(response.json())

    def list(
        self,
        *,
        org_id: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[Workspace]:
        """List all workspaces in the caller's organization.

        Args:
            org_id: Override organization UUID (SUPER_ADMIN only).
            offset: Number of items to skip (server-side pagination).
            limit: Maximum number of items to return.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            List of Workspace objects.
        """
        endpoint = ENDPOINT_WORKSPACES.format(base_url=self.base_url)
        params = {}
        if org_id is not None:
            params["org_id"] = org_id
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
        return [Workspace.model_validate(item) for item in response.json()]

    def get(
        self,
        *,
        workspace_id: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Workspace:
        """Get a workspace by ID.

        Args:
            workspace_id: Workspace UUID.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The requested Workspace.
        """
        endpoint = ENDPOINT_WORKSPACE_BY_ID.format(
            base_url=self.base_url,
            workspace_id=workspace_id,
        )

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
        return Workspace.model_validate(response.json())

    def update(
        self,
        *,
        workspace_id: str,
        name: str | None = None,
        description: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Workspace:
        """Update a workspace.

        Args:
            workspace_id: Workspace UUID.
            name: New workspace name.
            description: New description.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The updated Workspace.
        """
        endpoint = ENDPOINT_WORKSPACE_BY_ID.format(
            base_url=self.base_url,
            workspace_id=workspace_id,
        )
        payload: dict = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.put(
            endpoint,
            json=payload,
            headers=headers,
            timeout=timeout if timeout is not None else 60,
        )
        raise_for_status_sync(response)
        return Workspace.model_validate(response.json())

    def delete(
        self,
        *,
        workspace_id: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """Delete a workspace.

        Args:
            workspace_id: Workspace UUID.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.
        """
        endpoint = ENDPOINT_WORKSPACE_BY_ID.format(
            base_url=self.base_url,
            workspace_id=workspace_id,
        )

        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.delete(
            endpoint,
            headers=headers,
            timeout=timeout if timeout is not None else 60,
        )
        raise_for_status_sync(response)


class AsyncWorkspacesClient:
    """Asynchronous client for workspace operations."""

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
        name: str,
        description: str | None = None,
        org_id: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Workspace:
        """Create a workspace in the caller's organization.

        Args:
            name: Workspace name (must be unique within the org).
            description: Optional workspace description.
            org_id: Override organization UUID (SUPER_ADMIN only).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The newly created Workspace.
        """
        endpoint = ENDPOINT_WORKSPACES.format(base_url=self.base_url)
        payload: dict = {"name": name}
        if description is not None:
            payload["description"] = description
        params = {}
        if org_id is not None:
            params["org_id"] = org_id

        headers = await get_base_headers_async(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        client_timeout = aiohttp.ClientTimeout(
            total=timeout if timeout is not None else 60,
        )
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.post(
                endpoint, json=payload, params=params, headers=headers
            ) as resp:
                await raise_for_status_async(resp)
                return Workspace.model_validate(await resp.json())

    async def list(
        self,
        *,
        org_id: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[Workspace]:
        """List all workspaces in the caller's organization.

        Args:
            org_id: Override organization UUID (SUPER_ADMIN only).
            offset: Number of items to skip (server-side pagination).
            limit: Maximum number of items to return.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            List of Workspace objects.
        """
        endpoint = ENDPOINT_WORKSPACES.format(base_url=self.base_url)
        params = {}
        if org_id is not None:
            params["org_id"] = org_id
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
                return [Workspace.model_validate(item) for item in await resp.json()]

    async def get(
        self,
        *,
        workspace_id: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Workspace:
        """Get a workspace by ID.

        Args:
            workspace_id: Workspace UUID.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The requested Workspace.
        """
        endpoint = ENDPOINT_WORKSPACE_BY_ID.format(
            base_url=self.base_url,
            workspace_id=workspace_id,
        )

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
                return Workspace.model_validate(await resp.json())

    async def update(
        self,
        *,
        workspace_id: str,
        name: str | None = None,
        description: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Workspace:
        """Update a workspace.

        Args:
            workspace_id: Workspace UUID.
            name: New workspace name.
            description: New description.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The updated Workspace.
        """
        endpoint = ENDPOINT_WORKSPACE_BY_ID.format(
            base_url=self.base_url,
            workspace_id=workspace_id,
        )
        payload: dict = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        headers = await get_base_headers_async(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        client_timeout = aiohttp.ClientTimeout(
            total=timeout if timeout is not None else 60,
        )
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.put(endpoint, json=payload, headers=headers) as resp:
                await raise_for_status_async(resp)
                return Workspace.model_validate(await resp.json())

    async def delete(
        self,
        *,
        workspace_id: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """Delete a workspace.

        Args:
            workspace_id: Workspace UUID.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.
        """
        endpoint = ENDPOINT_WORKSPACE_BY_ID.format(
            base_url=self.base_url,
            workspace_id=workspace_id,
        )

        headers = await get_base_headers_async(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        client_timeout = aiohttp.ClientTimeout(
            total=timeout if timeout is not None else 60,
        )
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.delete(endpoint, headers=headers) as resp:
                await raise_for_status_async(resp)
