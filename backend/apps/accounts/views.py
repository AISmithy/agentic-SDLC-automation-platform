from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Role, Team
from .serializers import UserSerializer, UserProfileSerializer, RoleSerializer, TeamSerializer


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["name", "role_type"]


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.prefetch_related("members").all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["name", "slug"]
    filterset_fields = ["slug"]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("role").prefetch_related("teams").all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ["email", "full_name", "display_name"]
    filterset_fields = ["role__role_type", "is_active"]

    @action(detail=False, methods=["get", "patch"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Return or update the authenticated user's own profile."""
        if request.method == "GET":
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
