import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { workflowApi, approvalsApi } from "@/services/api";
import { useNavigate } from "react-router-dom";
import { BookOpen, Play, Clock, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import type { WorkflowTemplate, ApprovalRecord } from "@/types";
import clsx from "clsx";

function ApprovalCard({ approval }: { approval: ApprovalRecord }) {
  const queryClient = useQueryClient();
  const decide = useMutation({
    mutationFn: ({ decision, notes }: { decision: "approved" | "rejected"; notes?: string }) =>
      approvalsApi.decide(approval.id, decision, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["approvals"] });
      queryClient.invalidateQueries({ queryKey: ["workflow-runs"] });
    },
  });

  return (
    <div className="card border-l-4 border-l-amber-400">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-medium text-gray-900">
            {approval.action_type.replace(/_/g, " ")}
          </p>
          <p className="text-sm text-gray-500">Run: {approval.run}</p>
          <p className="mt-1 text-xs text-gray-400">
            Requested {formatDistanceToNow(new Date(approval.created_at), { addSuffix: true })}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => decide.mutate({ decision: "approved" })}
            disabled={decide.isPending}
            className="btn-primary text-xs"
          >
            <CheckCircle2 className="h-3.5 w-3.5" />
            Approve
          </button>
          <button
            onClick={() => decide.mutate({ decision: "rejected" })}
            disabled={decide.isPending}
            className="btn-danger text-xs"
          >
            <XCircle className="h-3.5 w-3.5" />
            Reject
          </button>
        </div>
      </div>
    </div>
  );
}

function NewRunForm({ templates }: { templates: WorkflowTemplate[] }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [templateId, setTemplateId] = useState("");
  const [jiraKey, setJiraKey] = useState("");
  const [repoUrl, setRepoUrl] = useState("");

  const createRun = useMutation({
    mutationFn: () =>
      workflowApi.createRun({ template: templateId, jira_issue_key: jiraKey, repository_url: repoUrl }),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ["workflow-runs"] });
      navigate(`/runs/${res.data.id}/review`);
    },
  });

  return (
    <div className="card">
      <h2 className="mb-4 font-semibold text-gray-900">Start New Workflow Run</h2>
      <form
        onSubmit={(e) => { e.preventDefault(); createRun.mutate(); }}
        className="space-y-4"
      >
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Workflow Template</label>
          <select
            value={templateId}
            onChange={(e) => setTemplateId(e.target.value)}
            required
            className="w-full rounded-md border px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          >
            <option value="">Select a template…</option>
            {templates.map((t) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Jira Issue Key</label>
          <input
            type="text"
            value={jiraKey}
            onChange={(e) => setJiraKey(e.target.value)}
            required
            placeholder="PROJ-123"
            className="w-full rounded-md border px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Repository URL</label>
          <input
            type="url"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            required
            placeholder="https://github.com/org/repo"
            className="w-full rounded-md border px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>

        {createRun.isError && (
          <p className="text-sm text-red-600">Failed to create run. Please try again.</p>
        )}

        <button type="submit" disabled={createRun.isPending} className="btn-primary w-full">
          {createRun.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          {createRun.isPending ? "Starting..." : "Start Workflow"}
        </button>
      </form>
    </div>
  );
}

export default function StoryIntake() {
  const { data: templatesData } = useQuery({
    queryKey: ["workflow-templates"],
    queryFn: () => workflowApi.listTemplates(),
    select: (r) => r.data,
  });

  const { data: approvalsData } = useQuery({
    queryKey: ["approvals", "pending"],
    queryFn: () => approvalsApi.listPending(),
    select: (r) => r.data,
  });

  const publishedTemplates = templatesData?.results.filter(
    (t) => t.publish_state === "published" || t.is_system_template
  ) ?? [];

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <BookOpen className="h-6 w-6 text-primary-600" />
          Story Intake
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Start a new workflow or review pending approvals.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* New run form */}
        <div>
          <NewRunForm templates={publishedTemplates} />
        </div>

        {/* Pending approvals */}
        <div>
          <div className="mb-4 flex items-center gap-2">
            <Clock className="h-4 w-4 text-amber-500" />
            <h2 className="font-semibold text-gray-900">
              Pending Approvals
              {(approvalsData?.count ?? 0) > 0 && (
                <span className="ml-2 badge bg-amber-100 text-amber-700">
                  {approvalsData!.count}
                </span>
              )}
            </h2>
          </div>

          {approvalsData?.results.length ? (
            <div className="space-y-3">
              {approvalsData.results.map((a) => (
                <ApprovalCard key={a.id} approval={a} />
              ))}
            </div>
          ) : (
            <div className="card flex flex-col items-center py-10 text-gray-400">
              <CheckCircle2 className="mb-2 h-8 w-8 text-green-400" />
              <p className="text-sm">No pending approvals.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
