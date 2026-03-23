from rest_framework import serializers
from .models import DeploymentRecord


class DeploymentRecordSerializer(serializers.ModelSerializer):
    deployed_by_email = serializers.EmailField(source="deployed_by.email", read_only=True)

    class Meta:
        model = DeploymentRecord
        fields = "__all__"
        read_only_fields = ["id", "started_at"]
