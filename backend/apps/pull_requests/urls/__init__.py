from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.pull_requests.views import PullRequestRecordViewSet

router = DefaultRouter()
router.register("", PullRequestRecordViewSet, basename="pull-request")
urlpatterns = [path("", include(router.urls))]
