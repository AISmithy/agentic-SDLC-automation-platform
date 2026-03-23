import { useParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { workflowApi } from "@/services/api";
import { CheckCircle2, XCircle, FileCode, GitBranch, Loader2, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { formatDistanceToNow } from "date-fns";
import clsx from "clsx";

const STATE_LABEL: Record<string, string> = {
  session_created: "Session Created",
  story_selected: "Story Selected",
  story_analyzed: "Story Analyzed",
  plan_generated: "Plan Generated",
  plan_approved: "Plan Approved",
  repository_confirmed: "Repository Confirmed",
  branch_created: "Branch Created",
  context_prepared: "Context Prepared",
  change_proposal_generated: "Changes Proposed",
  changes_reviewed: "Changes Reviewed",
  pr_draft_created: "PR Draft Created",
  review_pending: "Review Pending",
  review_approved: "Review Approved",
  deployment_pending: "Deployment Pending",
  deployed_to_development: "Deployed",
  rework_required: "Rework Required",
  closed: "Closed",
  failed: "Failed",
};

const WORKFLOW_STEPS = [
  "story_selected", "story_analyzed", "plan_generated", "plan_approved",
  "branch_created", "change_proposal_generated", "changes_reviewed",
  "pr_draft_created", "review_approved", "deployed_to_development",
];

// Mock diff data — in production this comes from the WorkflowRun context or MCP
const MOCK_DIFF = `diff --git a/src/auth/middleware.py b/src/auth/middleware.py
index a1b2c3d..e4f5a6b 100644
--- a/src/auth/middleware.py
+++ b/src/auth/middleware.py
@@ -42,6 +42,18 @@ class JWTAuthMiddleware:
         return get_response(request)

+class RateLimitMiddleware:
+    """Rate limit API endpoints to prevent abuse."""
+
+    LIMIT = 100  # requests per minute
+
+    def __init__(self, get_response):
+        self.get_response = get_response
+
+    def __call__(self, request):
+        if self._is_rate_limited(request):
+            return JsonResponse({'error': 'rate_limited'}, status=429)
+        return self.get_response(request)
+
     def _is_token_valid(self, token: str) -> bool:
         try:
             jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])`;

function DiffViewer({ diff }: { diff: string }) {
  const lines = diff.split("\n");
  return (
    <div className="overflow-x-auto rounded-md border bg-gray-950 font-mono text-xs">
      {lines.map((line, i) => (
        <div
          key={i}
          className={clsx(
            "px-4 py-0.5 leading-5",
            line.startsWith("+") && !line.startsWith("+++")
              ? "bg-green-950 text-green-300"
              : line.startsWith("-") && !line.startsWith("---")
              ? "bg-red-950 text-red-300"
              : line.startsWith("@@")
              ? "text-blue-400"
              : line.startsWith("diff")
              ? "text-yellow-400 font-bold"
              : "text-gray-300"
          )}
        >
          {line || " "}
        </div>
      ))}
    </div>
  );
}

export default function DiffReview() {
  const { runId } = useParams<{ runId: string }>();
  const queryClient = useQueryClient();

  const { data: run, isLoading } = useQuery({
    queryKey: ["workflow-run", runId],
    queryFn: () => workflowApi.getRun(runId!),
    select: (r) => r.data,
    enabled: !!runId,
  });

  const advance = useMutation({
    mutationFn: (action: string) => workflowApi.advanceRun(runId!, action),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["workflow-run", runId] }),
  });

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
      </div>
    );
  }

  if (!run) {
    return <div className="p-8 text-gray-500">Workflow run not found.</div>;
  }

  const currentStepIndex = WORKFLOW_STEPS.indexOf(run.state);

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6 flex items-center gap-3">
        <Link to="/stories" className="text-gray-400 hover:text-gray-600">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            {run.jira_issue_key || "Workflow Run"}
          </h1>
          <p className="text-sm text-gray-500">
            {run.repository_name || run.repository_url} · {run.working_branch || run.target_branch}
          </p>
        </div>
        <span className="ml-auto badge bg-blue-100 text-blue-700 text-xs">
          {STATE_LABEL[run.state] ?? run.state}
        </span>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Progress tracker */}
        <div className="card lg:col-span-1">
          <h2 className="mb-4 text-sm font-semibold text-gray-900">Workflow Progress</h2>
          <ol className="space-y-2">
            {WORKFLOW_STEPS.map((step, i) => {
              const done = i < currentStepIndex;
              const active = i === currentStepIndex;
              return (
                <li key={step} className="flex items-center gap-3">
                  <div className={clsx(
                    "flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold",
                    done ? "bg-green-500 text-white"
                      : active ? "bg-primary-600 text-white ring-2 ring-primary-200"
                      : "bg-gray-100 text-gray-400"
                  )}>
                    {done ? "✓" : i + 1}
                  </div>
                  <span className={clsx(
                    "text-xs",
                    active ? "font-semibold text-primary-700" : done ? "text-gray-400" : "text-gray-500"
                  )}>
                    {STATE_LABEL[step]}
                  </span>
                </li>
              );
            })}
          </ol>
        </div>

        {/* Main panel */}
        <div className="space-y-6 lg:col-span-2">
          {/* Step actions */}
          <div className="card">
            <h2 className="mb-4 text-sm font-semibold text-gray-900">Actions</h2>
            <div className="flex flex-wrap gap-2">
              {run.state === "story_selected" && (
                <button
                  onClick={() => advance.mutate("analyze_story")}
                  disabled={advance.isPending}
                  className="btn-primary text-xs"
                >
                  <FileCode className="h-3.5 w-3.5" />
                  Analyze Story
                </button>
              )}
              {run.state === "plan_generated" && (
                <>
                  <button onClick={() => advance.mutate("approve_plan")} disabled={advance.isPending} className="btn-primary text-xs">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    Approve Plan
                  </button>
                  <button onClick={() => advance.mutate("request_rework")} disabled={advance.isPending} className="btn-danger text-xs">
                    <XCircle className="h-3.5 w-3.5" />
                    Request Rework
                  </button>
                </>
              )}
              {run.state === "changes_reviewed" && (
                <button onClick={() => advance.mutate("create_pr_draft")} disabled={advance.isPending} className="btn-primary text-xs">
                  <GitBranch className="h-3.5 w-3.5" />
                  Create PR Draft
                </button>
              )}
              {run.state === "review_approved" && (
                <button onClick={() => advance.mutate("request_deployment")} disabled={advance.isPending} className="btn-primary text-xs">
                  Request Deployment
                </button>
              )}
              {!run.is_terminal && (
                <button onClick={() => advance.mutate("close")} disabled={advance.isPending} className="btn-secondary text-xs ml-auto">
                  Cancel Run
                </button>
              )}
            </div>
          </div>

          {/* Diff viewer */}
          {["change_proposal_generated", "changes_reviewed", "pr_draft_created"].includes(run.state) && (
            <div className="card">
              <h2 className="mb-3 text-sm font-semibold text-gray-900">Proposed Changes</h2>
              <DiffViewer diff={MOCK_DIFF} />
            </div>
          )}

          {/* Context */}
          <div className="card">
            <h2 className="mb-3 text-sm font-semibold text-gray-900">Run Details</h2>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
              <dt className="text-gray-500">Session ID</dt>
              <dd className="font-mono text-xs text-gray-700">{run.session_id}</dd>
              <dt className="text-gray-500">Started</dt>
              <dd className="text-gray-700">{formatDistanceToNow(new Date(run.created_at), { addSuffix: true })}</dd>
              <dt className="text-gray-500">Initiated by</dt>
              <dd className="text-gray-700">{run.initiated_by_email}</dd>
              <dt className="text-gray-500">Working Branch</dt>
              <dd className="font-mono text-xs text-gray-700">{run.working_branch || "—"}</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}
