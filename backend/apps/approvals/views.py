from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ApprovalRecord
from .serializers import ApprovalRecordSerializer, ApprovalDecisionSerializer


class ApprovalRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ApprovalRecordSerializer
    filterset_fields = ["status", "action_type", "run"]

    def get_queryset(self):
        return ApprovalRecord.objects.select_related(
            "run", "decided_by", "requested_from"
        ).order_by("-created_at")

    @action(detail=True, methods=["post"])
    def decide(self, request, pk=None):
        """Record an approval or rejection decision."""
        approval = self.get_object()

        if approval.status != ApprovalRecord.ApprovalStatus.PENDING:
            return Response(
                {"detail": "This approval has already been decided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ApprovalDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        decision = serializer.validated_data["decision"]
        approval.status = (
            ApprovalRecord.ApprovalStatus.APPROVED
            if decision == "approved"
            else ApprovalRecord.ApprovalStatus.REJECTED
        )
        approval.decided_by = request.user
        approval.decision_notes = serializer.validated_data.get("notes", "")
        approval.decided_at = timezone.now()
        approval.save(update_fields=["status", "decided_by", "decision_notes", "decided_at"])

        # Emit audit event
        from apps.audit.models import AuditEvent
        from config.middleware import get_correlation_id
        AuditEvent.objects.create(
            actor=request.user,
            actor_email=request.user.email,
            actor_role=getattr(getattr(request.user, "role", None), "name", ""),
            category=AuditEvent.EventCategory.APPROVAL,
            action=f"approval.{decision}",
            result=decision,
            workflow_run=approval.run,
            target_type="ApprovalRecord",
            target_id=str(approval.id),
            target_description=approval.action_type,
            correlation_id=get_correlation_id(),
            metadata={"notes": approval.decision_notes},
        )

        return Response(ApprovalRecordSerializer(approval).data)
