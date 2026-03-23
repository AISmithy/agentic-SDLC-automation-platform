/**
 * Axios API client — all requests go through Django backend.
 * JWT tokens are attached automatically. Never sends privileged
 * credentials directly to external services (MCP, Jira, GitHub).
 */

import axios, { AxiosError } from "axios";
import type {
  User,
  WorkflowRun,
  WorkflowTemplate,
  ApprovalRecord,
  PullRequestRecord,
  DeploymentRecord,
  AuditEvent,
  MCPCapability,
  PaginatedResponse,
} from "@/types";

const BASE_URL = "/api/v1";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT from localStorage
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Refresh token on 401
apiClient.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      const refresh = localStorage.getItem("refresh_token");
      if (refresh) {
        try {
          const { data } = await axios.post(`${BASE_URL}/auth/token/refresh/`, { refresh });
          localStorage.setItem("access_token", data.access);
          error.config!.headers!.Authorization = `Bearer ${data.access}`;
          return apiClient(error.config!);
        } catch {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post<{ access: string; refresh: string }>("/auth/token/", { email, password }),
  me: () => apiClient.get<User>("/users/me/"),
};

// ─── Workflow Runs ────────────────────────────────────────────────────────────
export const workflowApi = {
  listRuns: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<WorkflowRun>>("/workflows/runs/", { params }),

  getRun: (id: string) =>
    apiClient.get<WorkflowRun>(`/workflows/runs/${id}/`),

  createRun: (payload: { template: string; jira_issue_key: string; repository_url: string; team?: string }) =>
    apiClient.post<WorkflowRun>("/workflows/runs/", payload),

  advanceRun: (id: string, action: string, payload?: Record<string, unknown>) =>
    apiClient.post<WorkflowRun>(`/workflows/runs/${id}/advance/`, { action, payload }),

  cancelRun: (id: string) =>
    apiClient.post<{ detail: string }>(`/workflows/runs/${id}/cancel/`),

  listTemplates: () =>
    apiClient.get<PaginatedResponse<WorkflowTemplate>>("/workflows/templates/"),
};

// ─── Approvals ────────────────────────────────────────────────────────────────
export const approvalsApi = {
  listPending: () =>
    apiClient.get<PaginatedResponse<ApprovalRecord>>("/approvals/?status=pending"),

  decide: (id: string, decision: "approved" | "rejected", notes?: string) =>
    apiClient.post<ApprovalRecord>(`/approvals/${id}/decide/`, { decision, notes }),
};

// ─── Pull Requests ────────────────────────────────────────────────────────────
export const prApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<PullRequestRecord>>("/pull-requests/", { params }),

  get: (id: string) =>
    apiClient.get<PullRequestRecord>(`/pull-requests/${id}/`),
};

// ─── Deployments ──────────────────────────────────────────────────────────────
export const deploymentsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<DeploymentRecord>>("/deployments/", { params }),
};

// ─── Audit ────────────────────────────────────────────────────────────────────
export const auditApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<AuditEvent>>("/audit/", { params }),
};

// ─── MCP Capabilities ─────────────────────────────────────────────────────────
export const mcpApi = {
  listCapabilities: () =>
    apiClient.get<PaginatedResponse<MCPCapability>>("/mcp/capabilities/"),

  syncCapabilities: () =>
    apiClient.post<{ created: number; updated: number }>("/mcp/capabilities/sync/"),

  toggleCapability: (id: string) =>
    apiClient.post<{ is_enabled: boolean }>(`/mcp/capabilities/${id}/toggle/`),
};
