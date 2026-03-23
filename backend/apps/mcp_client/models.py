"""
MCP integration models.

MCPCapability — registry of discovered MCP tools/prompts/resources.
MCPToolCall — audit record for every MCP invocation.
"""

import uuid
from django.db import models


class MCPCapability(models.Model):
    """Registry entry for a discovered MCP capability."""

    class CapabilityType(models.TextChoices):
        TOOL = "tool", "Tool"
        PROMPT = "prompt", "Prompt"
        RESOURCE = "resource", "Resource"

    class AccessLevel(models.TextChoices):
        READ_ONLY = "read_only", "Read Only"
        WRITE_CAPABLE = "write_capable", "Write Capable"
        APPROVAL_REQUIRED = "approval_required", "Approval Required"
        ENVIRONMENT_SENSITIVE = "environment_sensitive", "Environment Sensitive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    capability_type = models.CharField(max_length=20, choices=CapabilityType.choices)
    name = models.CharField(max_length=300, unique=True)
    description = models.TextField(blank=True)

    # Raw MCP schema as discovered from the server
    schema = models.JSONField(default=dict, blank=True)

    # Classification
    access_level = models.CharField(
        max_length=30, choices=AccessLevel.choices, default=AccessLevel.READ_ONLY
    )
    is_enabled = models.BooleanField(default=True)

    # Unknown write-capable tools must be disabled by default (policy rule)
    is_unknown_write = models.BooleanField(default=False)

    # Roles permitted to invoke this capability
    allowed_roles = models.JSONField(default=list, blank=True)

    last_discovered_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["capability_type", "name"]
        verbose_name_plural = "MCP Capabilities"

    def __str__(self):
        return f"{self.capability_type}: {self.name}"


class MCPToolCall(models.Model):
    """Immutable audit record for every MCP tool/resource invocation."""

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        TIMEOUT = "timeout", "Timeout"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tool_call_id = models.UUIDField(unique=True, default=uuid.uuid4)

    step_run = models.ForeignKey(
        "workflows.WorkflowStepRun",
        on_delete=models.CASCADE,
        related_name="mcp_calls",
        null=True,
        blank=True,
    )
    capability = models.ForeignKey(
        MCPCapability,
        on_delete=models.PROTECT,
        related_name="calls",
    )

    # Arguments (redacted as needed)
    arguments = models.JSONField(default=dict, blank=True)
    arguments_redacted = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=Status.choices)

    # Response (redacted as needed)
    response = models.JSONField(null=True, blank=True)
    response_redacted = models.BooleanField(default=False)

    error_message = models.TextField(blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    # Approval reference if this call required approval
    approval_record = models.ForeignKey(
        "approvals.ApprovalRecord",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mcp_calls",
    )

    invoked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-invoked_at"]

    def __str__(self):
        return f"{self.capability.name} [{self.status}] @ {self.invoked_at}"
