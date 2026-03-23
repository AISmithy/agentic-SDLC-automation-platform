from rest_framework import serializers
from .models import WorkflowTemplate, WorkflowTemplateVersion, WorkflowRun, WorkflowStepRun


class WorkflowTemplateVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowTemplateVersion
        fields = [
            "id", "version_number", "definition", "is_valid",
            "validation_errors", "is_active", "published_by", "created_at",
        ]
        read_only_fields = ["id", "version_number", "is_valid", "validation_errors", "created_at"]


class WorkflowTemplateSerializer(serializers.ModelSerializer):
    active_version = WorkflowTemplateVersionSerializer(read_only=True)
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = WorkflowTemplate
        fields = [
            "id", "name", "description", "slug", "owner", "owner_email",
            "team", "publish_state", "is_system_template", "allowed_roles",
            "active_version", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "active_version"]


class WorkflowStepRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowStepRun
        fields = "__all__"
        read_only_fields = ["id", "step_id", "created_at"]


class WorkflowRunSerializer(serializers.ModelSerializer):
    steps = WorkflowStepRunSerializer(many=True, read_only=True)
    initiated_by_email = serializers.EmailField(source="initiated_by.email", read_only=True)
    is_terminal = serializers.ReadOnlyField()

    class Meta:
        model = WorkflowRun
        fields = [
            "id", "session_id", "template", "template_version",
            "initiated_by", "initiated_by_email", "team",
            "state", "previous_state",
            "jira_issue_key", "jira_issue_data",
            "repository_url", "repository_name", "target_branch", "working_branch",
            "context", "error_message", "retry_count",
            "is_terminal", "steps",
            "created_at", "updated_at", "completed_at",
        ]
        read_only_fields = [
            "id", "session_id", "previous_state", "is_terminal",
            "created_at", "updated_at", "completed_at",
        ]


class WorkflowRunCreateSerializer(serializers.ModelSerializer):
    """Slim serializer for creating a new workflow run."""

    class Meta:
        model = WorkflowRun
        fields = ["template", "jira_issue_key", "repository_url", "team"]

    def create(self, validated_data):
        template = validated_data["template"]
        version = template.active_version
        if not version:
            raise serializers.ValidationError(
                {"template": "No active version found for this template."}
            )
        validated_data["template_version"] = version
        validated_data["initiated_by"] = self.context["request"].user
        return super().create(validated_data)
