"""
Celery background tasks for the Agentic SDLC Platform.

Long-running operations (agent execution, MCP polling, deployment status checks)
are offloaded to workers so the API response layer stays responsive.
"""

import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="workers.execute_agent_task",
)
def execute_agent_task(self, step_run_id: str, agent_type: str, input_context: dict):
    """
    Execute a bounded LangChain agent for a given workflow step.
    Retries on transient LLM or network errors.
    """
    from apps.workflows.models import WorkflowStepRun
    from apps.agents.orchestrator.registry import get_agent_class

    try:
        step_run = WorkflowStepRun.objects.get(id=step_run_id)
    except WorkflowStepRun.DoesNotExist:
        logger.error("execute_agent_task: step_run %s not found", step_run_id)
        return {"error": "step_run_not_found"}

    # Mark step as running
    step_run.status = WorkflowStepRun.StepStatus.RUNNING
    step_run.started_at = timezone.now()
    step_run.save(update_fields=["status", "started_at"])

    try:
        AgentClass = get_agent_class(agent_type)
        agent = AgentClass(step_run=step_run)
        result = agent.run(input_context)

        step_run.status = WorkflowStepRun.StepStatus.COMPLETED
        step_run.output_data = result
        step_run.completed_at = timezone.now()
        step_run.save(update_fields=["status", "output_data", "completed_at"])

        logger.info("Agent %s completed for step %s", agent_type, step_run_id)
        return result

    except Exception as exc:
        logger.exception("Agent %s failed for step %s: %s", agent_type, step_run_id, exc)

        try:
            raise self.retry(exc=exc, countdown=10 * (self.request.retries + 1))
        except self.MaxRetriesExceededError:
            step_run.status = WorkflowStepRun.StepStatus.FAILED
            step_run.error_message = str(exc)
            step_run.completed_at = timezone.now()
            step_run.save(update_fields=["status", "error_message", "completed_at"])
            return {"error": str(exc)}


@shared_task(name="workers.sync_mcp_capabilities")
def sync_mcp_capabilities():
    """Periodic task: refresh MCP capability registry from the server."""
    from apps.mcp_client.discovery import sync_capabilities
    result = sync_capabilities()
    logger.info("MCP capability sync: %s", result)
    return result


@shared_task(
    bind=True,
    max_retries=10,
    default_retry_delay=30,
    name="workers.poll_deployment_status",
)
def poll_deployment_status(self, deployment_id: str):
    """
    Poll the CI/CD system for deployment completion.
    Retries until the deployment reaches a terminal state.
    """
    from apps.deployments.models import DeploymentRecord
    from apps.mcp_client.client import get_mcp_client

    try:
        deployment = DeploymentRecord.objects.get(id=deployment_id)
    except DeploymentRecord.DoesNotExist:
        return {"error": "deployment_not_found"}

    if deployment.status in (
        DeploymentRecord.DeploymentStatus.SUCCESS,
        DeploymentRecord.DeploymentStatus.FAILED,
        DeploymentRecord.DeploymentStatus.ROLLED_BACK,
    ):
        return {"status": deployment.status, "done": True}

    try:
        client = get_mcp_client()
        result = client.invoke_tool(
            "get_deployment_status",
            {"pipeline_id": deployment.external_pipeline_id},
        )

        remote_status = result.get("status", "").lower()
        if remote_status in ("success", "completed"):
            deployment.status = DeploymentRecord.DeploymentStatus.SUCCESS
            deployment.completed_at = timezone.now()
        elif remote_status in ("failed", "error"):
            deployment.status = DeploymentRecord.DeploymentStatus.FAILED
            deployment.error_message = result.get("message", "Deployment failed")
            deployment.completed_at = timezone.now()
        # else still in progress — retry

        deployment.save()

        if deployment.status not in (
            DeploymentRecord.DeploymentStatus.SUCCESS,
            DeploymentRecord.DeploymentStatus.FAILED,
        ):
            raise self.retry(countdown=30)

        return {"status": deployment.status, "done": True}

    except Exception as exc:
        logger.error("Deployment poll failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(name="workers.expire_stale_approvals")
def expire_stale_approvals():
    """
    Mark pending approvals as timed out if they have passed their expiry.
    Runs periodically via Celery Beat.
    """
    from apps.approvals.models import ApprovalRecord

    now = timezone.now()
    expired = ApprovalRecord.objects.filter(
        status=ApprovalRecord.ApprovalStatus.PENDING,
        expires_at__lt=now,
    )
    count = expired.update(status=ApprovalRecord.ApprovalStatus.TIMED_OUT)
    logger.info("Expired %d stale approvals", count)
    return {"expired": count}
