"""Agent registry — maps agent_type strings to agent classes."""

from .story_analysis import StoryAnalysisAgent
from .implementation_planning import ImplementationPlanningAgent
from .pr_packaging import PRPackagingAgent
from .base import BoundedAgent

AGENT_REGISTRY: dict[str, type[BoundedAgent]] = {
    "story_analysis": StoryAnalysisAgent,
    "implementation_planning": ImplementationPlanningAgent,
    "pr_packaging": PRPackagingAgent,
}


def get_agent_class(agent_type: str) -> type[BoundedAgent]:
    cls = AGENT_REGISTRY.get(agent_type)
    if not cls:
        raise ValueError(f"No agent registered for type '{agent_type}'.")
    return cls
