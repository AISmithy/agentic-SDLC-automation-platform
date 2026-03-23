import { useQuery } from "@tanstack/react-query";
import { auditApi } from "@/services/api";
import { ScrollText, Activity, Shield, GitPullRequest, Rocket, CheckCircle2, Bot } from "lucide-react";
import { format } from "date-fns";
import type { AuditEvent } from "@/types";
import clsx from "clsx";

const CATEGORY_CONFIG: Record<string, { icon: React.ElementType; color: string }> = {
  auth: { icon: Shield, color: "text-blue-500 bg-blue-50" },
  workflow: { icon: Activity, color: "text-purple-500 bg-purple-50" },
  agent: { icon: Bot, color: "text-indigo-500 bg-indigo-50" },
  mcp_call: { icon: Activity, color: "text-teal-500 bg-teal-50" },
  approval: { icon: CheckCircle2, color: "text-amber-500 bg-amber-50" },
  pr: { icon: GitPullRequest, color: "text-green-500 bg-green-50" },
  deployment: { icon: Rocket, color: "text-orange-500 bg-orange-50" },
  policy: { icon: Shield, color: "text-red-500 bg-red-50" },
  admin: { icon: Shield, color: "text-gray-500 bg-gray-100" },
};

function EventItem({ event }: { event: AuditEvent }) {
  const cfg = CATEGORY_CONFIG[event.category] ?? CATEGORY_CONFIG.admin;
  const Icon = cfg.icon;
  const success = event.result === "success";

  return (
    <div className="flex gap-4">
      {/* Icon */}
      <div className={clsx("mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full", cfg.color)}>
        <Icon className="h-4 w-4" />
      </div>

      {/* Content */}
      <div className="flex-1 border-b pb-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-gray-900">
              {event.action}
              <span className={clsx(
                "ml-2 badge text-xs",
                success ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
              )}>
                {event.result}
              </span>
            </p>
            <p className="text-xs text-gray-500 mt-0.5">
              {event.actor_email || "system"} · {event.target_description || event.target_type}
            </p>
          </div>
          <time className="shrink-0 text-xs text-gray-400">
            {format(new Date(event.timestamp), "MMM d, HH:mm:ss")}
          </time>
        </div>

        {event.correlation_id && (
          <p className="mt-1 font-mono text-xs text-gray-300 truncate">
            {event.correlation_id}
          </p>
        )}
      </div>
    </div>
  );
}

export default function AuditTimeline() {
  const [category, setCategory] = React.useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["audit-events", category],
    queryFn: () => auditApi.list(category ? { category } : undefined),
    select: (r) => r.data,
  });

  const categories = ["", "workflow", "agent", "mcp_call", "approval", "pr", "deployment", "auth", "admin"];

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center gap-3">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <ScrollText className="h-6 w-6 text-primary-600" />
          Audit Timeline
        </h1>
        <span className="badge bg-gray-100 text-gray-600">{data?.count ?? 0} events</span>

        {/* Category filter */}
        <div className="ml-auto flex gap-1 flex-wrap">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={clsx(
                "badge cursor-pointer transition-colors",
                category === cat
                  ? "bg-primary-600 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              )}
            >
              {cat || "All"}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        {isLoading ? (
          <div className="py-10 text-center text-gray-400 text-sm">Loading audit events…</div>
        ) : data?.results.length === 0 ? (
          <div className="flex flex-col items-center py-16 text-gray-400">
            <ScrollText className="mb-2 h-8 w-8" />
            <p className="text-sm">No audit events found.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {data?.results.map((event) => (
              <EventItem key={event.id} event={event} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// React must be imported for useState
import React from "react";
