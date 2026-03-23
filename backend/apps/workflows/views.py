from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import WorkflowTemplate, WorkflowTemplateVersion, WorkflowRun, WorkflowStepRun
from .serializers import (
    WorkflowTemplateSerializer, WorkflowTemplateVersionSerializer,
    WorkflowRunSerializer, WorkflowRunCreateSerializer, WorkflowStepRunSerializer,
)


class WorkflowTemplateViewSet(viewsets.ModelViewSet):
    queryset = WorkflowTemplate.objects.select_related("owner", "team").all()
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["name", "slug", "description"]
    filterset_fields = ["publish_state", "is_system_template", "team"]

    def get_serializer_class(self):
        return WorkflowTemplateSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """Publish the active draft version of a template."""
        template = self.get_object()
        version = template.active_version
        if not version:
            return Response(
                {"detail": "No active version to publish."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        template.publish_state = WorkflowTemplate.PublishState.PUBLISHED
        template.save(update_fields=["publish_state", "updated_at"])
        return Response({"detail": "Template published."})

    @action(detail=True, methods=["get"])
    def versions(self, request, pk=None):
        template = self.get_object()
        versions = template.versions.all()
        serializer = WorkflowTemplateVersionSerializer(versions, many=True)
        return Response(serializer.data)


class WorkflowRunViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["state", "jira_issue_key", "template"]

    def get_queryset(self):
        user = self.request.user
        qs = WorkflowRun.objects.select_related(
            "template", "template_version", "initiated_by", "team"
        ).prefetch_related("steps")
        # Admins see all runs; others see only their own or team runs
        if not (user.is_staff or user.is_superuser):
            qs = qs.filter(initiated_by=user)
        return qs.order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return WorkflowRunCreateSerializer
        return WorkflowRunSerializer

    @action(detail=True, methods=["post"])
    def advance(self, request, pk=None):
        """
        Advance workflow to the next state.
        Delegates to the WorkflowEngine service.
        """
        from apps.workflows.engine import WorkflowEngine
        run = self.get_object()
        action_name = request.data.get("action")
        payload = request.data.get("payload", {})
        try:
            engine = WorkflowEngine(run, request.user)
            updated_run = engine.advance(action_name, payload)
            return Response(WorkflowRunSerializer(updated_run).data)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a running workflow session."""
        run = self.get_object()
        if run.is_terminal:
            return Response(
                {"detail": "Run is already in a terminal state."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        run.state = WorkflowRun.State.CLOSED
        run.save(update_fields=["state", "updated_at"])
        return Response({"detail": "Workflow run cancelled."})

    @action(detail=True, methods=["get"])
    def steps(self, request, pk=None):
        run = self.get_object()
        serializer = WorkflowStepRunSerializer(run.steps.all(), many=True)
        return Response(serializer.data)
