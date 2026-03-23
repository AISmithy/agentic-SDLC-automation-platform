import { useQuery } from "@tanstack/react-query";
import { deploymentsApi } from "@/services/api";
import { Rocket, CheckCircle2, XCircle, Clock, ExternalLink, RefreshCw } from "lucide-react";
import { formatDistanceToNow, format } from "date-fns";
import type { DeploymentRecord } from "@/types";
import clsx from "clsx";

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ElementType }> = {
  pending: { label: "Pending", color: "bg-gray-100 text-gray-600", icon: Clock },
  in_progress: { label: "In Progress", color: "bg-blue-100 text-blue-700", icon: RefreshCw },
  success: { label: "Success", color: "bg-green-100 text-green-700", icon: CheckCircle2 },
  failed: { label: "Failed", color: "bg-red-100 text-red-700", icon: XCircle },
  rolled_back: { label: "Rolled Back", color: "bg-orange-100 text-orange-700", icon: XCircle },
  cancelled: { label: "Cancelled", color: "bg-gray-100 text-gray-500", icon: XCircle },
};

function DeploymentRow({ d }: { d: DeploymentRecord }) {
  const cfg = STATUS_CONFIG[d.status] ?? STATUS_CONFIG.pending;
  const Icon = cfg.icon;

  return (
    <tr className="hover:bg-gray-50 text-sm">
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <Icon className={clsx("h-4 w-4", d.status === "in_progress" && "animate-spin")} />
          <span className={clsx("badge", cfg.color)}>{cfg.label}</span>
        </div>
      </td>
      <td className="px-4 py-3 text-gray-700 font-medium">{d.environment}</td>
      <td className="px-4 py-3 text-gray-500">{d.deployed_by_email}</td>
      <td className="px-4 py-3">
        {d.commit_sha ? (
          <span className="font-mono text-xs text-gray-600">{d.commit_sha.slice(0, 8)}</span>
        ) : "—"}
      </td>
      <td className="px-4 py-3 text-gray-500">
        {d.duration_seconds != null ? `${d.duration_seconds}s` : "—"}
      </td>
      <td className="px-4 py-3 text-gray-400 text-xs">
        {formatDistanceToNow(new Date(d.started_at), { addSuffix: true })}
      </td>
      <td className="px-4 py-3">
        <div className="flex gap-2">
          {d.pipeline_url && (
            <a href={d.pipeline_url} target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-primary-600">
              <ExternalLink className="h-4 w-4" />
            </a>
          )}
          {d.deployment_log_url && (
            <a href={d.deployment_log_url} target="_blank" rel="noopener noreferrer" className="text-xs text-primary-600 hover:underline">
              Logs
            </a>
          )}
        </div>
      </td>
    </tr>
  );
}

export default function DeploymentConsole() {
  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["deployments"],
    queryFn: () => deploymentsApi.list({ ordering: "-started_at" }),
    select: (r) => r.data,
    refetchInterval: 15_000, // poll every 15s for live status
  });

  const inProgress = data?.results.filter((d) => d.status === "in_progress").length ?? 0;
  const successes = data?.results.filter((d) => d.status === "success").length ?? 0;
  const failures = data?.results.filter((d) => d.status === "failed").length ?? 0;

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center gap-3">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Rocket className="h-6 w-6 text-primary-600" />
          Deployment Console
        </h1>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="btn-secondary ml-auto text-xs"
        >
          <RefreshCw className={clsx("h-3.5 w-3.5", isFetching && "animate-spin")} />
          Refresh
        </button>
      </div>

      {/* Summary stats */}
      <div className="mb-6 grid grid-cols-3 gap-4">
        <div className="card flex items-center gap-3">
          <RefreshCw className="h-5 w-5 text-blue-500" />
          <div>
            <p className="text-xl font-bold">{inProgress}</p>
            <p className="text-xs text-gray-500">In Progress</p>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <CheckCircle2 className="h-5 w-5 text-green-500" />
          <div>
            <p className="text-xl font-bold">{successes}</p>
            <p className="text-xs text-gray-500">Successful</p>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <XCircle className="h-5 w-5 text-red-500" />
          <div>
            <p className="text-xl font-bold">{failures}</p>
            <p className="text-xs text-gray-500">Failed</p>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden p-0">
        <div className="border-b px-4 py-3">
          <h2 className="font-semibold text-gray-900 text-sm">Deployment History (Development)</h2>
        </div>
        {isLoading ? (
          <div className="py-10 text-center text-gray-400 text-sm">Loading…</div>
        ) : data?.results.length === 0 ? (
          <div className="flex flex-col items-center py-16 text-gray-400">
            <Rocket className="mb-2 h-8 w-8" />
            <p className="text-sm">No deployments yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-gray-50 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                  <th className="px-4 py-2">Status</th>
                  <th className="px-4 py-2">Environment</th>
                  <th className="px-4 py-2">Deployed By</th>
                  <th className="px-4 py-2">Commit</th>
                  <th className="px-4 py-2">Duration</th>
                  <th className="px-4 py-2">Started</th>
                  <th className="px-4 py-2">Links</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {data?.results.map((d) => <DeploymentRow key={d.id} d={d} />)}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
