from rest_framework import serializers
from .models import User, Role, Team


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), source="role", write_only=True, required=False
    )
    teams = TeamSerializer(many=True, read_only=True)
    effective_display_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "display_name", "effective_display_name",
            "role", "role_id", "teams", "is_active", "sso_provider",
            "preferences", "created_at", "updated_at", "last_login_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "sso_provider"]


class UserProfileSerializer(serializers.ModelSerializer):
    """Lightweight self-profile serializer."""
    role = RoleSerializer(read_only=True)
    effective_display_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "display_name", "effective_display_name",
            "role", "is_active", "preferences",
        ]
        read_only_fields = ["id", "email", "role", "is_active"]
