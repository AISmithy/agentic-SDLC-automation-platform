from rest_framework import serializers
from .models import AgentRun
from .orchestrator.registry import AGENT_REGISTRY


class AgentRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentRun
        fields = "__all__"
        read_only_fields = ["id", "started_at", "completed_at", "duration_ms"]


class AgentExecuteSerializer(serializers.Serializer):
    step_run_id = serializers.UUIDField()
    agent_type = serializers.ChoiceField(choices=list(AGENT_REGISTRY.keys()))
    input_context = serializers.DictField(default=dict)

    def validate_step_run_id(self, value):
        from apps.workflows.models import WorkflowStepRun
        try:
            return WorkflowStepRun.objects.get(id=value)
        except WorkflowStepRun.DoesNotExist:
            raise serializers.ValidationError("Step run not found.")
