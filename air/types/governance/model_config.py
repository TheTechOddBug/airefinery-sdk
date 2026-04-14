"""Pydantic models for Governance models configuration inputs."""

from typing import Optional

from pydantic import BaseModel, Field


class LLMClientRequest(BaseModel):
    """Default request parameters embedded in LLMClientConfig."""

    model: str = Field(
        ..., description="Actual model name for requests (endpoint model)."
    )
    temperature: Optional[float] = Field(
        default=0.5, description="Sampling temperature."
    )
    top_p: Optional[float] = Field(default=1.0, description="Top-p (nucleus) sampling.")
    max_tokens: Optional[int] = Field(
        default=None,
        description="Default maximum tokens to generate (None = API default).",
    )
    cost: Optional[float] = Field(default=0, description="Cost per 1k tokens.")


class LLMClientConfig(BaseModel):
    """User-supplied configuration for one logical LLM model."""

    api_type: str = Field(..., description="Type of API: 'openai' or 'azureopenai'.")
    base_url: str = Field(..., description="Base URL for the LLM API endpoint.")
    api_key: str = Field(..., description="API key for authentication.")
    api_version: Optional[str] = Field(
        default="2023-05-15", description="Azure-only; ignored for OpenAI."
    )
    request: LLMClientRequest = Field(..., description="Default request parameters.")


class EmbeddingClientRequest(BaseModel):
    """Default request parameters for the EmbeddingClient."""

    model: str = Field(
        ...,
        description="Actual model name for requests (to the Embedding endpoint).",
    )


class EmbeddingClientConfig(BaseModel):
    """
    Configuration for a single-embedding client.

    - model: The actual model name for the request (e.g., "text-embedding-ada-002").
    - model_key: A client-facing name, used to override the .model field in the returned response.
    """

    api_type: str = Field(..., description="Type of API: 'openai' or 'azureopenai'.")
    base_url: str = Field(..., description="Base URL for the embedding API endpoint.")
    api_key: str = Field(..., description="API key for authentication.")

    api_version: str = Field(
        default="2023-05-15",
        description="API version if using Azure (ignored for plain OpenAI).",
    )

    request: EmbeddingClientRequest = Field(
        ...,
        description="Default Request parameters for Embedding Client.",
    )


CLIENT_CONFIG_REGISTRY = {"llm": LLMClientConfig, "embedding": EmbeddingClientConfig}
