from rest_framework import serializers
from .models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    actor_email_display = serializers.SerializerMethodField()

    class Meta:
        model = AuditEvent
        fields = "__all__"
        read_only_fields = ["id", "event_id", "timestamp"]

    def get_actor_email_display(self, obj):
        return obj.actor_email or (obj.actor.email if obj.actor else "system")
