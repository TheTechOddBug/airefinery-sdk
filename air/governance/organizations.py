"""Clients for the ``/governance/organizations`` endpoints."""

import aiohttp
import requests

from air import BASE_URL
from air.auth.token_provider import TokenProvider
from air.governance._http import raise_for_status_async, raise_for_status_sync
from air.types.governance import Organization
from air.utils import get_base_headers, get_base_headers_async

ENDPOINT_ORGANIZATIONS = "{base_url}/governance/organizations"
ENDPOINT_ORGANIZATION_ME = "{base_url}/governance/organizations/me"
ENDPOINT_ORGANIZATION_BY_ID = "{base_url}/governance/organizations/{org_id}"


class OrganizationsClient:
    """Synchronous client for organization operations."""

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
        display_name: str | None = None,
        owner_user_id: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Organization:
        """Create a new organization (SUPER_ADMIN only).

        Args:
            name: Unique organization name.
            display_name: Optional human-friendly display name.
            owner_user_id: User UUID to assign as ORG_ADMIN (defaults to caller).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The newly created Organization.
        """
        endpoint = ENDPOINT_ORGANIZATIONS.format(base_url=self.base_url)
        payload: dict = {"name": name}
        if display_name is not None:
            payload["display_name"] = display_name
        if owner_user_id is not None:
            payload["owner_user_id"] = owner_user_id

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
        return Organization.model_validate(response.json())

    def me(
        self,
        *,
        org_id: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Organization:
        """Get the caller's organization.

        Args:
            org_id: Override organization UUID (SUPER_ADMIN only).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The caller's Organization.
        """
        endpoint = ENDPOINT_ORGANIZATION_ME.format(base_url=self.base_url)
        params = {}
        if org_id is not None:
            params["org_id"] = org_id

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
        return Organization.model_validate(response.json())

    def list(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[Organization]:
        """List all organizations (SUPER_ADMIN only).

        Args:
            offset: Number of items to skip (server-side pagination).
            limit: Maximum number of items to return.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            List of Organization objects.
        """
        endpoint = ENDPOINT_ORGANIZATIONS.format(base_url=self.base_url)
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
        return [Organization.model_validate(item) for item in response.json()]

    def get(
        self,
        *,
        org_id: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Organization:
        """Get an organization by ID.

        Args:
            org_id: Organization UUID.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The requested Organization.
        """
        endpoint = ENDPOINT_ORGANIZATION_BY_ID.format(
            base_url=self.base_url,
            org_id=org_id,
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
        return Organization.model_validate(response.json())

    def update(
        self,
        *,
        org_id: str,
        display_name: str | None = None,
        status: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Organization:
        """Update an organization.

        Args:
            org_id: Organization UUID.
            display_name: New display name.
            status: New status (``active``, ``suspended``, or ``deleted``).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The updated Organization.
        """
        endpoint = ENDPOINT_ORGANIZATION_BY_ID.format(
            base_url=self.base_url,
            org_id=org_id,
        )
        payload: dict = {}
        if display_name is not None:
            payload["display_name"] = display_name
        if status is not None:
            payload["status"] = status

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
        return Organization.model_validate(response.json())

    def delete(
        self,
        *,
        org_id: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """Delete an organization (SUPER_ADMIN only).

        Args:
            org_id: Organization UUID.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.
        """
        endpoint = ENDPOINT_ORGANIZATION_BY_ID.format(
            base_url=self.base_url,
            org_id=org_id,
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


class AsyncOrganizationsClient:
    """Asynchronous client for organization operations."""

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
        display_name: str | None = None,
        owner_user_id: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Organization:
        """Create a new organization (SUPER_ADMIN only).

        Args:
            name: Unique organization name.
            display_name: Optional human-friendly display name.
            owner_user_id: User UUID to assign as ORG_ADMIN (defaults to caller).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The newly created Organization.
        """
        endpoint = ENDPOINT_ORGANIZATIONS.format(base_url=self.base_url)
        payload: dict = {"name": name}
        if display_name is not None:
            payload["display_name"] = display_name
        if owner_user_id is not None:
            payload["owner_user_id"] = owner_user_id

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
                return Organization.model_validate(await resp.json())

    async def me(
        self,
        *,
        org_id: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Organization:
        """Get the caller's organization.

        Args:
            org_id: Override organization UUID (SUPER_ADMIN only).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The caller's Organization.
        """
        endpoint = ENDPOINT_ORGANIZATION_ME.format(base_url=self.base_url)
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
            async with session.get(endpoint, params=params, headers=headers) as resp:
                await raise_for_status_async(resp)
                return Organization.model_validate(await resp.json())

    async def list(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[Organization]:
        """List all organizations (SUPER_ADMIN only).

        Args:
            offset: Number of items to skip (server-side pagination).
            limit: Maximum number of items to return.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            List of Organization objects.
        """
        endpoint = ENDPOINT_ORGANIZATIONS.format(base_url=self.base_url)
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
                return [Organization.model_validate(item) for item in await resp.json()]

    async def get(
        self,
        *,
        org_id: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Organization:
        """Get an organization by ID.

        Args:
            org_id: Organization UUID.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The requested Organization.
        """
        endpoint = ENDPOINT_ORGANIZATION_BY_ID.format(
            base_url=self.base_url,
            org_id=org_id,
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
                return Organization.model_validate(await resp.json())

    async def update(
        self,
        *,
        org_id: str,
        display_name: str | None = None,
        status: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Organization:
        """Update an organization.

        Args:
            org_id: Organization UUID.
            display_name: New display name.
            status: New status (``active``, ``suspended``, or ``deleted``).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The updated Organization.
        """
        endpoint = ENDPOINT_ORGANIZATION_BY_ID.format(
            base_url=self.base_url,
            org_id=org_id,
        )
        payload: dict = {}
        if display_name is not None:
            payload["display_name"] = display_name
        if status is not None:
            payload["status"] = status

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
                return Organization.model_validate(await resp.json())

    async def delete(
        self,
        *,
        org_id: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """Delete an organization (SUPER_ADMIN only).

        Args:
            org_id: Organization UUID.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.
        """
        endpoint = ENDPOINT_ORGANIZATION_BY_ID.format(
            base_url=self.base_url,
            org_id=org_id,
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
