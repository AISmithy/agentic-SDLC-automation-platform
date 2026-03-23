import { useQuery } from "@tanstack/react-query";
import { workflowApi, approvalsApi, deploymentsApi } from "@/services/api";
import { useAuthStore } from "@/store/authStore";
import { Link } from "react-router-dom";
import {
  Activity, GitPullRequest, Rocket, Clock,
  CheckCircle2, XCircle, AlertTriangle, ArrowRight,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import type { WorkflowRun, WorkflowState } from "@/types";
import clsx from "clsx";

const STATE_COLORS: Record<string, string> = {
  session_created: "bg-gray-100 text-gray-700",
  story_selected: "bg-blue-100 text-blue-700",
  story_analyzed: "bg-blue-100 text-blue-700",
  plan_generated: "bg-purple-100 text-purple-700",
  plan_approved: "bg-purple-100 text-purple-700",
  repository_confirmed: "bg-indigo-100 text-indigo-700",
  branch_created: "bg-indigo-100 text-indigo-700",
  context_prepared: "bg-yellow-100 text-yellow-700",
  change_proposal_generated: "bg-yellow-100 text-yellow-700",
  changes_reviewed: "bg-orange-100 text-orange-700",
  pr_draft_created: "bg-orange-100 text-orange-700",
  review_pending: "bg-amber-100 text-amber-700",
  review_approved: "bg-green-100 text-green-700",
  deployment_pending: "bg-teal-100 text-teal-700",
  deployed_to_development: "bg-green-100 text-green-700",
  rework_required: "bg-red-100 text-red-700",
  closed: "bg-gray-100 text-gray-500",
  failed: "bg-red-100 text-red-700",
};

function StatCard({ label, value, icon: Icon, color }: {
  label: string; value: number | string; icon: React.ElementType; color: string;
}) {
  return (
    <div className="card flex items-center gap-4">
      <div className={clsx("flex h-12 w-12 items-center justify-center rounded-xl", color)}>
        <Icon className="h-6 w-6" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500">{label}</p>
      </div>
    </div>
  );
}

function RunRow({ run }: { run: WorkflowRun }) {
  return (
    <tr className="hover:bg-gray-50">
      <td className="px-4 py-3">
        <Link
          to={`/runs/${run.id}/review`}
          className="font-medium text-primary-600 hover:underline"
        >
          {run.jira_issue_key || run.session_id.slice(0, 8)}
        </Link>
        <p className="text-xs text-gray-400 truncate max-w-xs">
          {run.repository_name || "—"}
        </p>
      </td>
      <td className="px-4 py-3">
        <span className={clsx("badge", STATE_COLORS[run.state] ?? "bg-gray-100 text-gray-600")}>
          {run.state.replace(/_/g, " ")}
        </span>
      </td>
      <td className="px-4 py-3 text-sm text-gray-500">
        {formatDistanceToNow(new Date(run.created_at), { addSuffix: true })}
      </td>
      <td className="px-4 py-3 text-sm text-gray-500">
        {run.initiated_by_email}
      </td>
      <td className="px-4 py-3">
        <Link to={`/runs/${run.id}/review`} className="text-gray-400 hover:text-primary-600">
          <ArrowRight className="h-4 w-4" />
        </Link>
      </td>
    </tr>
  );
}

export default function Dashboard() {
  const user = useAuthStore((s) => s.user);

  const { data: runsData } = useQuery({
    queryKey: ["workflow-runs"],
    queryFn: () => workflowApi.listRuns({ page_size: "10" }),
    select: (r) => r.data,
  });

  const { data: approvalsData } = useQuery({
    queryKey: ["approvals", "pending"],
    queryFn: () => approvalsApi.listPending(),
    select: (r) => r.data,
  });

  const { data: deploymentsData } = useQuery({
    queryKey: ["deployments"],
    queryFn: () => deploymentsApi.list({ page_size: "5" }),
    select: (r) => r.data,
  });

  const activeRuns = runsData?.results.filter((r) => !r.is_terminal).length ?? 0;
  const pendingApprovals = approvalsData?.count ?? 0;
  const totalDeployments = deploymentsData?.count ?? 0;
  const successfulDeployments = deploymentsData?.results.filter(
    (d) => d.status === "success"
  ).length ?? 0;

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.effective_display_name} 👋
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Here's what's happening across your SDLC workflows.
        </p>
      </div>

      {/* Stats */}
      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Active Runs"
          value={activeRuns}
          icon={Activity}
          color="bg-blue-50 text-blue-600"
        />
        <StatCard
          label="Pending Approvals"
          value={pendingApprovals}
          icon={Clock}
          color={pendingApprovals > 0 ? "bg-amber-50 text-amber-600" : "bg-gray-50 text-gray-500"}
        />
        <StatCard
          label="Deployments"
          value={totalDeployments}
          icon={Rocket}
          color="bg-teal-50 text-teal-600"
        />
        <StatCard
          label="Successful Deploys"
          value={successfulDeployments}
          icon={CheckCircle2}
          color="bg-green-50 text-green-600"
        />
      </div>

      {/* Pending Approvals Alert */}
      {pendingApprovals > 0 && (
        <div className="mb-6 flex items-center gap-3 rounded-lg border border-amber-200 bg-amber-50 p-4">
          <AlertTriangle className="h-5 w-5 shrink-0 text-amber-600" />
          <p className="text-sm text-amber-800">
            You have <strong>{pendingApprovals}</strong> pending approval{pendingApprovals !== 1 ? "s" : ""} that require your attention.
          </p>
          <Link to="/stories" className="ml-auto btn-secondary text-xs">
            Review
          </Link>
        </div>
      )}

      {/* Recent Runs */}
      <div className="card overflow-hidden p-0">
        <div className="flex items-center justify-between border-b px-4 py-3">
          <h2 className="font-semibold text-gray-900">Recent Workflow Runs</h2>
          <Link to="/stories" className="text-sm text-primary-600 hover:underline">
            View all
          </Link>
        </div>
        {runsData?.results.length ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-gray-50 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                  <th className="px-4 py-2">Story / Run</th>
                  <th className="px-4 py-2">State</th>
                  <th className="px-4 py-2">Started</th>
                  <th className="px-4 py-2">Initiated By</th>
                  <th className="px-4 py-2"></th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {runsData.results.map((run) => (
                  <RunRow key={run.id} run={run} />
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-gray-400">
            <Activity className="mb-2 h-8 w-8" />
            <p className="text-sm">No workflow runs yet.</p>
            <Link to="/stories" className="btn-primary mt-3 text-xs">
              Start a workflow
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
