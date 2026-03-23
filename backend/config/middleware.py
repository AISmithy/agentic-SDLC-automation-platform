"""Custom middleware for the platform."""

import uuid
import threading

_correlation_id = threading.local()


def get_correlation_id() -> str:
    return getattr(_correlation_id, "value", "")


class CorrelationIDMiddleware:
    """Attach a correlation ID to every request for observability."""

    HEADER = "X-Correlation-ID"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        correlation_id = request.headers.get(self.HEADER) or str(uuid.uuid4())
        _correlation_id.value = correlation_id
        request.correlation_id = correlation_id

        response = self.get_response(request)
        response[self.HEADER] = correlation_id
        return response
