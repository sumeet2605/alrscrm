from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock


@dataclass
class MetricsRegistry:
    _lock: Lock = field(default_factory=Lock)
    api_request_count: int = 0
    api_error_count: int = 0
    api_latency_total_ms: float = 0
    database_latency_ms: float | None = None
    storage_latency_ms: float | None = None
    invoice_creation_count: int = 0
    payment_creation_count: int = 0
    gallery_access_count: int = 0
    delivery_count: int = 0

    def record_api_request(
        self, route: str, method: str, status_code: int, duration_ms: float
    ) -> None:
        with self._lock:
            self.api_request_count += 1
            self.api_latency_total_ms += duration_ms
            if status_code >= 500:
                self.api_error_count += 1
            if method == "POST" and status_code < 400:
                if route == "/api/v1/invoices":
                    self.invoice_creation_count += 1
                elif route == "/api/v1/payments":
                    self.payment_creation_count += 1
                elif route.startswith("/api/v1/delivery"):
                    self.delivery_count += 1
            if route.startswith("/api/v1/galleries/client") and status_code < 400:
                self.gallery_access_count += 1

    def record_database_latency(self, duration_ms: float) -> None:
        with self._lock:
            self.database_latency_ms = duration_ms

    def record_storage_latency(self, duration_ms: float) -> None:
        with self._lock:
            self.storage_latency_ms = duration_ms

    def snapshot(self) -> dict[str, int | float | None]:
        with self._lock:
            average_latency = (
                round(self.api_latency_total_ms / self.api_request_count, 2)
                if self.api_request_count
                else 0
            )
            error_rate = (
                round(self.api_error_count / self.api_request_count, 4)
                if self.api_request_count
                else 0
            )
            return {
                "api_request_count": self.api_request_count,
                "api_error_count": self.api_error_count,
                "api_error_rate": error_rate,
                "api_average_latency_ms": average_latency,
                "database_latency_ms": self.database_latency_ms,
                "storage_latency_ms": self.storage_latency_ms,
                "invoice_creation_count": self.invoice_creation_count,
                "payment_creation_count": self.payment_creation_count,
                "gallery_access_count": self.gallery_access_count,
                "delivery_count": self.delivery_count,
            }

    def reset(self) -> None:
        with self._lock:
            self.api_request_count = 0
            self.api_error_count = 0
            self.api_latency_total_ms = 0
            self.database_latency_ms = None
            self.storage_latency_ms = None
            self.invoice_creation_count = 0
            self.payment_creation_count = 0
            self.gallery_access_count = 0
            self.delivery_count = 0


metrics_registry = MetricsRegistry()
