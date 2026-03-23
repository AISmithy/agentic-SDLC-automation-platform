import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import AppLayout from "@/components/layout/AppLayout";
import LoginPage from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import StoryIntake from "@/pages/StoryIntake";
import FlowBuilder from "@/pages/FlowBuilder";
import DiffReview from "@/pages/DiffReview";
import PRManagement from "@/pages/PRManagement";
import DeploymentConsole from "@/pages/DeploymentConsole";
import AuditTimeline from "@/pages/AuditTimeline";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="stories" element={<StoryIntake />} />
          <Route path="flow-builder" element={<FlowBuilder />} />
          <Route path="flow-builder/:templateId" element={<FlowBuilder />} />
          <Route path="runs/:runId/review" element={<DiffReview />} />
          <Route path="pull-requests" element={<PRManagement />} />
          <Route path="deployments" element={<DeploymentConsole />} />
          <Route path="audit" element={<AuditTimeline />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
