from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import MCPCapability, MCPToolCall
from .serializers import MCPCapabilitySerializer, MCPToolCallSerializer
from .discovery import sync_capabilities


class MCPCapabilityViewSet(viewsets.ModelViewSet):
    queryset = MCPCapability.objects.all()
    serializer_class = MCPCapabilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["capability_type", "access_level", "is_enabled"]
    search_fields = ["name", "description"]

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def sync(self, request):
        """Trigger MCP capability discovery and sync."""
        result = sync_capabilities()
        return Response(result)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def toggle(self, request, pk=None):
        """Enable or disable a capability."""
        cap = self.get_object()
        cap.is_enabled = not cap.is_enabled
        cap.save(update_fields=["is_enabled"])
        return Response({"is_enabled": cap.is_enabled})


class MCPToolCallViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MCPToolCall.objects.select_related("capability", "step_run").order_by("-invoked_at")
    serializer_class = MCPToolCallSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "capability__name"]
