"""
Base class for all bounded LangChain agents.

Each agent:
- Receives a scoped context (never raw user input without filtering)
- Uses only the tools injected by the engine (never arbitrary tool access)
- Produces typed Pydantic output persisted to AgentRun
- Runs within policy-approved model + prompt constraints
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Type

from pydantic import BaseModel
from django.conf import settings
from django.utils import timezone as django_timezone

logger = logging.getLogger(__name__)


def _build_llm(provider: str | None = None, model: str | None = None):
    """Factory — returns a LangChain-compatible LLM instance."""
    provider = provider or settings.DEFAULT_LLM_PROVIDER
    model = model or settings.DEFAULT_LLM_MODEL

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            api_key=settings.ANTHROPIC_API_KEY,
            max_tokens=4096,
        )
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model, api_key=settings.OPENAI_API_KEY)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


class BoundedAgent(ABC):
    """
    Abstract base for all platform agents.

    Subclasses define:
    - system_prompt: str
    - OutputSchema: Type[BaseModel]
    - _build_chain(): returns a LangChain Runnable
    """

    agent_type: str = "base"
    system_prompt: str = ""
    OutputSchema: Type[BaseModel] | None = None

    def __init__(self, step_run, allowed_tools: list | None = None):
        """
        :param step_run: WorkflowStepRun instance this agent runs within.
        :param allowed_tools: List of MCP capability names this agent may invoke.
        """
        self.step_run = step_run
        self.allowed_tools = allowed_tools or []
        self.llm = _build_llm()

    def run(self, input_context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the agent and persist results to AgentRun.
        Returns the structured output dict.
        """
        from apps.agents.models import AgentRun

        agent_run = AgentRun.objects.create(
            step_run=self.step_run,
            agent_type=self.agent_type,
            llm_provider=settings.DEFAULT_LLM_PROVIDER,
            llm_model=settings.DEFAULT_LLM_MODEL,
            system_prompt=self.system_prompt,
            user_prompt=self._format_user_prompt(input_context),
        )

        try:
            chain = self._build_chain()
            raw_result = chain.invoke(self._prepare_input(input_context))
            structured = self._parse_output(raw_result)

            agent_run.status = AgentRun.Status.COMPLETED
            agent_run.raw_response = str(raw_result)
            agent_run.structured_output = structured
            agent_run.completed_at = django_timezone.now()
            agent_run.save(update_fields=[
                "status", "raw_response", "structured_output", "completed_at"
            ])

            return structured

        except Exception as exc:
            logger.exception("Agent %s failed: %s", self.agent_type, exc)
            agent_run.status = AgentRun.Status.FAILED
            agent_run.error_message = str(exc)
            agent_run.completed_at = django_timezone.now()
            agent_run.save(update_fields=["status", "error_message", "completed_at"])
            raise

    @abstractmethod
    def _build_chain(self):
        """Return a LangChain Runnable."""
        ...

    def _prepare_input(self, input_context: dict) -> dict:
        return input_context

    def _format_user_prompt(self, input_context: dict) -> str:
        return str(input_context)

    def _parse_output(self, raw_result) -> dict:
        """Parse LLM output to structured dict. Override for schema validation."""
        if hasattr(raw_result, "content"):
            return {"content": raw_result.content}
        return {"content": str(raw_result)}
