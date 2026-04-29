"""
Module providing clients for PaddleX document analysis endpoints.
Supports layout detection, text detection, and OCR.

This module includes:
  - `DocumentAnalysisClient` for synchronous calls.
  - `AsyncDocumentAnalysisClient` for asynchronous calls.

Example usage:

    from air.document_analysis import DocumentAnalysisClient, AsyncDocumentAnalysisClient

    # Synchronous OCR
    sync_client = DocumentAnalysisClient(
        base_url="https://api.airefinery.accenture.com",
        api_key="...",
    )
    response = sync_client.ocr(
        model="paddlex/PP-OCRv5_server",
        image_path="/path/to/image.png",
        language="en",
    )

    # Async layout detection
    async_client = AsyncDocumentAnalysisClient(
        base_url="https://api.airefinery.accenture.com",
        api_key="...",
    )
    response = await async_client.layout_detection(
        model="paddlex/RT-DETR-H_layout_17cls",
        image_base64="...",
    )
"""

import base64
from typing import Literal

import aiohttp
import requests
from pydantic import BaseModel, Field

from air import BASE_URL, __version__
from air.auth.token_provider import TokenProvider
from air.utils import get_base_headers, get_base_headers_async

# Endpoints - route through main AIRefinery API
ENDPOINT_LAYOUT = "{base_url}/v1/document-analysis/layout-detection"
ENDPOINT_TEXT_DET = "{base_url}/v1/document-analysis/text-detection"
ENDPOINT_OCR = "{base_url}/v1/document-analysis/ocr"


# Response models
class LayoutElement(BaseModel):
    """A detected layout element (table, figure, text block, etc.)."""

    label: str = Field(..., description="Element type (table, figure, text, etc.)")
    score: float = Field(..., description="Detection confidence score")
    bbox: list[float] = Field(..., description="Bounding box [x1, y1, x2, y2]")


class TextRegion(BaseModel):
    """A detected text region."""

    bbox: list[list[float]] = Field(
        ..., description="Quadrilateral bounding box coordinates"
    )
    score: float = Field(..., description="Detection confidence score")


class OCRResult(BaseModel):
    """OCR result with text and location."""

    text: str = Field(..., description="Recognized text")
    score: float = Field(..., description="Recognition confidence score")
    bbox: list[list[float]] = Field(
        ..., description="Quadrilateral bounding box coordinates"
    )


class LayoutDetectionResponse(BaseModel):
    """Response from layout detection endpoint."""

    elements: list[LayoutElement] = Field(
        default_factory=list, description="Detected layout elements"
    )
    inference_time_ms: float = Field(
        default=0, description="Inference time in milliseconds"
    )


class TextDetectionResponse(BaseModel):
    """Response from text detection endpoint."""

    regions: list[TextRegion] = Field(
        default_factory=list, description="Detected text regions"
    )
    inference_time_ms: float = Field(
        default=0, description="Inference time in milliseconds"
    )


class OCRResponse(BaseModel):
    """Response from OCR endpoint."""

    results: list[OCRResult] = Field(
        default_factory=list, description="OCR results with text and location"
    )
    inference_time_ms: float = Field(
        default=0, description="Inference time in milliseconds"
    )


def _load_image_base64(image_path: str | None, image_base64: str | None) -> str:
    """Load image as base64 from path or validate base64 input."""
    if image_path is not None:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    elif image_base64 is not None:
        return image_base64
    else:
        raise ValueError("Either image_path or image_base64 must be provided")


def _parse_layout_response(data: dict) -> LayoutDetectionResponse:
    """Parse layout detection API response."""
    elements = []
    for elem in data.get("boxes", []):
        # Server returns: x1, y1, x2, y2, confidence, label
        elements.append(
            LayoutElement(
                label=elem.get("label", ""),
                score=elem.get("confidence", 0.0),
                bbox=[
                    elem.get("x1", 0),
                    elem.get("y1", 0),
                    elem.get("x2", 0),
                    elem.get("y2", 0),
                ],
            )
        )
    return LayoutDetectionResponse(
        elements=elements,
        inference_time_ms=data.get("inference_time_ms", 0),
    )


def _parse_text_det_response(data: dict) -> TextDetectionResponse:
    """Parse text detection API response."""
    regions = []
    # Server returns boxes as list of polygons (4 points each)
    for box in data.get("boxes", []):
        regions.append(
            TextRegion(
                bbox=box,  # Already in polygon format
                score=1.0,  # Server doesn't return scores for text detection
            )
        )
    return TextDetectionResponse(
        regions=regions,
        inference_time_ms=data.get("inference_time_ms", 0),
    )


def _parse_ocr_response(data: dict) -> OCRResponse:
    """Parse OCR API response."""
    results = []
    for result in data.get("results", []):
        results.append(
            OCRResult(
                text=result.get("text", ""),
                score=result.get("confidence", 0.0),  # Server uses 'confidence'
                bbox=result.get("box", []),  # Server uses 'box' not 'bbox'
            )
        )
    return OCRResponse(
        results=results,
        inference_time_ms=data.get("inference_time_ms", 0),
    )


class DocumentAnalysisClient:
    """
    A synchronous client for PaddleX document analysis endpoints.

    Supports layout detection, text detection, and OCR.
    """

    def __init__(
        self,
        api_key: str | TokenProvider,
        *,
        base_url: str = BASE_URL,
        default_headers: dict[str, str] | None = None,
    ):
        """
        Initialize the synchronous document analysis client.

        Args:
            api_key: API key or TokenProvider for authentication.
            base_url: Base URL of the API.
            default_headers: Headers applied to every request.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.default_headers = default_headers or {}

    def layout_detection(
        self,
        *,
        model: str = "paddlex/RT-DETR-H_layout_17cls",
        image_path: str | None = None,
        image_base64: str | None = None,
        threshold: float = 0.5,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> LayoutDetectionResponse:
        """
        Detect layout elements in a document image.

        Args:
            model: Model name (e.g., "paddlex/RT-DETR-H_layout_17cls").
            image_path: Path to image file (mutually exclusive with image_base64).
            image_base64: Base64-encoded image data.
            threshold: Detection confidence threshold (0-1).
            timeout: Request timeout in seconds.
            extra_headers: Request-specific headers.

        Returns:
            LayoutDetectionResponse with detected elements.
        """
        endpoint = ENDPOINT_LAYOUT.format(base_url=self.base_url)
        image_data = _load_image_base64(image_path, image_base64)

        payload = {"image": image_data, "threshold": threshold}
        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=timeout if timeout else 60,
        )
        response.raise_for_status()
        return _parse_layout_response(response.json())

    def text_detection(
        self,
        *,
        model: str = "paddlex/PP-OCRv4_server_det",
        image_path: str | None = None,
        image_base64: str | None = None,
        threshold: float = 0.3,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> TextDetectionResponse:
        """
        Detect text regions in a document image.

        Args:
            model: Model name (e.g., "paddlex/PP-OCRv4_server_det").
            image_path: Path to image file (mutually exclusive with image_base64).
            image_base64: Base64-encoded image data.
            threshold: Detection confidence threshold (0-1).
            timeout: Request timeout in seconds.
            extra_headers: Request-specific headers.

        Returns:
            TextDetectionResponse with detected text regions.
        """
        endpoint = ENDPOINT_TEXT_DET.format(base_url=self.base_url)
        image_data = _load_image_base64(image_path, image_base64)

        payload = {"image": image_data, "threshold": threshold}
        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=timeout if timeout else 60,
        )
        response.raise_for_status()
        return _parse_text_det_response(response.json())

    def ocr(
        self,
        *,
        model: str = "paddlex/PP-OCRv5_server",
        image_path: str | None = None,
        image_base64: str | None = None,
        threshold: float = 0.3,
        language: str = "en",
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> OCRResponse:
        """
        Perform OCR (text detection + recognition) on a document image.

        Args:
            model: Model name (e.g., "paddlex/PP-OCRv5_server").
            image_path: Path to image file (mutually exclusive with image_base64).
            image_base64: Base64-encoded image data.
            threshold: Detection confidence threshold (0-1).
            language: OCR language (en, ch, japan, korean, latin, arabic, etc.).
            timeout: Request timeout in seconds.
            extra_headers: Request-specific headers.

        Returns:
            OCRResponse with recognized text and locations.
        """
        endpoint = ENDPOINT_OCR.format(base_url=self.base_url)
        image_data = _load_image_base64(image_path, image_base64)

        payload = {
            "image": image_data,
            "threshold": threshold,
            "language": language,
        }
        headers = get_base_headers(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=timeout if timeout else 60,
        )
        response.raise_for_status()
        return _parse_ocr_response(response.json())


class AsyncDocumentAnalysisClient:
    """
    An asynchronous client for PaddleX document analysis endpoints.

    Supports layout detection, text detection, and OCR.
    """

    def __init__(
        self,
        api_key: str | TokenProvider,
        *,
        base_url: str = BASE_URL,
        default_headers: dict[str, str] | None = None,
    ):
        """
        Initialize the asynchronous document analysis client.

        Args:
            api_key: API key or TokenProvider for authentication.
            base_url: Base URL of the API.
            default_headers: Headers applied to every request.
        """
        self.base_url = base_url
        self.api_key = api_key
        self.default_headers = default_headers or {}

    async def layout_detection(
        self,
        *,
        model: str = "paddlex/RT-DETR-H_layout_17cls",
        image_path: str | None = None,
        image_base64: str | None = None,
        threshold: float = 0.5,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> LayoutDetectionResponse:
        """
        Detect layout elements in a document image asynchronously.

        Args:
            model: Model name (e.g., "paddlex/RT-DETR-H_layout_17cls").
            image_path: Path to image file (mutually exclusive with image_base64).
            image_base64: Base64-encoded image data.
            threshold: Detection confidence threshold (0-1).
            timeout: Request timeout in seconds.
            extra_headers: Request-specific headers.

        Returns:
            LayoutDetectionResponse with detected elements.
        """
        endpoint = ENDPOINT_LAYOUT.format(base_url=self.base_url)
        image_data = _load_image_base64(image_path, image_base64)

        payload = {"image": image_data, "threshold": threshold}
        headers = await get_base_headers_async(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        client_timeout = aiohttp.ClientTimeout(total=timeout if timeout else 60)
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.post(endpoint, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return _parse_layout_response(data)

    async def text_detection(
        self,
        *,
        model: str = "paddlex/PP-OCRv4_server_det",
        image_path: str | None = None,
        image_base64: str | None = None,
        threshold: float = 0.3,
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> TextDetectionResponse:
        """
        Detect text regions in a document image asynchronously.

        Args:
            model: Model name (e.g., "paddlex/PP-OCRv4_server_det").
            image_path: Path to image file (mutually exclusive with image_base64).
            image_base64: Base64-encoded image data.
            threshold: Detection confidence threshold (0-1).
            timeout: Request timeout in seconds.
            extra_headers: Request-specific headers.

        Returns:
            TextDetectionResponse with detected text regions.
        """
        endpoint = ENDPOINT_TEXT_DET.format(base_url=self.base_url)
        image_data = _load_image_base64(image_path, image_base64)

        payload = {"image": image_data, "threshold": threshold}
        headers = await get_base_headers_async(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        client_timeout = aiohttp.ClientTimeout(total=timeout if timeout else 60)
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.post(endpoint, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return _parse_text_det_response(data)

    async def ocr(
        self,
        *,
        model: str = "paddlex/PP-OCRv5_server",
        image_path: str | None = None,
        image_base64: str | None = None,
        threshold: float = 0.3,
        language: str = "en",
        timeout: float | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> OCRResponse:
        """
        Perform OCR (text detection + recognition) on a document image asynchronously.

        Args:
            model: Model name (e.g., "paddlex/PP-OCRv5_server").
            image_path: Path to image file (mutually exclusive with image_base64).
            image_base64: Base64-encoded image data.
            threshold: Detection confidence threshold (0-1).
            language: OCR language (en, ch, japan, korean, latin, arabic, etc.).
            timeout: Request timeout in seconds.
            extra_headers: Request-specific headers.

        Returns:
            OCRResponse with recognized text and locations.
        """
        endpoint = ENDPOINT_OCR.format(base_url=self.base_url)
        image_data = _load_image_base64(image_path, image_base64)

        payload = {
            "image": image_data,
            "threshold": threshold,
            "language": language,
        }
        headers = await get_base_headers_async(self.api_key)
        headers.update(self.default_headers)
        if extra_headers:
            headers.update(extra_headers)

        client_timeout = aiohttp.ClientTimeout(total=timeout if timeout else 60)
        async with aiohttp.ClientSession(timeout=client_timeout) as session:
            async with session.post(endpoint, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return _parse_ocr_response(data)
