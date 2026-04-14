"""Clients for the ``/governance/users`` endpoints."""

from __future__ import annotations

import json

import aiohttp
import requests

from air import BASE_URL
from air.auth.token_provider import TokenProvider
from air.governance._http import (
    raise_for_status_async,
    raise_for_status_sync,
)
from air.types.governance.user import User
from air.utils import (
    get_base_headers,
    get_base_headers_async,
)

ENDPOINT_USERS = "{base_url}/governance/users"
ENDPOINT_USERS_ME = "{base_url}/governance/users/me"
ENDPOINT_USER_BY_ID = "{base_url}/governance/users/{user_id}"


class UsersClient:
    """Synchronous client for user operations."""

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
        email: str,
        external_id: str | None = None,
        display_name: str | None = None,
        org_id: str | None = None,
        role: str = "ORG_MEMBER",
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> User:
        """Create a new user (SUPER_ADMIN or ORG_ADMIN only).

        Args:
            email: User email address.
            external_id: External IdP identifier (e.g. Azure AD oid).
            display_name: Optional human-friendly display name.
            org_id: Target organization UUID (SUPER_ADMIN can specify any,
                ORG_ADMIN uses their own).
            role: RBAC role to assign (default ``ORG_MEMBER``).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The newly created User.
        """
        endpoint = ENDPOINT_USERS.format(base_url=self.base_url)
        payload: dict = {"email": email, "role": role}
        if external_id is not None:
            payload["external_id"] = external_id
        if display_name is not None:
            payload["display_name"] = display_name
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
        return User.model_validate(response.json())

    def list(
        self,
        *,
        org_id: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[User]:
        """List all users in the caller's organization.

        Args:
            org_id: Override organization UUID (SUPER_ADMIN only).
            offset: Number of items to skip (server-side pagination).
            limit: Maximum number of items to return.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            List of User objects.
        """
        endpoint = ENDPOINT_USERS.format(base_url=self.base_url)
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
        return [User.model_validate(item) for item in response.json()]

    def me(
        self,
        *,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> User:
        """Get the current authenticated user.

        Args:
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The current User.
        """
        endpoint = ENDPOINT_USERS_ME.format(base_url=self.base_url)

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
        return User.model_validate(response.json())

    def get(
        self,
        *,
        user_id: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> User:
        """Get a user by ID.

        Args:
            user_id: User UUID.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The requested User.
        """
        endpoint = ENDPOINT_USER_BY_ID.format(
            base_url=self.base_url,
            user_id=user_id,
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
        return User.model_validate(response.json())

    def update(
        self,
        *,
        user_id: str,
        display_name: str | None = None,
        status: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> User:
        """Update a user.

        Args:
            user_id: User UUID.
            display_name: New display name.
            status: New status (``active``, ``inactive``, or ``deleted``).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The updated User.
        """
        endpoint = ENDPOINT_USER_BY_ID.format(
            base_url=self.base_url,
            user_id=user_id,
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
        return User.model_validate(response.json())

    def delete(
        self,
        *,
        user_id: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """Delete a user.

        Args:
            user_id: User UUID.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.
        """
        endpoint = ENDPOINT_USER_BY_ID.format(
            base_url=self.base_url,
            user_id=user_id,
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


class AsyncUsersClient:
    """Asynchronous client for user operations."""

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
        email: str,
        external_id: str | None = None,
        display_name: str | None = None,
        org_id: str | None = None,
        role: str = "ORG_MEMBER",
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> User:
        """Create a new user (SUPER_ADMIN or ORG_ADMIN only).

        Args:
            email: User email address.
            external_id: External IdP identifier (e.g. Azure AD oid).
            display_name: Optional human-friendly display name.
            org_id: Target organization UUID (SUPER_ADMIN can specify any,
                ORG_ADMIN uses their own).
            role: RBAC role to assign (default ``ORG_MEMBER``).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The newly created User.
        """
        endpoint = ENDPOINT_USERS.format(base_url=self.base_url)
        payload: dict = {"email": email, "role": role}
        if external_id is not None:
            payload["external_id"] = external_id
        if display_name is not None:
            payload["display_name"] = display_name
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
                if resp.content_type == "application/json":
                    return User.model_validate(await resp.json())
                else:
                    return User.model_validate(json.loads(await resp.text()))

    async def list(
        self,
        *,
        org_id: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> list[User]:
        """List all users in the caller's organization.

        Args:
            org_id: Override organization UUID (SUPER_ADMIN only).
            offset: Number of items to skip (server-side pagination).
            limit: Maximum number of items to return.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            List of User objects.
        """
        endpoint = ENDPOINT_USERS.format(base_url=self.base_url)
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
                return [User.model_validate(item) for item in await resp.json()]

    async def me(
        self,
        *,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> User:
        """Get the current authenticated user.

        Args:
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The current User.
        """
        endpoint = ENDPOINT_USERS_ME.format(base_url=self.base_url)

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
                return User.model_validate(await resp.json())

    async def get(
        self,
        *,
        user_id: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> User:
        """Get a user by ID.

        Args:
            user_id: User UUID.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The requested User.
        """
        endpoint = ENDPOINT_USER_BY_ID.format(
            base_url=self.base_url,
            user_id=user_id,
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
                return User.model_validate(await resp.json())

    async def update(
        self,
        *,
        user_id: str,
        display_name: str | None = None,
        status: str | None = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> User:
        """Update a user.

        Args:
            user_id: User UUID.
            display_name: New display name.
            status: New status (``active``, ``inactive``, or ``deleted``).
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.

        Returns:
            The updated User.
        """
        endpoint = ENDPOINT_USER_BY_ID.format(
            base_url=self.base_url,
            user_id=user_id,
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
                return User.model_validate(await resp.json())

    async def delete(
        self,
        *,
        user_id: str,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """Delete a user.

        Args:
            user_id: User UUID.
            timeout: Request timeout in seconds (default 60).
            extra_headers: Per-request header overrides.
        """
        endpoint = ENDPOINT_USER_BY_ID.format(
            base_url=self.base_url,
            user_id=user_id,
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
