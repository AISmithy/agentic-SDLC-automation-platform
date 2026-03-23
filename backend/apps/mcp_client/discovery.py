"""
MCP Capability Discovery Service.

Queries the MCP server, syncs capabilities to the database registry,
and classifies new write-capable tools as disabled by default.
"""

import logging
from .client import get_mcp_client
from .models import MCPCapability

logger = logging.getLogger(__name__)

# Tools known to be write-capable by category
WRITE_CAPABLE_TOOLS = {
    "create_branch", "create_pr", "merge_pr", "trigger_deployment",
    "push_commits", "update_issue", "create_issue",
}
APPROVAL_REQUIRED_TOOLS = {"create_pr", "trigger_deployment", "merge_pr"}
ENVIRONMENT_SENSITIVE_TOOLS = {"trigger_deployment"}


def sync_capabilities() -> dict[str, int]:
    """
    Discover MCP capabilities and sync them to the database.
    Returns counts of created/updated entries.
    """
    client = get_mcp_client()
    try:
        remote = client.discover_capabilities()
    except Exception as exc:
        logger.error("MCP capability discovery failed: %s", exc)
        return {"error": str(exc)}

    created = updated = 0

    for capability_type, items in remote.items():
        if capability_type not in ("tools", "prompts", "resources"):
            continue
        cap_type_key = capability_type.rstrip("s")  # tools -> tool

        for item in items:
            name = item.get("name", "")
            if not name:
                continue

            access_level = _classify_access(name, cap_type_key)
            is_unknown_write = (
                cap_type_key == "tool"
                and access_level == MCPCapability.AccessLevel.WRITE_CAPABLE
                and name not in WRITE_CAPABLE_TOOLS
            )

            cap, was_created = MCPCapability.objects.update_or_create(
                name=name,
                capability_type=cap_type_key,
                defaults={
                    "description": item.get("description", ""),
                    "schema": item.get("inputSchema", {}),
                    "access_level": access_level,
                    # Unknown write-capable tools disabled by default (policy §9.3)
                    "is_enabled": not is_unknown_write,
                    "is_unknown_write": is_unknown_write,
                },
            )
            if was_created:
                created += 1
                logger.info("MCP capability registered: %s/%s", cap_type_key, name)
            else:
                updated += 1

    logger.info("MCP sync complete: %d created, %d updated", created, updated)
    return {"created": created, "updated": updated}


def _classify_access(name: str, capability_type: str) -> str:
    if capability_type != "tool":
        return MCPCapability.AccessLevel.READ_ONLY
    if name in ENVIRONMENT_SENSITIVE_TOOLS:
        return MCPCapability.AccessLevel.ENVIRONMENT_SENSITIVE
    if name in APPROVAL_REQUIRED_TOOLS:
        return MCPCapability.AccessLevel.APPROVAL_REQUIRED
    if name in WRITE_CAPABLE_TOOLS:
        return MCPCapability.AccessLevel.WRITE_CAPABLE
    return MCPCapability.AccessLevel.READ_ONLY
