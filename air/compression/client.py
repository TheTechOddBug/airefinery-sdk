"""
Module providing clients for prompt compression operations.
All responses are validated using Pydantic models.

This module includes:
  - `CompressionClient` for synchronous calls.
  - `AsyncCompressionClient` for asynchronous calls.

Both clients call the `/compress` endpoint.
All responses are validated using Pydantic models (`CompressionResponse`).
"""

from typing import List, Optional, Union

import aiohttp
import requests

from air import BASE_URL
from air.auth.token_provider import TokenProvider
from air.types.compression import CompressedPrompt, CompressionResponse
from air.types.constants import DEFAULT_TIMEOUT
from air.utils import get_base_headers, get_base_headers_async

ENDPOINT_COMPRESS = "{base_url}/v1/compress"


class CompressionClient:
    """
    A synchronous client for the prompt compression endpoint.

    This class handles sending requests to the compression endpoint
    and converts the responses into Pydantic models for type safety.
    """

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

    def compress(
        self,
        *,
        context: Union[str, List[str]],
        model: str,
        rate: float = 0.5,
        target_token: int = -1,
        instruction: Optional[str] = None,
        question: Optional[str] = None,
        force_tokens: Optional[List[str]] = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
        **kwargs,
    ) -> CompressionResponse:
        """
        Compresses a prompt synchronously.

        Args:
            context (str | List[str]): Text or list of texts to compress
            model (str): The compression model name
            rate (float): Target compression rate (0.0 to 1.0). Default 0.5
            target_token (int): Explicit target token count (-1 for rate-based). Default -1
            instruction (str | None): Optional instruction for compression context
            question (str | None): Optional question for compression context
            force_tokens (List[str] | None): Tokens to preserve in compressed output
            timeout (float | None): Max time (in seconds) to wait for a response
            extra_headers (dict[str, str] | None): Request-specific headers
            **kwargs: Additional compression parameters

        Returns:
            CompressionResponse: The parsed response containing compressed prompts
        """
        effective_timeout = timeout if timeout is not None else DEFAULT_TIMEOUT

        endpoint = ENDPOINT_COMPRESS.format(base_url=self.base_url)

        payload: dict = {
            "model": model,
            "context": context,
            "rate": rate,
            "target_token": target_token,
            **kwargs,
        }
        if instruction is not None:
            payload["instruction"] = instruction
        if question is not None:
            payload["question"] = question
        if force_tokens is not None:
            payload["force_tokens"] = force_tokens

        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.post(
            endpoint, json=payload, headers=headers, timeout=effective_timeout
        )
        response.raise_for_status()

        results = response.json()
        # Platform returns a single object; raw server returns a list
        if isinstance(results, dict):
            results = [results]
        return CompressionResponse(
            data=[CompressedPrompt.model_validate(r) for r in results]
        )


class AsyncCompressionClient:
    """
    An asynchronous client for the prompt compression endpoint.

    This class handles sending requests to the compression endpoint
    and converts the responses into Pydantic models for type safety.
    """

    def __init__(
        self,
        api_key: str | TokenProvider,
        *,
        base_url: str,
        default_headers: dict[str, str] | None = None,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.default_headers = default_headers or {}

    async def compress(
        self,
        *,
        context: Union[str, List[str]],
        model: str,
        rate: float = 0.5,
        target_token: int = -1,
        instruction: Optional[str] = None,
        question: Optional[str] = None,
        force_tokens: Optional[List[str]] = None,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
        **kwargs,
    ) -> CompressionResponse:
        """
        Compresses a prompt asynchronously.

        Args:
            context (str | List[str]): Text or list of texts to compress
            model (str): The compression model name
            rate (float): Target compression rate (0.0 to 1.0). Default 0.5
            target_token (int): Explicit target token count (-1 for rate-based). Default -1
            instruction (str | None): Optional instruction for compression context
            question (str | None): Optional question for compression context
            force_tokens (List[str] | None): Tokens to preserve in compressed output
            timeout (float | None): Max time (in seconds) to wait for a response
            extra_headers (dict[str, str] | None): Request-specific headers
            **kwargs: Additional compression parameters

        Returns:
            CompressionResponse: The parsed response containing compressed prompts
        """
        effective_timeout = DEFAULT_TIMEOUT if timeout is None else timeout

        endpoint = ENDPOINT_COMPRESS.format(base_url=self.base_url)

        payload: dict = {
            "model": model,
            "context": context,
            "rate": rate,
            "target_token": target_token,
            **kwargs,
        }
        if instruction is not None:
            payload["instruction"] = instruction
        if question is not None:
            payload["question"] = question
        if force_tokens is not None:
            payload["force_tokens"] = force_tokens

        headers = await get_base_headers_async(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        client_timeout = aiohttp.ClientTimeout(total=effective_timeout)
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.post(endpoint, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                results = await resp.json()

                # Platform returns a single object; raw server returns a list
                if isinstance(results, dict):
                    results = [results]
                return CompressionResponse(
                    data=[CompressedPrompt.model_validate(r) for r in results]
                )
