"""Pydantic models for governance Model responses."""

from typing import Any, Dict, Literal, Optional

from air.types.base import CustomBaseModel


class Model(CustomBaseModel):
    """Represents a private model in the registry."""

    model_name: str
    model_type: Literal["llm", "embedding"]
    config: Optional[Dict[str, Any]] = None
    status: bool = True
    description: Optional[str] = None
