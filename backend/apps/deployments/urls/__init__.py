from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.deployments.views import DeploymentRecordViewSet

router = DefaultRouter()
router.register("", DeploymentRecordViewSet, basename="deployment")
urlpatterns = [path("", include(router.urls))]
