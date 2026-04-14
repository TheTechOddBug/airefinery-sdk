"""Pydantic models for governance Project responses."""

from datetime import datetime
from typing import Optional

from air.types.base import CustomBaseModel


class Project(CustomBaseModel):
    """Represents a project within a workspace.

    Attributes:
        id: Project UUID.
        workspace_id: Parent workspace UUID.
        org_id: Parent organization UUID.
        name: Project name (unique within the workspace).
        description: Optional project description.
        created_by: UUID of the user who created the project.
        status: Current status (``active``, ``archived``, or ``deleted``).
        created_at: Timestamp when the project was created.
        updated_at: Timestamp of the last update.
    """

    id: str
    workspace_id: str
    org_id: str
    name: str
    description: Optional[str] = None
    created_by: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
