"""Clients for the ``/governance/projects`` endpoints."""

from __future__ import annotations

import aiohttp
import requests

from air import BASE_URL
from air.auth.token_provider import TokenProvider
from air.governance._http import raise_for_status_async, raise_for_status_sync
from air.types.governance import Project
from air.utils import get_base_headers, get_base_headers_async

ENDPOINT_PROJECTS = "{base_url}/governance/projects"
ENDPOINT_PROJECT_BY_ID = "{base_url}/governance/projects/{project_id}"


class ProjectsClient:
    """Synchronous client for project operations."""

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

    def list(
        self,
        *,
        org_id: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[Project]:
        """List all projects in the caller's organization.

        Args:
            org_id: Override organization UUID (SUPER_ADMIN only).
            offset: Number of items to skip (server-side pagination).
            limit: Maximum number of items to return.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            List of Project objects.
        """
        endpoint = ENDPOINT_PROJECTS.format(base_url=self.base_url)
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
        return [Project.model_validate(item) for item in response.json()]

    def get(
        self,
        *,
        project_id: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Project:
        """Get a project by ID.

        Args:
            project_id: Project UUID.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The requested Project.
        """
        endpoint = ENDPOINT_PROJECT_BY_ID.format(
            base_url=self.base_url,
            project_id=project_id,
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
        return Project.model_validate(response.json())


class AsyncProjectsClient:
    """Asynchronous client for project operations."""

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

    async def list(
        self,
        *,
        org_id: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[Project]:
        """List all projects in the caller's organization.

        Args:
            org_id: Override organization UUID (SUPER_ADMIN only).
            offset: Number of items to skip (server-side pagination).
            limit: Maximum number of items to return.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            List of Project objects.
        """
        endpoint = ENDPOINT_PROJECTS.format(base_url=self.base_url)
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
                return [Project.model_validate(item) for item in await resp.json()]

    async def get(
        self,
        *,
        project_id: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Project:
        """Get a project by ID.

        Args:
            project_id: Project UUID.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The requested Project.
        """
        endpoint = ENDPOINT_PROJECT_BY_ID.format(
            base_url=self.base_url,
            project_id=project_id,
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
                return Project.model_validate(await resp.json())
