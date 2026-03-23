"""Root URL configuration for the Agentic SDLC Platform."""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView as SpectacularSwaggerUIView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/auth/", include("apps.accounts.urls.auth")),
    path("api/v1/users/", include("apps.accounts.urls.users")),
    path("api/v1/workflows/", include("apps.workflows.urls")),
    path("api/v1/agents/", include("apps.agents.urls")),
    path("api/v1/mcp/", include("apps.mcp_client.urls")),
    path("api/v1/approvals/", include("apps.approvals.urls")),
    path("api/v1/pull-requests/", include("apps.pull_requests.urls")),
    path("api/v1/deployments/", include("apps.deployments.urls")),
    path("api/v1/audit/", include("apps.audit.urls")),

    # OpenAPI schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerUIView.as_view(url_name="schema"), name="swagger-ui"),
]
