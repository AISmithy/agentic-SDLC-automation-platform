// ─── Auth / Users ────────────────────────────────────────────────────────────

export interface Role {
  id: string;
  name: string;
  role_type: "developer" | "reviewer" | "team_lead" | "admin" | "read_only";
  can_create_workflow: boolean;
  can_approve_plan: boolean;
  can_approve_pr: boolean;
  can_approve_deployment: boolean;
  can_publish_flow: boolean;
  can_manage_capabilities: boolean;
  can_view_audit: boolean;
}

export interface Team {
  id: string;
  name: string;
  slug: string;
  description: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  display_name: string;
  effective_display_name: string;
  role: Role | null;
  teams: Team[];
  is_active: boolean;
  preferences: Record<string, unknown>;
}

// ─── Workflows ───────────────────────────────────────────────────────────────

export type WorkflowState =
  | "session_created"
  | "story_selected"
  | "story_analyzed"
  | "plan_generated"
  | "plan_approved"
  | "repository_confirmed"
  | "branch_created"
  | "context_prepared"
  | "change_proposal_generated"
  | "changes_reviewed"
  | "pr_draft_created"
  | "review_pending"
  | "review_approved"
  | "deployment_pending"
  | "deployed_to_development"
  | "rework_required"
  | "closed"
  | "failed";

export interface WorkflowRun {
  id: string;
  session_id: string;
  template: string;
  template_version: string;
  initiated_by: string;
  initiated_by_email: string;
  team: string | null;
  state: WorkflowState;
  previous_state: string;
  jira_issue_key: string;
  jira_issue_data: Record<string, unknown>;
  repository_url: string;
  repository_name: string;
  target_branch: string;
  working_branch: string;
  context: Record<string, unknown>;
  error_message: string;
  retry_count: number;
  is_terminal: boolean;
  steps: WorkflowStepRun[];
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface WorkflowStepRun {
  id: string;
  step_id: string;
  run: string;
  step_type: string;
  step_name: string;
  node_id: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped" | "awaiting_approval";
  input_data: Record<string, unknown>;
  output_data: Record<string, unknown>;
  error_message: string;
  started_at: string | null;
  completed_at: string | null;
  duration_ms: number | null;
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  slug: string;
  owner: string;
  owner_email: string;
  team: string | null;
  publish_state: "draft" | "review" | "published" | "deprecated";
  is_system_template: boolean;
  allowed_roles: string[];
  active_version: WorkflowTemplateVersion | null;
  created_at: string;
  updated_at: string;
}

export interface WorkflowTemplateVersion {
  id: string;
  version_number: number;
  definition: FlowDefinition;
  is_valid: boolean;
  validation_errors: string[];
  is_active: boolean;
  created_at: string;
}

// ─── Flow Builder ────────────────────────────────────────────────────────────

export interface FlowNode {
  id: string;
  type: "trigger" | "agent" | "mcp_tool" | "approval" | "condition" | "notification" | "pr_action" | "deploy_action";
  position: { x: number; y: number };
  data: {
    label: string;
    config: Record<string, unknown>;
  };
}

export interface FlowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

export interface FlowDefinition {
  metadata: {
    name: string;
    description: string;
    version: string;
  };
  nodes: FlowNode[];
  edges: FlowEdge[];
}

// ─── Approvals ───────────────────────────────────────────────────────────────

export interface ApprovalRecord {
  id: string;
  run: string;
  action_type: string;
  status: "pending" | "approved" | "rejected" | "timed_out" | "cancelled";
  required_role: string;
  decided_by: string | null;
  decided_by_email: string | null;
  decision_notes: string;
  context_snapshot: Record<string, unknown>;
  created_at: string;
  expires_at: string | null;
  decided_at: string | null;
}

// ─── Pull Requests ───────────────────────────────────────────────────────────

export interface PullRequestRecord {
  id: string;
  run: string;
  external_pr_id: string;
  external_pr_number: number | null;
  repository_url: string;
  repository_name: string;
  source_branch: string;
  target_branch: string;
  pr_url: string;
  title: string;
  body: string;
  labels: string[];
  status: "draft" | "open" | "under_review" | "approved" | "merged" | "closed" | "declined";
  files_changed: number;
  lines_added: number;
  lines_removed: number;
  created_by_email: string;
  created_at: string;
  updated_at: string;
}

// ─── Deployments ─────────────────────────────────────────────────────────────

export interface DeploymentRecord {
  id: string;
  run: string;
  environment: "development";
  status: "pending" | "in_progress" | "success" | "failed" | "rolled_back" | "cancelled";
  external_pipeline_id: string;
  pipeline_url: string;
  commit_sha: string;
  deployed_by_email: string;
  error_message: string;
  deployment_log_url: string;
  started_at: string;
  completed_at: string | null;
  duration_seconds: number | null;
}

// ─── Audit ───────────────────────────────────────────────────────────────────

export interface AuditEvent {
  id: string;
  event_id: string;
  actor: string | null;
  actor_email: string;
  actor_role: string;
  category: "auth" | "workflow" | "agent" | "mcp_call" | "approval" | "pr" | "deployment" | "policy" | "admin";
  action: string;
  result: string;
  workflow_run: string | null;
  target_type: string;
  target_id: string;
  target_description: string;
  metadata: Record<string, unknown>;
  correlation_id: string;
  timestamp: string;
}

// ─── MCP ─────────────────────────────────────────────────────────────────────

export interface MCPCapability {
  id: string;
  capability_type: "tool" | "prompt" | "resource";
  name: string;
  description: string;
  access_level: "read_only" | "write_capable" | "approval_required" | "environment_sensitive";
  is_enabled: boolean;
  is_unknown_write: boolean;
  last_discovered_at: string;
}

// ─── API pagination ──────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
