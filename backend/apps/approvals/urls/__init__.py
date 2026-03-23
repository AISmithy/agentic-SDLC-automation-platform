from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.approvals.views import ApprovalRecordViewSet

router = DefaultRouter()
router.register("", ApprovalRecordViewSet, basename="approval")
urlpatterns = [path("", include(router.urls))]
