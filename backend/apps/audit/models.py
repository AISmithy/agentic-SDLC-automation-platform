"""
Audit models — append-only event log for compliance and non-repudiation.

AuditEvent records every high-impact action with identity, timestamp,
action, target, and result. Events are never updated or deleted.
"""

import uuid
from django.db import models
from django.conf import settings


class AuditEvent(models.Model):
    """
    Immutable audit event. Append-only by convention (never update).
    High-impact actions must always emit an AuditEvent.
    """

    class EventCategory(models.TextChoices):
        AUTH = "auth", "Authentication"
        WORKFLOW = "workflow", "Workflow"
        AGENT = "agent", "Agent Execution"
        MCP_CALL = "mcp_call", "MCP Tool Call"
        APPROVAL = "approval", "Approval"
        PR = "pr", "Pull Request"
        DEPLOYMENT = "deployment", "Deployment"
        POLICY = "policy", "Policy Enforcement"
        ADMIN = "admin", "Administration"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.UUIDField(unique=True, default=uuid.uuid4)

    # Who performed the action
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    actor_email = models.EmailField(blank=True)  # snapshot in case user deleted
    actor_role = models.CharField(max_length=100, blank=True)

    # What happened
    category = models.CharField(max_length=30, choices=EventCategory.choices, db_index=True)
    action = models.CharField(max_length=300, db_index=True)
    result = models.CharField(max_length=50)  # success / failure / blocked

    # Context
    workflow_run = models.ForeignKey(
        "workflows.WorkflowRun",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )

    # Target resource
    target_type = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=200, blank=True)
    target_description = models.CharField(max_length=500, blank=True)

    # Rich metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Observability IDs
    correlation_id = models.CharField(max_length=100, blank=True, db_index=True)
    session_id = models.UUIDField(null=True, blank=True, db_index=True)

    # IP / request metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["category", "timestamp"]),
            models.Index(fields=["actor", "timestamp"]),
            models.Index(fields=["workflow_run", "timestamp"]),
        ]

    def __str__(self):
        return f"[{self.category}] {self.action} by {self.actor_email} @ {self.timestamp}"

    def save(self, *args, **kwargs):
        """Prevent updates — audit events are append-only."""
        if self.pk:
            raise RuntimeError("AuditEvent records are immutable and cannot be updated.")
        super().save(*args, **kwargs)
