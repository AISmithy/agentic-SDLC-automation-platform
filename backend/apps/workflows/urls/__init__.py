from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.workflows.views import WorkflowTemplateViewSet, WorkflowRunViewSet

router = DefaultRouter()
router.register("templates", WorkflowTemplateViewSet, basename="workflow-template")
router.register("runs", WorkflowRunViewSet, basename="workflow-run")

urlpatterns = [path("", include(router.urls))]
