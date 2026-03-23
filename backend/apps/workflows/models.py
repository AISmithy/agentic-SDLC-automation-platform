"""
Workflow domain models.

WorkflowTemplate / WorkflowTemplateVersion — versioned, reusable flow definitions.
WorkflowRun — a stateful session for one story/task execution.
WorkflowStepRun — granular step-level execution record.
"""

import uuid
from django.db import models
from django.conf import settings


class WorkflowTemplate(models.Model):
    """A named, reusable SDLC workflow template."""

    class PublishState(models.TextChoices):
        DRAFT = "draft", "Draft"
        REVIEW = "review", "Under Review"
        PUBLISHED = "published", "Published"
        DEPRECATED = "deprecated", "Deprecated"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_templates",
    )
    team = models.ForeignKey(
        "accounts.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="templates",
    )

    publish_state = models.CharField(
        max_length=20, choices=PublishState.choices, default=PublishState.DRAFT
    )
    is_system_template = models.BooleanField(default=False)

    # Role restrictions: only these roles may execute this template
    allowed_roles = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name

    @property
    def active_version(self):
        return self.versions.filter(is_active=True).order_by("-version_number").first()


class WorkflowTemplateVersion(models.Model):
    """Immutable versioned snapshot of a flow definition."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        WorkflowTemplate, on_delete=models.CASCADE, related_name="versions"
    )
    version_number = models.PositiveIntegerField()

    # The flow definition: nodes, edges, configurations
    # Schema: {metadata, nodes: [...], edges: [...], node_configs: {...}}
    definition = models.JSONField()

    # Validation outcome
    is_valid = models.BooleanField(default=False)
    validation_errors = models.JSONField(default=list, blank=True)

    is_active = models.BooleanField(default=False)
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="published_versions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("template", "version_number")]
        ordering = ["-version_number"]

    def __str__(self):
        return f"{self.template.name} v{self.version_number}"


class WorkflowRun(models.Model):
    """
    A stateful workflow session. Persisted throughout the full SDLC cycle.
    State transitions are enforced by the WorkflowEngine service.
    """

    class State(models.TextChoices):
        SESSION_CREATED = "session_created", "Session Created"
        STORY_SELECTED = "story_selected", "Story Selected"
        STORY_ANALYZED = "story_analyzed", "Story Analyzed"
        PLAN_GENERATED = "plan_generated", "Plan Generated"
        PLAN_APPROVED = "plan_approved", "Plan Approved"
        REPOSITORY_CONFIRMED = "repository_confirmed", "Repository Confirmed"
        BRANCH_CREATED = "branch_created", "Branch Created"
        CONTEXT_PREPARED = "context_prepared", "Context Prepared"
        CHANGE_PROPOSAL_GENERATED = "change_proposal_generated", "Change Proposal Generated"
        CHANGES_REVIEWED = "changes_reviewed", "Changes Reviewed"
        PR_DRAFT_CREATED = "pr_draft_created", "PR Draft Created"
        REVIEW_PENDING = "review_pending", "Review Pending"
        REVIEW_APPROVED = "review_approved", "Review Approved"
        DEPLOYMENT_PENDING = "deployment_pending", "Deployment Pending"
        DEPLOYED_TO_DEVELOPMENT = "deployed_to_development", "Deployed to Development"
        REWORK_REQUIRED = "rework_required", "Rework Required"
        CLOSED = "closed", "Closed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(unique=True, default=uuid.uuid4)

    template = models.ForeignKey(
        WorkflowTemplate, on_delete=models.PROTECT, related_name="runs"
    )
    template_version = models.ForeignKey(
        WorkflowTemplateVersion, on_delete=models.PROTECT, related_name="runs"
    )

    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="initiated_runs",
    )
    team = models.ForeignKey(
        "accounts.Team", on_delete=models.SET_NULL, null=True, blank=True
    )

    # Current state
    state = models.CharField(
        max_length=50, choices=State.choices, default=State.SESSION_CREATED, db_index=True
    )
    previous_state = models.CharField(max_length=50, blank=True)

    # Story / task context
    jira_issue_key = models.CharField(max_length=100, blank=True, db_index=True)
    jira_issue_data = models.JSONField(default=dict, blank=True)

    # Repository context
    repository_url = models.URLField(blank=True)
    repository_name = models.CharField(max_length=300, blank=True)
    target_branch = models.CharField(max_length=300, blank=True, default="main")
    working_branch = models.CharField(max_length=300, blank=True)

    # Execution context (accumulated as the run progresses)
    context = models.JSONField(default=dict, blank=True)

    # Failure / retry
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["state", "created_at"]),
            models.Index(fields=["initiated_by", "state"]),
        ]

    def __str__(self):
        return f"Run {self.session_id} [{self.state}]"

    @property
    def is_terminal(self) -> bool:
        return self.state in (self.State.CLOSED, self.State.FAILED)


class WorkflowStepRun(models.Model):
    """Granular execution record for a single step within a WorkflowRun."""

    class StepType(models.TextChoices):
        AGENT = "agent", "Agent Task"
        MCP_TOOL = "mcp_tool", "MCP Tool Call"
        MCP_RESOURCE = "mcp_resource", "MCP Resource Fetch"
        APPROVAL = "approval", "Human Approval"
        CONDITION = "condition", "Condition Branch"
        NOTIFICATION = "notification", "Notification"
        PR_ACTION = "pr_action", "PR Action"
        DEPLOY_ACTION = "deploy_action", "Deploy Action"

    class StepStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"
        AWAITING_APPROVAL = "awaiting_approval", "Awaiting Approval"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    step_id = models.UUIDField(default=uuid.uuid4)  # correlation ID for telemetry
    run = models.ForeignKey(WorkflowRun, on_delete=models.CASCADE, related_name="steps")

    step_type = models.CharField(max_length=30, choices=StepType.choices)
    step_name = models.CharField(max_length=300)
    node_id = models.CharField(max_length=100, blank=True)  # matches flow builder node ID

    status = models.CharField(
        max_length=30, choices=StepStatus.choices, default=StepStatus.PENDING
    )

    # Input/output — redaction applied at service layer for sensitive data
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)

    error_message = models.TextField(blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.step_name} [{self.status}]"
