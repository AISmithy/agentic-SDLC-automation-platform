"""
Story Analysis Agent — summarizes a Jira story into a structured
implementation context including acceptance criteria, estimated scope,
affected modules, and recommended approach.
"""

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from .base import BoundedAgent


class StoryAnalysisOutput(BaseModel):
    summary: str = Field(description="Concise summary of the story")
    acceptance_criteria: list[str] = Field(description="Parsed acceptance criteria")
    estimated_complexity: str = Field(
        description="Estimated complexity: trivial | low | medium | high | very_high"
    )
    affected_modules: list[str] = Field(description="Likely affected system modules or services")
    recommended_approach: str = Field(description="Recommended implementation approach")
    questions: list[str] = Field(
        default_factory=list,
        description="Clarifying questions if story is ambiguous",
    )
    risks: list[str] = Field(default_factory=list, description="Identified risks or blockers")


class StoryAnalysisAgent(BoundedAgent):
    agent_type = "story_analysis"
    OutputSchema = StoryAnalysisOutput

    system_prompt = (
        "You are an experienced software engineer assistant. "
        "Analyze the provided Jira story and produce a structured analysis "
        "that will guide the implementation team. Be concise and precise. "
        "Do not hallucinate details not present in the story."
    )

    def _build_chain(self):
        parser = PydanticOutputParser(pydantic_object=StoryAnalysisOutput)
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt + "\n\n{format_instructions}"),
            ("human", (
                "Jira Story:\n"
                "Key: {issue_key}\n"
                "Summary: {summary}\n"
                "Description: {description}\n"
                "Acceptance Criteria: {acceptance_criteria}\n"
                "Story Type: {issue_type}\n"
                "Priority: {priority}\n\n"
                "Analyze this story."
            )),
        ]).partial(format_instructions=parser.get_format_instructions())
        return prompt | self.llm | parser

    def _format_user_prompt(self, ctx: dict) -> str:
        return (
            f"Story: {ctx.get('issue_key')} — {ctx.get('summary', '')}"
        )

    def _parse_output(self, raw_result) -> dict:
        if isinstance(raw_result, StoryAnalysisOutput):
            return raw_result.model_dump()
        return {"content": str(raw_result)}
