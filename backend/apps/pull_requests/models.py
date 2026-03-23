"""Pull Request domain models."""

import uuid
from django.db import models
from django.conf import settings


class PullRequestRecord(models.Model):
    """Tracks a pull request created through the platform."""

    class PRStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        UNDER_REVIEW = "under_review", "Under Review"
        APPROVED = "approved", "Approved"
        MERGED = "merged", "Merged"
        CLOSED = "closed", "Closed"
        DECLINED = "declined", "Declined"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        "workflows.WorkflowRun", on_delete=models.PROTECT, related_name="pull_requests"
    )

    # GitHub / SCM data
    external_pr_id = models.CharField(max_length=100, blank=True)
    external_pr_number = models.PositiveIntegerField(null=True, blank=True)
    repository_url = models.URLField()
    repository_name = models.CharField(max_length=300)
    source_branch = models.CharField(max_length=300)
    target_branch = models.CharField(max_length=300, default="main")
    pr_url = models.URLField(blank=True)

    title = models.CharField(max_length=500)
    body = models.TextField(blank=True)
    labels = models.JSONField(default=list, blank=True)

    status = models.CharField(max_length=30, choices=PRStatus.choices, default=PRStatus.DRAFT)

    # Diff summary stored for review UI
    diff_summary = models.JSONField(default=dict, blank=True)
    files_changed = models.PositiveSmallIntegerField(default=0)
    lines_added = models.PositiveIntegerField(default=0)
    lines_removed = models.PositiveIntegerField(default=0)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_prs",
    )
    merged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="merged_prs",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    merged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"PR #{self.external_pr_number or 'draft'} — {self.title[:60]}"
