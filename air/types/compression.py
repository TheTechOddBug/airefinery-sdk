"""
Pydantic models for the prompt compression response.

Provides:

- CompressedPrompt: a single compression result
- CompressionResponse: the top-level container for a compression.compress call

"""

from typing import List

from air.types.base import CustomBaseModel


class CompressedPrompt(CustomBaseModel):
    """Represents a single compressed prompt result.

    Attributes:
        compressed_prompt: The compressed version of the input text
        origin_tokens: Number of tokens in the original input
        compressed_tokens: Number of tokens in the compressed output
    """

    compressed_prompt: str
    origin_tokens: int
    compressed_tokens: int


class CompressionResponse(CustomBaseModel):
    """Represents the full response returned by the compression endpoint.

    Attributes:
        data: A list of compressed prompt results, one per input context
    """

    data: List[CompressedPrompt]
