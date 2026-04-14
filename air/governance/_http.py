"""Shared HTTP helpers for governance sub-clients."""

from __future__ import annotations

import json
import logging
from typing import Any

import aiohttp
import requests
from air.governance.exceptions import (
    DuplicateResourceError,
    GovernanceError,
    PermissionDeniedError,
    ResourceNotFoundError,
    UnprocessableContentError,
)

logger = logging.getLogger(__name__)

_STATUS_MAP: dict[int, type[GovernanceError]] = {
    400: DuplicateResourceError,
    403: PermissionDeniedError,
    404: ResourceNotFoundError,
    422: UnprocessableContentError,
}


def _parse_error_body(body: str) -> dict[str, Any]:
    try:
        return json.loads(body)
    except (json.JSONDecodeError, TypeError):
        return {"error": body}


def raise_for_status_sync(response: requests.Response) -> None:
    """Raise the appropriate GovernanceError subclass for non-2xx responses."""
    if response.ok:
        return
    body = _parse_error_body(response.text)
    message = body.get("error", response.reason or "Unknown error")
    exc_cls = _STATUS_MAP.get(response.status_code, GovernanceError)
    raise exc_cls(
        str(message),
        status_code=response.status_code,
        response_body=body,
    )


async def raise_for_status_async(response: aiohttp.ClientResponse) -> None:
    """Raise the appropriate GovernanceError subclass for non-2xx responses."""
    if response.ok:
        return
    text = await response.text()
    body = _parse_error_body(text)
    message = body.get("error", response.reason or "Unknown error")
    exc_cls = _STATUS_MAP.get(response.status, GovernanceError)
    raise exc_cls(
        str(message),
        status_code=response.status,
        response_body=body,
    )
