from rest_framework import viewsets, permissions
from .models import DeploymentRecord
from .serializers import DeploymentRecordSerializer


class DeploymentRecordViewSet(viewsets.ModelViewSet):
    queryset = DeploymentRecord.objects.select_related("run", "deployed_by").order_by("-started_at")
    serializer_class = DeploymentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "environment", "run"]
