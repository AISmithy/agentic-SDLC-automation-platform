from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import AuditEvent
from .serializers import AuditEventSerializer


class AuditEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Audit log is read-only from the API. Events are appended by platform services.
    """
    queryset = AuditEvent.objects.select_related("actor", "workflow_run").order_by("-timestamp")
    serializer_class = AuditEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    filterset_fields = ["category", "action", "result", "workflow_run", "actor"]
    search_fields = ["action", "target_description", "actor_email"]
    ordering_fields = ["timestamp", "category", "action"]
