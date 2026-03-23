from rest_framework import serializers
from .models import MCPCapability, MCPToolCall


class MCPCapabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MCPCapability
        fields = "__all__"
        read_only_fields = ["id", "created_at", "last_discovered_at"]


class MCPToolCallSerializer(serializers.ModelSerializer):
    capability_name = serializers.CharField(source="capability.name", read_only=True)

    class Meta:
        model = MCPToolCall
        fields = "__all__"
        read_only_fields = ["id", "tool_call_id", "invoked_at"]
