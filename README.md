# Agentic SDLC Automation Platform

> **Governed, human-in-the-loop software delivery automation** — React + Django + LangChain + MCP

[![Architecture](https://img.shields.io/badge/arch-v1.0-blue)](#architecture)
[![Stack](https://img.shields.io/badge/stack-React%20%2B%20Django%20%2B%20LangChain-blueviolet)](#technology-stack)

---

## Overview

The Agentic SDLC Automation Platform enables software teams to design and execute agent-driven delivery workflows across:

- **Jira** story intake and analysis
- **GitHub** branch creation, code proposals, and pull request management
- **Code generation** via bounded LangChain agents
- **Human-in-the-loop** review, diff inspection, and approval gates
- **Deployment** to development environments via MCP-mediated CI/CD

All high-impact actions pass through policy-enforced approval gates. No agent or the frontend ever directly calls external tools — all external execution is mediated by the Django backend and MCP client.

---

## Architecture

```
[ React UI ]
     │
     ▼
[ Django REST API ]         ← Authentication, RBAC, validation
     │
     ▼
[ Workflow Engine ]         ← State machine, policy enforcement
     │
     ▼
[ LangChain Orchestrator ]  ← Bounded agents, structured outputs
     │
     ▼
[ MCP Client ]              ← Capability registry, audit trace
     │
     ▼
[ MCP Server ]              ← Jira · GitHub · CI/CD · Deploy
```

### Six Architectural Layers

| Layer | Technology | Responsibility |
|-------|-----------|---------------|
| User Interaction | React + Vite + TailwindCSS | Dashboard, Flow Builder, Diff Review, Audit Timeline |
| Application & API | Django + DRF | Auth, routing, RBAC, state management |
| Orchestration & Agents | LangChain | Bounded agent execution, structured outputs |
| Governance & Policy | Django service layer | Approval gates, tool authorization, audit |
| Integration | MCP client + capability registry | Tool/prompt/resource discovery and invocation |
| Data & Persistence | H2/SQLite → PostgreSQL | Users, sessions, runs, approvals, audit events |

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React 18, Vite, TypeScript, TailwindCSS, TanStack Query, ReactFlow, Zustand |
| Backend | Python 3.12, Django 4.2, Django REST Framework |
| Agents | LangChain 0.3, LangChain-Anthropic, Pydantic v2 |
| MCP | `mcp` Python SDK, Anthropic API |
| Workers | Celery 5, Redis |
| Database | SQLite (dev / H2-equivalent) → PostgreSQL (production) |
| Container | Docker, Docker Compose, Nginx |

---

## Project Structure

```
agentic-SDLC-automation-platform/
├── backend/
│   ├── config/                  # Django settings, URLs, Celery, middleware
│   │   ├── settings/
│   │   │   ├── base.py          # Shared settings
│   │   │   ├── development.py   # Local dev (SQLite)
│   │   │   └── production.py    # Production (PostgreSQL, security headers)
│   │   ├── celery.py
│   │   ├── middleware.py        # Correlation ID middleware
│   │   └── exceptions.py       # Structured error responses
│   ├── apps/
│   │   ├── accounts/            # User, Role, Team models + auth API
│   │   ├── workflows/           # WorkflowTemplate, WorkflowRun, state machine engine
│   │   ├── agents/              # AgentRun models, LangChain orchestrator, agent registry
│   │   ├── mcp_client/          # MCPCapability, MCPToolCall, client, discovery service
│   │   ├── approvals/           # ApprovalRecord, approval decision API
│   │   ├── pull_requests/       # PullRequestRecord
│   │   ├── deployments/         # DeploymentRecord
│   │   └── audit/               # AuditEvent (append-only)
│   ├── workers/
│   │   └── tasks.py             # Celery tasks: agent execution, MCP polling, approval expiry
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard/       # Workflow summary, stats, pending approvals
│   │   │   ├── StoryIntake/     # Start workflow, approval decisions
│   │   │   ├── FlowBuilder/     # ReactFlow canvas-based workflow designer
│   │   │   ├── DiffReview/      # Diff viewer, workflow step actions
│   │   │   ├── PRManagement/    # Pull request list and status
│   │   │   ├── DeploymentConsole/ # Live deployment status with auto-refresh
│   │   │   └── AuditTimeline/   # Filterable audit event log
│   │   ├── services/api.ts      # Typed Axios API client with JWT refresh
│   │   ├── store/authStore.ts   # Zustand auth state (persisted)
│   │   ├── types/index.ts       # TypeScript domain types
│   │   └── components/layout/   # AppLayout with sidebar navigation
│   ├── Dockerfile
│   └── package.json
├── nginx/nginx.conf             # Reverse proxy: frontend + /api → backend
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Workflow State Machine

Each workflow session traverses these states, enforced by `WorkflowEngine`:

```
Session Created → Story Selected → Story Analyzed → Plan Generated
  → Plan Approved* → Repository Confirmed → Branch Created* → Context Prepared
  → Change Proposal Generated → Changes Reviewed → PR Draft Created*
  → Review Pending → Review Approved → Deployment Pending → Deployed to Development
                                    ↕
                              Rework Required
```

`*` = requires an approved `ApprovalRecord` before transition is allowed.

---

## Key Domain Rules

- **Backend mediation**: The browser never holds privileged credentials for Jira, GitHub, or MCP write actions.
- **Bounded agents**: LangChain agents only receive tools explicitly injected per workflow step and user role.
- **Immutable audit**: `AuditEvent` records cannot be updated — enforced at the model layer.
- **Unknown write tools disabled**: Any newly discovered write-capable MCP tool is disabled by default until explicitly enabled.
- **Structured outputs**: All agent outputs are validated against Pydantic schemas before being persisted.

---

## Getting Started

### Local development (SQLite / no Docker)

```bash
# 1. Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp ../.env.example ../.env                          # fill in ANTHROPIC_API_KEY etc.
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# 2. Worker (separate terminal)
celery -A config worker --loglevel=info

# 3. Frontend (separate terminal)
cd ../frontend
npm install
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173) for the React app.
API docs: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

### Docker Compose (full stack)

```bash
cp .env.example .env    # edit with your secrets
docker compose up --build
```

Nginx will be available at [http://localhost:80](http://localhost:80).

---

## API Groups

| Group | Prefix | Description |
|-------|--------|-------------|
| Auth | `/api/v1/auth/` | JWT obtain, refresh, verify |
| Users | `/api/v1/users/` | Users, roles, teams, `/me` |
| Workflows | `/api/v1/workflows/` | Templates, runs, step transitions |
| Agents | `/api/v1/agents/` | Agent run records, execute endpoint |
| MCP | `/api/v1/mcp/` | Capability registry, sync, tool call audit |
| Approvals | `/api/v1/approvals/` | Approval records, decision endpoint |
| Pull Requests | `/api/v1/pull-requests/` | PR records |
| Deployments | `/api/v1/deployments/` | Deployment records |
| Audit | `/api/v1/audit/` | Read-only audit event log |

Interactive Swagger UI: `/api/docs/`

---

## Environment Variables

See [`.env.example`](.env.example) for all variables. Key ones:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude agents |
| `MCP_SERVER_URL` | URL of your enterprise MCP server |
| `MCP_SERVER_TOKEN` | Auth token for MCP server |
| `DB_*` | Database connection (omit for SQLite dev) |
| `CELERY_BROKER_URL` | Redis URL for Celery |

---

## Phased Rollout

| Phase | Scope |
|-------|-------|
| **Phase 1 (current)** | Development environment only. Story intake → code → PR → deploy to dev |
| **Phase 2** | QA / staging environment promotion, multi-team support |
| **Phase 3** | Vector retrieval for code context, advanced analytics, dry-run mode |

---

## Security Notes

- Enterprise SSO is the target authentication path (JWT in dev)
- All secrets are server-side only — frontend never sees API keys
- Prompt injection: story text and repo content are treated as untrusted input
- Audit events are append-only and correlation-ID tagged end-to-end
