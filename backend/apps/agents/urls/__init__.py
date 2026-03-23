from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.agents.views import AgentRunViewSet

router = DefaultRouter()
router.register("runs", AgentRunViewSet, basename="agent-run")

urlpatterns = [path("", include(router.urls))]
