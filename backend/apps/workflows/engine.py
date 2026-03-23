"""
WorkflowEngine — enforces the SDLC state machine.

Each call to advance() validates the requested transition, applies
policy checks, persists the new state, and emits an audit event.
No invalid transitions are permitted. High-risk actions require an
approved ApprovalRecord before they can proceed.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from django.conf import settings
from django.db import transaction

from .models import WorkflowRun, WorkflowStepRun

logger = logging.getLogger(__name__)

# ─── Allowed state transitions ───────────────────────────────────────────────
# action_name -> (required_current_state, next_state)
TRANSITIONS: dict[str, tuple[str, str]] = {
    "select_story": (
        WorkflowRun.State.SESSION_CREATED,
        WorkflowRun.State.STORY_SELECTED,
    ),
    "analyze_story": (
        WorkflowRun.State.STORY_SELECTED,
        WorkflowRun.State.STORY_ANALYZED,
    ),
    "generate_plan": (
        WorkflowRun.State.STORY_ANALYZED,
        WorkflowRun.State.PLAN_GENERATED,
    ),
    "approve_plan": (
        WorkflowRun.State.PLAN_GENERATED,
        WorkflowRun.State.PLAN_APPROVED,
    ),
    "confirm_repository": (
        WorkflowRun.State.PLAN_APPROVED,
        WorkflowRun.State.REPOSITORY_CONFIRMED,
    ),
    "create_branch": (
        WorkflowRun.State.REPOSITORY_CONFIRMED,
        WorkflowRun.State.BRANCH_CREATED,
    ),
    "prepare_context": (
        WorkflowRun.State.BRANCH_CREATED,
        WorkflowRun.State.CONTEXT_PREPARED,
    ),
    "generate_changes": (
        WorkflowRun.State.CONTEXT_PREPARED,
        WorkflowRun.State.CHANGE_PROPOSAL_GENERATED,
    ),
    "review_changes": (
        WorkflowRun.State.CHANGE_PROPOSAL_GENERATED,
        WorkflowRun.State.CHANGES_REVIEWED,
    ),
    "create_pr_draft": (
        WorkflowRun.State.CHANGES_REVIEWED,
        WorkflowRun.State.PR_DRAFT_CREATED,
    ),
    "submit_for_review": (
        WorkflowRun.State.PR_DRAFT_CREATED,
        WorkflowRun.State.REVIEW_PENDING,
    ),
    "approve_review": (
        WorkflowRun.State.REVIEW_PENDING,
        WorkflowRun.State.REVIEW_APPROVED,
    ),
    "request_deployment": (
        WorkflowRun.State.REVIEW_APPROVED,
        WorkflowRun.State.DEPLOYMENT_PENDING,
    ),
    "confirm_deployed": (
        WorkflowRun.State.DEPLOYMENT_PENDING,
        WorkflowRun.State.DEPLOYED_TO_DEVELOPMENT,
    ),
    "request_rework": (
        WorkflowRun.State.REVIEW_PENDING,
        WorkflowRun.State.REWORK_REQUIRED,
    ),
    "resubmit_after_rework": (
        WorkflowRun.State.REWORK_REQUIRED,
        WorkflowRun.State.CHANGES_REVIEWED,
    ),
    "close": (None, WorkflowRun.State.CLOSED),  # Any state → Closed
    "mark_failed": (None, WorkflowRun.State.FAILED),
}

# Actions that require an approved ApprovalRecord before proceeding
APPROVAL_REQUIRED_ACTIONS = {"approve_plan", "create_branch", "create_pr_draft", "confirm_deployed"}


class WorkflowEngine:
    """
    State machine engine for WorkflowRun.

    Usage:
        engine = WorkflowEngine(run, requesting_user)
        updated_run = engine.advance("select_story", payload={"jira_issue_key": "PROJ-123"})
    """

    def __init__(self, run: WorkflowRun, user):
        self.run = run
        self.user = user

    def advance(self, action_name: str, payload: dict[str, Any] | None = None) -> WorkflowRun:
        payload = payload or {}

        if self.run.is_terminal:
            raise ValueError(
                f"Workflow run is in terminal state '{self.run.state}' and cannot be advanced."
            )

        transition = TRANSITIONS.get(action_name)
        if not transition:
            raise ValueError(f"Unknown action '{action_name}'.")

        required_state, next_state = transition

        # Validate current state (None means any state is acceptable)
        if required_state is not None and self.run.state != required_state:
            raise ValueError(
                f"Action '{action_name}' requires state '{required_state}', "
                f"but run is in '{self.run.state}'."
            )

        # Policy: check approval gate
        if action_name in APPROVAL_REQUIRED_ACTIONS:
            self._assert_approved(action_name)

        # Apply transition
        with transaction.atomic():
            self._apply_transition(action_name, next_state, payload)
            self._emit_audit(action_name, next_state)

        logger.info(
            "workflow_transition",
            extra={
                "run_id": str(self.run.id),
                "action": action_name,
                "from_state": self.run.previous_state,
                "to_state": self.run.state,
                "user": self.user.email,
            },
        )
        return self.run

    def _assert_approved(self, action_name: str):
        from apps.approvals.models import ApprovalRecord

        approved = ApprovalRecord.objects.filter(
            run=self.run,
            action_type=action_name,
            status=ApprovalRecord.ApprovalStatus.APPROVED,
        ).exists()
        if not approved:
            raise ValueError(
                f"Action '{action_name}' requires an approved ApprovalRecord. "
                "Please obtain approval before proceeding."
            )

    def _apply_transition(self, action_name: str, next_state: str, payload: dict):
        previous_state = self.run.state
        self.run.previous_state = previous_state
        self.run.state = next_state

        # Merge payload into run context
        if payload:
            self.run.context.update(payload)

        # State-specific side effects
        if action_name == "select_story":
            self.run.jira_issue_key = payload.get("jira_issue_key", self.run.jira_issue_key)
            self.run.jira_issue_data = payload.get("jira_issue_data", self.run.jira_issue_data)

        if action_name == "confirm_repository":
            self.run.repository_url = payload.get("repository_url", self.run.repository_url)
            self.run.repository_name = payload.get("repository_name", self.run.repository_name)
            self.run.target_branch = payload.get("target_branch", self.run.target_branch)

        if action_name == "create_branch":
            self.run.working_branch = payload.get("working_branch", self.run.working_branch)

        if next_state in (WorkflowRun.State.CLOSED, WorkflowRun.State.DEPLOYED_TO_DEVELOPMENT):
            self.run.completed_at = datetime.now(timezone.utc)

        self.run.save()

    def _emit_audit(self, action_name: str, next_state: str):
        from apps.audit.models import AuditEvent
        from config.middleware import get_correlation_id

        try:
            AuditEvent.objects.create(
                actor=self.user,
                actor_email=self.user.email,
                actor_role=getattr(getattr(self.user, "role", None), "name", ""),
                category=AuditEvent.EventCategory.WORKFLOW,
                action=f"workflow.{action_name}",
                result="success",
                workflow_run=self.run,
                target_type="WorkflowRun",
                target_id=str(self.run.id),
                target_description=f"Run {self.run.session_id} → {next_state}",
                correlation_id=get_correlation_id(),
                session_id=self.run.session_id,
                metadata={
                    "from_state": self.run.previous_state,
                    "to_state": next_state,
                },
            )
        except Exception as exc:
            logger.error("Failed to emit audit event: %s", exc)
