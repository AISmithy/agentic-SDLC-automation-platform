"""Deployment domain models."""

import uuid
from django.db import models
from django.conf import settings


class DeploymentRecord(models.Model):
    """Records a deployment triggered through the platform."""

    class Environment(models.TextChoices):
        DEVELOPMENT = "development", "Development"
        # Future phases: QA, STAGING, PRODUCTION
        # Platform only supports DEVELOPMENT in Phase 1

    class DeploymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        ROLLED_BACK = "rolled_back", "Rolled Back"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        "workflows.WorkflowRun", on_delete=models.PROTECT, related_name="deployments"
    )
    pull_request = models.ForeignKey(
        "pull_requests.PullRequestRecord",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deployments",
    )

    environment = models.CharField(
        max_length=20, choices=Environment.choices, default=Environment.DEVELOPMENT
    )
    status = models.CharField(
        max_length=20, choices=DeploymentStatus.choices, default=DeploymentStatus.PENDING
    )

    # CI/CD reference
    external_pipeline_id = models.CharField(max_length=300, blank=True)
    pipeline_url = models.URLField(blank=True)
    commit_sha = models.CharField(max_length=100, blank=True)

    # Artifact info
    artifact_name = models.CharField(max_length=300, blank=True)
    artifact_version = models.CharField(max_length=100, blank=True)

    deployed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="deployments",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_deployments",
    )

    error_message = models.TextField(blank=True)
    deployment_log_url = models.URLField(blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Deploy to {self.environment} [{self.status}]"
