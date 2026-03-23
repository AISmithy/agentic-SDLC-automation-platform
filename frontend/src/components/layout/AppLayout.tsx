import { Outlet, NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, BookOpen, GitPullRequest, Rocket,
  ScrollText, Settings, LogOut, Workflow, Eye,
} from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import clsx from "clsx";

const NAV_ITEMS = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/stories", icon: BookOpen, label: "Story Intake" },
  { to: "/flow-builder", icon: Workflow, label: "Flow Builder" },
  { to: "/pull-requests", icon: GitPullRequest, label: "Pull Requests" },
  { to: "/deployments", icon: Rocket, label: "Deployments" },
  { to: "/audit", icon: ScrollText, label: "Audit Log" },
];

export default function AppLayout() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Sidebar */}
      <aside className="flex w-64 flex-col bg-primary-900 text-white">
        {/* Logo */}
        <div className="flex h-16 items-center gap-3 px-6 border-b border-primary-700">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary-500">
            <Eye className="h-4 w-4 text-white" />
          </div>
          <div>
            <p className="text-sm font-bold leading-tight">Agentic SDLC</p>
            <p className="text-xs text-primary-300">Platform</p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto py-4 px-3">
          <ul className="space-y-1">
            {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  className={({ isActive }) =>
                    clsx(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-primary-700 text-white"
                        : "text-primary-200 hover:bg-primary-800 hover:text-white"
                    )
                  }
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  {label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* User footer */}
        <div className="border-t border-primary-700 p-4">
          <div className="mb-3 flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-600 text-xs font-semibold">
              {user?.effective_display_name?.[0]?.toUpperCase() ?? "?"}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-white">
                {user?.effective_display_name ?? "Loading..."}
              </p>
              <p className="truncate text-xs text-primary-300">
                {user?.role?.name ?? "—"}
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-primary-200 hover:bg-primary-800 hover:text-white transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
