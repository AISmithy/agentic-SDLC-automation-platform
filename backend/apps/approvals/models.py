"""
Approval models.

ApprovalRecord — human-in-the-loop gate for high-impact workflow actions.
"""

import uuid
from django.db import models
from django.conf import settings


class ApprovalRecord(models.Model):
    """Gate that must be resolved before a high-impact action proceeds."""

    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        TIMED_OUT = "timed_out", "Timed Out"
        CANCELLED = "cancelled", "Cancelled"

    class ActionType(models.TextChoices):
        PLAN_APPROVAL = "plan_approval", "Implementation Plan Approval"
        BRANCH_CREATE = "branch_create", "Branch Creation"
        CODE_REVIEW = "code_review", "Code Change Review"
        PR_CREATE = "pr_create", "Pull Request Creation"
        PR_REVIEW = "pr_review", "Pull Request Review"
        DEPLOY_TO_DEV = "deploy_to_dev", "Deploy to Development"
        CUSTOM_FLOW_PUBLISH = "custom_flow_publish", "Custom Flow Publish"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        "workflows.WorkflowRun",
        on_delete=models.CASCADE,
        related_name="approvals",
    )
    step_run = models.ForeignKey(
        "workflows.WorkflowStepRun",
        on_delete=models.CASCADE,
        related_name="approvals",
        null=True,
        blank=True,
    )

    action_type = models.CharField(max_length=50, choices=ActionType.choices)
    status = models.CharField(
        max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING
    )

    # Who must approve (role or specific user)
    required_role = models.CharField(max_length=50, blank=True)
    requested_from = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requested_approvals",
    )

    # Decision
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="decided_approvals",
    )
    decision_notes = models.TextField(blank=True)

    # Payload displayed to approver
    context_snapshot = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["run", "action_type"]),
        ]

    def __str__(self):
        return f"{self.action_type} [{self.status}]"
