"""Pydantic models for governance Organization responses."""

from datetime import datetime
from typing import Optional

from air.types.base import CustomBaseModel


class Organization(CustomBaseModel):
    """Represents an organization in the governance layer.

    Attributes:
        id: Organization UUID.
        name: Unique organization name.
        display_name: Human-friendly display name.
        status: Current status (``active``, ``suspended``, or ``deleted``).
        created_at: Timestamp when the organization was created.
        updated_at: Timestamp of the last update.
    """

    id: str
    name: str
    display_name: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
