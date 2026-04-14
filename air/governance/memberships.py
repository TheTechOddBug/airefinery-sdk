"""Clients for the ``/governance/memberships`` endpoints."""

from __future__ import annotations

import aiohttp
import requests

from air import BASE_URL
from air.auth.token_provider import TokenProvider
from air.governance._http import raise_for_status_async, raise_for_status_sync
from air.types.governance import OrgMembership
from air.utils import get_base_headers, get_base_headers_async

ENDPOINT_MEMBERSHIPS = "{base_url}/governance/memberships"
ENDPOINT_MEMBERSHIP_ROLE = "{base_url}/governance/memberships/role"


class MembershipsClient:
    """Synchronous client for membership operations."""

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
        user_id: str,
        org_id: str | None = None,
        role: str = "ORG_MEMBER",
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> OrgMembership:
        """Add a user to an organization (SUPER_ADMIN or ORG_ADMIN only).

        Args:
            user_id: UUID of the user to add.
            org_id: Target organization UUID (defaults to caller's org).
            role: RBAC role to assign (default ``ORG_MEMBER``).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The newly created OrgMembership.
        """
        endpoint = ENDPOINT_MEMBERSHIPS.format(base_url=self.base_url)
        payload: dict = {"user_id": user_id, "role": role}
        if org_id is not None:
            payload["org_id"] = org_id

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
        return OrgMembership.model_validate(response.json())

    def list(
        self,
        *,
        org_id: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[OrgMembership]:
        """List all memberships in the caller's organization.

        Args:
            org_id: Override organization UUID (SUPER_ADMIN only).
            offset: Number of items to skip (server-side pagination).
            limit: Maximum number of items to return.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            List of OrgMembership objects.
        """
        endpoint = ENDPOINT_MEMBERSHIPS.format(base_url=self.base_url)
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
        return [OrgMembership.model_validate(item) for item in response.json()]

    def update_role(
        self,
        *,
        user_id: str,
        role: str,
        org_id: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """Update a user's role in the organization.

        Args:
            user_id: UUID of the user whose role to update.
            role: New role (``SUPER_ADMIN``, ``ORG_ADMIN``, ``ORG_MEMBER``,
                or ``ORG_VIEWER``).
            org_id: Override organization UUID (SUPER_ADMIN only).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.
        """
        endpoint = ENDPOINT_MEMBERSHIP_ROLE.format(base_url=self.base_url)
        payload = {"user_id": user_id, "role": role}
        params = {}
        if org_id is not None:
            params["org_id"] = org_id

        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.put(
            endpoint,
            json=payload,
            params=params,
            headers=headers,
            timeout=timeout if timeout is not None else 60,
        )
        raise_for_status_sync(response)

    def delete(
        self,
        *,
        user_id: str,
        org_id: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """Remove a user from an organization.

        Args:
            user_id: UUID of the user to remove.
            org_id: Target organization UUID (defaults to caller's org).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.
        """
        endpoint = ENDPOINT_MEMBERSHIPS.format(base_url=self.base_url)
        payload: dict = {"user_id": user_id}
        if org_id is not None:
            payload["org_id"] = org_id

        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.delete(
            endpoint,
            json=payload,
            headers=headers,
            timeout=timeout if timeout is not None else 60,
        )
        raise_for_status_sync(response)


class AsyncMembershipsClient:
    """Asynchronous client for membership operations."""

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
        user_id: str,
        org_id: str | None = None,
        role: str = "ORG_MEMBER",
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> OrgMembership:
        """Add a user to an organization (SUPER_ADMIN or ORG_ADMIN only).

        Args:
            user_id: UUID of the user to add.
            org_id: Target organization UUID (defaults to caller's org).
            role: RBAC role to assign (default ``ORG_MEMBER``).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The newly created OrgMembership.
        """
        endpoint = ENDPOINT_MEMBERSHIPS.format(base_url=self.base_url)
        payload: dict = {"user_id": user_id, "role": role}
        if org_id is not None:
            payload["org_id"] = org_id

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
                return OrgMembership.model_validate(await resp.json())

    async def list(
        self,
        *,
        org_id: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[OrgMembership]:
        """List all memberships in the caller's organization.

        Args:
            org_id: Override organization UUID (SUPER_ADMIN only).
            offset: Number of items to skip (server-side pagination).
            limit: Maximum number of items to return.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            List of OrgMembership objects.
        """
        endpoint = ENDPOINT_MEMBERSHIPS.format(base_url=self.base_url)
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
                return [
                    OrgMembership.model_validate(item) for item in await resp.json()
                ]

    async def update_role(
        self,
        *,
        user_id: str,
        role: str,
        org_id: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """Update a user's role in the organization.

        Args:
            user_id: UUID of the user whose role to update.
            role: New role (``SUPER_ADMIN``, ``ORG_ADMIN``, ``ORG_MEMBER``,
                or ``ORG_VIEWER``).
            org_id: Override organization UUID (SUPER_ADMIN only).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.
        """
        endpoint = ENDPOINT_MEMBERSHIP_ROLE.format(base_url=self.base_url)
        payload = {"user_id": user_id, "role": role}
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
            async with session.put(
                endpoint, json=payload, params=params, headers=headers
            ) as resp:
                await raise_for_status_async(resp)

    async def delete(
        self,
        *,
        user_id: str,
        org_id: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """Remove a user from an organization.

        Args:
            user_id: UUID of the user to remove.
            org_id: Target organization UUID (defaults to caller's org).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.
        """
        endpoint = ENDPOINT_MEMBERSHIPS.format(base_url=self.base_url)
        payload: dict = {"user_id": user_id}
        if org_id is not None:
            payload["org_id"] = org_id

        headers = await get_base_headers_async(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        client_timeout = aiohttp.ClientTimeout(
            total=timeout if timeout is not None else 60,
        )
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.delete(endpoint, json=payload, headers=headers) as resp:
                await raise_for_status_async(resp)
