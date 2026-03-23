from rest_framework import viewsets, permissions
from .models import PullRequestRecord
from .serializers import PullRequestRecordSerializer


class PullRequestRecordViewSet(viewsets.ModelViewSet):
    queryset = PullRequestRecord.objects.select_related("run", "created_by").order_by("-created_at")
    serializer_class = PullRequestRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "run", "repository_name"]
    search_fields = ["title", "external_pr_number", "repository_name"]
