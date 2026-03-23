"""Agent API views — trigger agent execution and retrieve agent run results."""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AgentRun
from .serializers import AgentRunSerializer, AgentExecuteSerializer


class AgentRunViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AgentRunSerializer
    filterset_fields = ["agent_type", "status", "step_run"]

    def get_queryset(self):
        return AgentRun.objects.select_related("step_run__run").order_by("-started_at")

    @action(detail=False, methods=["post"])
    def execute(self, request):
        """
        Trigger a bounded agent for a given workflow step.
        Validates allowed agent types and policy before dispatching.
        """
        serializer = AgentExecuteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        from workers.tasks import execute_agent_task
        result = execute_agent_task.delay(
            step_run_id=str(serializer.validated_data["step_run_id"]),
            agent_type=serializer.validated_data["agent_type"],
            input_context=serializer.validated_data["input_context"],
        )
        return Response(
            {"task_id": result.id, "detail": "Agent dispatched to worker queue."},
            status=status.HTTP_202_ACCEPTED,
        )
