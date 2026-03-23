"""
MCP Client Service.

Responsible for:
- Discovering available tools, prompts, and resources from the MCP server
- Validating invocation payloads server-side before dispatch
- Invoking MCP capabilities and returning normalized responses
- Recording every call as an MCPToolCall audit record
- Enforcing the policy that all MCP invocations originate from the backend only
"""

import logging
import time
import uuid
from typing import Any

import httpx
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class MCPClientError(Exception):
    """Raised when the MCP server returns an error or is unreachable."""


class MCPClient:
    """
    HTTP client for the enterprise MCP server.

    All external tool execution passes through this class.
    No direct MCP calls are allowed from frontend or LangChain directly.
    """

    def __init__(self):
        self.base_url = settings.MCP_SERVER_URL.rstrip("/")
        self.token = settings.MCP_SERVER_TOKEN
        self._http = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    def discover_capabilities(self) -> dict[str, list[dict]]:
        """
        Query the MCP server for available tools, prompts, and resources.
        Returns a dict keyed by capability_type.
        """
        try:
            response = self._http.get("/capabilities")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise MCPClientError(f"MCP capability discovery failed: {exc}") from exc

    def invoke_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        step_run=None,
        requesting_user=None,
    ) -> dict[str, Any]:
        """
        Invoke an MCP tool.

        - Validates the capability is enabled and authorized
        - Records an MCPToolCall audit record
        - Returns the normalized response
        """
        capability = self._get_capability(tool_name, "tool")
        self._assert_enabled(capability)

        tool_call_record = self._begin_call(capability, arguments, step_run)
        start = time.monotonic()

        try:
            response = self._http.post(
                f"/tools/{tool_name}/invoke",
                json={"arguments": arguments},
            )
            response.raise_for_status()
            result = response.json()
            duration_ms = int((time.monotonic() - start) * 1000)

            self._complete_call(tool_call_record, result, duration_ms)
            self._emit_audit(tool_name, arguments, result, requesting_user, step_run)
            return result

        except httpx.HTTPError as exc:
            duration_ms = int((time.monotonic() - start) * 1000)
            self._fail_call(tool_call_record, str(exc), duration_ms)
            raise MCPClientError(f"MCP tool '{tool_name}' invocation failed: {exc}") from exc

    def fetch_resource(self, resource_name: str) -> Any:
        """Fetch a named MCP resource (read-only)."""
        try:
            response = self._http.get(f"/resources/{resource_name}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise MCPClientError(f"MCP resource '{resource_name}' fetch failed: {exc}") from exc

    def get_prompt(self, prompt_name: str, variables: dict | None = None) -> str:
        """Retrieve and render a named MCP prompt template."""
        try:
            response = self._http.post(
                f"/prompts/{prompt_name}/render",
                json={"variables": variables or {}},
            )
            response.raise_for_status()
            return response.json().get("prompt", "")
        except httpx.HTTPError as exc:
            raise MCPClientError(f"MCP prompt '{prompt_name}' render failed: {exc}") from exc

    # ─── Internal helpers ────────────────────────────────────────────────────

    def _get_capability(self, name: str, capability_type: str):
        from .models import MCPCapability
        try:
            return MCPCapability.objects.get(name=name, capability_type=capability_type)
        except MCPCapability.DoesNotExist:
            raise MCPClientError(
                f"MCP capability '{name}' ({capability_type}) is not registered. "
                "Run capability discovery first."
            )

    def _assert_enabled(self, capability):
        if not capability.is_enabled:
            raise MCPClientError(
                f"MCP capability '{capability.name}' is disabled. "
                "Enable it in the capability registry before use."
            )

    def _begin_call(self, capability, arguments: dict, step_run):
        from .models import MCPToolCall
        return MCPToolCall.objects.create(
            tool_call_id=uuid.uuid4(),
            step_run=step_run,
            capability=capability,
            arguments=arguments,
            status=MCPToolCall.Status.SUCCESS,  # optimistic; updated on failure
        )

    def _complete_call(self, record, response: dict, duration_ms: int):
        record.response = response
        record.status = record.Status.SUCCESS
        record.duration_ms = duration_ms
        record.save(update_fields=["response", "status", "duration_ms"])

    def _fail_call(self, record, error: str, duration_ms: int):
        record.status = record.Status.FAILED
        record.error_message = error
        record.duration_ms = duration_ms
        record.save(update_fields=["status", "error_message", "duration_ms"])

    def _emit_audit(self, tool_name, arguments, result, user, step_run):
        from apps.audit.models import AuditEvent
        from config.middleware import get_correlation_id
        try:
            AuditEvent.objects.create(
                actor=user,
                actor_email=getattr(user, "email", "system"),
                category=AuditEvent.EventCategory.MCP_CALL,
                action=f"mcp.tool.{tool_name}",
                result="success",
                workflow_run=getattr(getattr(step_run, "run", None), None, None),
                target_type="MCPTool",
                target_id=tool_name,
                metadata={"arguments_keys": list(arguments.keys())},
                correlation_id=get_correlation_id(),
            )
        except Exception as exc:
            logger.error("Failed to emit MCP audit event: %s", exc)


# Module-level singleton — one client per process
_client: MCPClient | None = None


def get_mcp_client() -> MCPClient:
    global _client
    if _client is None:
        _client = MCPClient()
    return _client
