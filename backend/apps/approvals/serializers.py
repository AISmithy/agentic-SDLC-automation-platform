from rest_framework import serializers
from .models import ApprovalRecord


class ApprovalRecordSerializer(serializers.ModelSerializer):
    decided_by_email = serializers.EmailField(source="decided_by.email", read_only=True)

    class Meta:
        model = ApprovalRecord
        fields = "__all__"
        read_only_fields = ["id", "created_at", "decided_at"]


class ApprovalDecisionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=["approved", "rejected"])
    notes = serializers.CharField(required=False, allow_blank=True)
