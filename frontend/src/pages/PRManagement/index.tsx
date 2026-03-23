import { useQuery } from "@tanstack/react-query";
import { prApi } from "@/services/api";
import { GitPullRequest, ExternalLink, GitMerge, XCircle } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import type { PullRequestRecord } from "@/types";
import clsx from "clsx";

const STATUS_STYLES: Record<string, string> = {
  draft: "bg-gray-100 text-gray-600",
  open: "bg-blue-100 text-blue-700",
  under_review: "bg-yellow-100 text-yellow-700",
  approved: "bg-green-100 text-green-700",
  merged: "bg-purple-100 text-purple-700",
  closed: "bg-gray-100 text-gray-500",
  declined: "bg-red-100 text-red-700",
};

function PRCard({ pr }: { pr: PullRequestRecord }) {
  return (
    <div className="card hover:border-primary-300 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <GitPullRequest className="mt-0.5 h-5 w-5 shrink-0 text-primary-500" />
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">
                #{pr.external_pr_number ?? "draft"}
              </span>
              <span className={clsx("badge", STATUS_STYLES[pr.status])}>
                {pr.status.replace(/_/g, " ")}
              </span>
            </div>
            <h3 className="mt-0.5 font-medium text-gray-900 leading-snug">
              {pr.title}
            </h3>
            <p className="text-xs text-gray-500 mt-1">
              {pr.repository_name} ·{" "}
              <span className="font-mono">{pr.source_branch}</span> →{" "}
              <span className="font-mono">{pr.target_branch}</span>
            </p>
          </div>
        </div>

        {pr.pr_url && (
          <a
            href={pr.pr_url}
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 text-gray-400 hover:text-primary-600"
          >
            <ExternalLink className="h-4 w-4" />
          </a>
        )}
      </div>

      <div className="mt-3 flex items-center gap-4 text-xs text-gray-400">
        <span className="flex items-center gap-1">
          <span className="text-green-600 font-mono">+{pr.lines_added}</span>
          <span className="text-red-600 font-mono">-{pr.lines_removed}</span>
          <span>{pr.files_changed} file{pr.files_changed !== 1 ? "s" : ""}</span>
        </span>
        <span>by {pr.created_by_email}</span>
        <span className="ml-auto">
          {formatDistanceToNow(new Date(pr.created_at), { addSuffix: true })}
        </span>
      </div>
    </div>
  );
}

export default function PRManagement() {
  const { data, isLoading } = useQuery({
    queryKey: ["pull-requests"],
    queryFn: () => prApi.list(),
    select: (r) => r.data,
  });

  const openPRs = data?.results.filter((p) => ["open", "under_review"].includes(p.status)) ?? [];
  const otherPRs = data?.results.filter((p) => !["open", "under_review"].includes(p.status)) ?? [];

  return (
    <div className="p-8">
      <div className="mb-8 flex items-center gap-3">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <GitPullRequest className="h-6 w-6 text-primary-600" />
          Pull Requests
        </h1>
        <span className="badge bg-blue-100 text-blue-700">{data?.count ?? 0} total</span>
      </div>

      {isLoading ? (
        <div className="text-gray-400 text-sm">Loading…</div>
      ) : data?.results.length === 0 ? (
        <div className="card flex flex-col items-center py-16 text-gray-400">
          <GitMerge className="mb-2 h-8 w-8" />
          <p className="text-sm">No pull requests yet.</p>
        </div>
      ) : (
        <div className="space-y-8">
          {openPRs.length > 0 && (
            <section>
              <h2 className="mb-3 text-sm font-semibold text-gray-700">Open / Under Review</h2>
              <div className="space-y-3">
                {openPRs.map((pr) => <PRCard key={pr.id} pr={pr} />)}
              </div>
            </section>
          )}
          {otherPRs.length > 0 && (
            <section>
              <h2 className="mb-3 text-sm font-semibold text-gray-700">Closed / Merged</h2>
              <div className="space-y-3">
                {otherPRs.map((pr) => <PRCard key={pr.id} pr={pr} />)}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
