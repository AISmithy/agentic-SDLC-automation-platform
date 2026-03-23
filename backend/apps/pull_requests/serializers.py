from rest_framework import serializers
from .models import PullRequestRecord


class PullRequestRecordSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = PullRequestRecord
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
