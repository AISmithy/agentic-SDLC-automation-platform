from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.accounts.views import UserViewSet, RoleViewSet, TeamViewSet

router = DefaultRouter()
router.register("roles", RoleViewSet, basename="role")
router.register("teams", TeamViewSet, basename="team")
router.register("", UserViewSet, basename="user")

urlpatterns = [path("", include(router.urls))]
