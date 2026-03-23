from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.mcp_client.views import MCPCapabilityViewSet, MCPToolCallViewSet

router = DefaultRouter()
router.register("capabilities", MCPCapabilityViewSet, basename="mcp-capability")
router.register("calls", MCPToolCallViewSet, basename="mcp-call")

urlpatterns = [path("", include(router.urls))]
