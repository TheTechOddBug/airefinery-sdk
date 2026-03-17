from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple, Union

# Nanoseconds per second for Loki timestamp conversion
_NS_PER_SECOND = 1_000_000_000


class ObservabilityResponse:
    """Base wrapper for observability HTTP responses.

    Provides dict-like access for backward compatibility. You can use
    subscript notation (response["key"]) or the helper methods.

    Args:
        http_response_or_json: Either an httpx Response object or a dict.
            When a dict is passed, it is used directly as the JSON payload
            (useful for testing).
    """

    def __init__(self, http_response_or_json: Union[Any, Dict[str, Any]]):
        if isinstance(http_response_or_json, dict):
            self._resp = None
            self._json: Optional[Dict[str, Any]] = http_response_or_json
        else:
            self._resp = http_response_or_json
            self._json = None

    def json(self) -> Dict[str, Any]:
        """Return cached JSON payload from the HTTP response."""
        cached = self._json
        if cached is not None:
            return cached
        # _resp is guaranteed to be set when _json is None (see __init__)
        assert self._resp is not None
        result: Dict[str, Any] = self._resp.json()
        self._json = result
        return result

    # ------------------------------------------------------------------ #
    # Dict-like interface for backward compatibility                     #
    # ------------------------------------------------------------------ #

    def __getitem__(self, key: str) -> Any:
        """Allow dict-style access: response['key']."""
        return self.json()[key]

    def __contains__(self, key: object) -> bool:
        """Allow 'in' checks: 'key' in response."""
        return key in self.json()

    def __iter__(self) -> Iterator[str]:
        """Allow iteration over keys."""
        return iter(self.json())

    def keys(self) -> Any:
        """Return dict keys."""
        return self.json().keys()

    def values(self) -> Any:
        """Return dict values."""
        return self.json().values()

    def items(self) -> Any:
        """Return dict items."""
        return self.json().items()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value with optional default."""
        return self.json().get(key, default)

    def __repr__(self) -> str:
        """Return a readable representation."""
        cls_name = self.__class__.__name__
        try:
            keys = list(self.json().keys())
            return f"<{cls_name} keys={keys}>"
        except Exception:
            return f"<{cls_name}>"


@dataclass(frozen=True)
class MetricSample:
    """Single metric sample with labels and value."""

    metric: Dict[str, Any]
    value: List[Any]

    @property
    def timestamp(self) -> Optional[float]:
        """Return the sample timestamp as float, if present."""
        if not self.value:
            return None
        try:
            return float(self.value[0])
        except (TypeError, ValueError):
            return None

    @property
    def value_str(self) -> Optional[str]:
        """Return the sample value as a string, if present."""
        if len(self.value) < 2:
            return None
        return str(self.value[1])


class MetricsResponse(ObservabilityResponse):
    """Helper for standard metrics JSON responses (Prometheus-style)."""

    def status(self) -> Optional[str]:
        """Return response status if provided."""
        return self.json().get("status")

    def query(self) -> Optional[str]:
        """Return the original query string if provided."""
        return self.json().get("query")

    def data(self) -> Dict[str, Any]:
        """Return the nested data object."""
        return self.json().get("data", {})

    def result_type(self) -> Optional[str]:
        """Return the result type string if provided."""
        return self.data().get("resultType")

    def analysis(self) -> Dict[str, Any]:
        """Return the analysis object if provided."""
        return self.data().get("analysis", {})

    def result(self) -> List[Dict[str, Any]]:
        """Return the raw result list."""
        return self.data().get("result", [])

    def samples(self) -> List[MetricSample]:
        """Return parsed metric samples."""
        return [
            MetricSample(metric=item.get("metric", {}), value=item.get("value", []))
            for item in self.result()
        ]

    def metric_labels(self) -> List[Dict[str, Any]]:
        """Return the metric label dicts for each sample."""
        return [sample.metric for sample in self.samples()]

    def sample_values(self) -> List[List[Any]]:
        """Return the raw value lists for each sample."""
        return [sample.value for sample in self.samples()]

    def iter_pairs(self) -> Iterable[Tuple[Dict[str, Any], List[Any]]]:
        """Iterate over (metric_labels, value) pairs."""
        for sample in self.samples():
            yield sample.metric, sample.value


@dataclass(frozen=True)
class LogStreamSample:
    """Single log stream with labels and values."""

    stream: Dict[str, Any]
    values: List[List[Any]]

    @staticmethod
    def _parse_timestamp(raw: Any) -> Optional[float]:
        """Parse a raw timestamp value to float (nanoseconds)."""
        if raw is None:
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def timestamp_to_seconds(ts_ns: Optional[float]) -> Optional[float]:
        """Convert a nanosecond timestamp to seconds.

        Args:
            ts_ns: Timestamp in nanoseconds (as returned by Loki).

        Returns:
            Timestamp in seconds (Unix epoch), or None if input is None.
        """
        if ts_ns is None:
            return None
        return ts_ns / _NS_PER_SECOND

    def iter_messages(self) -> Iterable[Tuple[Optional[float], Optional[str]]]:
        """Iterate over (timestamp_ns, message) tuples in the stream.

        Note: Timestamps are in nanoseconds as returned by Loki.
        Use iter_messages_seconds() for timestamps in seconds.
        """
        for item in self.values:
            if not item:
                yield None, None
                continue
            ts = self._parse_timestamp(item[0]) if len(item) >= 1 else None
            msg = str(item[1]) if len(item) >= 2 else None
            yield ts, msg

    def iter_messages_seconds(self) -> Iterable[Tuple[Optional[float], Optional[str]]]:
        """Iterate over (timestamp_seconds, message) tuples in the stream.

        Timestamps are converted from Loki nanoseconds to Unix seconds.
        """
        for ts_ns, msg in self.iter_messages():
            yield self.timestamp_to_seconds(ts_ns), msg


class LogsResponse(ObservabilityResponse):
    """Helper for standard logs JSON responses (Loki-style)."""

    def status(self) -> Optional[str]:
        """Return response status if provided."""
        return self.json().get("status")

    def data(self) -> Dict[str, Any]:
        """Return the nested data object."""
        return self.json().get("data", {})

    def result_type(self) -> Optional[str]:
        """Return the result type string if provided."""
        return self.data().get("resultType")

    def result(self) -> List[Dict[str, Any]]:
        """Return the raw result list."""
        return self.data().get("result", [])

    def samples(self) -> List[LogStreamSample]:
        """Return parsed log stream samples."""
        return [
            LogStreamSample(
                stream=item.get("stream", {}),
                values=item.get("values", []),
            )
            for item in self.result()
        ]

    def streams(self) -> List[Dict[str, Any]]:
        """Return stream label dicts for each sample."""
        return [sample.stream for sample in self.samples()]

    def stream_values(self) -> List[List[List[Any]]]:
        """Return value lists for each stream sample."""
        return [sample.values for sample in self.samples()]

    def iter_pairs(self) -> Iterable[Tuple[Dict[str, Any], List[List[Any]]]]:
        """Iterate over (stream_labels, values) pairs."""
        for sample in self.samples():
            yield sample.stream, sample.values


@dataclass(frozen=True)
class TraceBatch:
    """Single trace batch with resource and scope spans."""

    resource: Dict[str, Any]
    scope_spans: List[Dict[str, Any]]

    def iter_spans(self) -> Iterable[Dict[str, Any]]:
        """Iterate over spans for all scopes in the batch."""
        for scope in self.scope_spans:
            for span in scope.get("spans", []) or []:
                yield span


class TracesResponse(ObservabilityResponse):
    """Helper for standard traces JSON responses (OTLP-style)."""

    def traces(self) -> List[Dict[str, Any]]:
        """Return the raw traces list."""
        return self.json().get("traces", [])

    def batches(self) -> List[Dict[str, Any]]:
        """Return flattened batch list across traces."""
        batches: List[Dict[str, Any]] = []
        for trace in self.traces():
            batches.extend(trace.get("batches", []) or [])
        return batches

    def trace_batches(self) -> List[TraceBatch]:
        """Return parsed trace batches."""
        return [
            TraceBatch(
                resource=item.get("resource", {}),
                scope_spans=item.get("scopeSpans", []),
            )
            for item in self.batches()
        ]

    def scope_spans(self) -> List[Dict[str, Any]]:
        """Return flattened scope span lists across batches."""
        scopes: List[Dict[str, Any]] = []
        for batch in self.trace_batches():
            scopes.extend(batch.scope_spans or [])
        return scopes

    def spans(self) -> List[Dict[str, Any]]:
        """Return flattened spans across all scopes."""
        spans: List[Dict[str, Any]] = []
        for scope in self.scope_spans():
            spans.extend(scope.get("spans", []) or [])
        return spans

    def iter_spans(self) -> Iterable[Dict[str, Any]]:
        """Iterate over all spans across batches."""
        for batch in self.trace_batches():
            yield from batch.iter_spans()
