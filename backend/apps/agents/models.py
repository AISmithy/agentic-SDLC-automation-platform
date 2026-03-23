"""
Agent execution models.

AgentRun — records a single bounded LangChain agent invocation with its
inputs, outputs, token usage, and provenance.
"""

import uuid
from django.db import models


class AgentRun(models.Model):
    """Records one LangChain agent execution within a workflow step."""

    class AgentType(models.TextChoices):
        STORY_ANALYSIS = "story_analysis", "Story Analysis Agent"
        IMPLEMENTATION_PLANNING = "implementation_planning", "Implementation Planning Agent"
        CONTEXT_RETRIEVAL = "context_retrieval", "Context Retrieval Agent"
        CODE_PROPOSAL = "code_proposal", "Code Proposal Agent"
        TEST_GENERATION = "test_generation", "Test Generation Agent"
        PR_PACKAGING = "pr_packaging", "PR Packaging Agent"
        REVIEW_READINESS = "review_readiness", "Review Readiness Agent"
        DEPLOYMENT_READINESS = "deployment_readiness", "Deployment Readiness Agent"

    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    step_run = models.ForeignKey(
        "workflows.WorkflowStepRun",
        on_delete=models.CASCADE,
        related_name="agent_runs",
    )

    agent_type = models.CharField(max_length=50, choices=AgentType.choices)
    agent_version = models.CharField(max_length=50, default="1.0")

    # LLM configuration used
    llm_provider = models.CharField(max_length=50)
    llm_model = models.CharField(max_length=100)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RUNNING)

    # Prompt and response (structured)
    system_prompt = models.TextField(blank=True)
    user_prompt = models.TextField(blank=True)
    raw_response = models.TextField(blank=True)

    # Parsed structured output (Pydantic schema validated)
    structured_output = models.JSONField(null=True, blank=True)
    output_schema_version = models.CharField(max_length=20, default="1.0")

    # Tool calls made during this agent run
    tool_calls_summary = models.JSONField(default=list, blank=True)

    # Token metrics
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)

    error_message = models.TextField(blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.agent_type} [{self.status}]"
