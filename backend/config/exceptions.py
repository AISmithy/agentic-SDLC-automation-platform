"""Custom exception handler returning consistent structured error responses."""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def platform_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {
                "error": "internal_server_error",
                "detail": "An unexpected error occurred.",
                "correlation_id": getattr(
                    context.get("request"), "correlation_id", None
                ),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    response.data = {
        "error": _classify_error(response.status_code),
        "detail": response.data,
        "correlation_id": getattr(
            context.get("request"), "correlation_id", None
        ),
    }
    return response


def _classify_error(status_code: int) -> str:
    return {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        422: "unprocessable_entity",
        429: "too_many_requests",
    }.get(status_code, "api_error")
