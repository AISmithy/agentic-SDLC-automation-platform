"""
Implementation Planning Agent — produces a step-by-step implementation plan
from the story analysis, repository context, and coding standards.
"""

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from .base import BoundedAgent


class ImplementationStep(BaseModel):
    order: int
    title: str
    description: str
    file_paths: list[str] = Field(default_factory=list)
    estimated_effort: str = Field(description="trivial | small | medium | large")
    step_type: str = Field(description="create | modify | delete | test | config | docs")


class ImplementationPlanOutput(BaseModel):
    plan_title: str
    plan_summary: str
    steps: list[ImplementationStep]
    test_strategy: str
    dependencies: list[str] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)
    total_estimated_effort: str


class ImplementationPlanningAgent(BoundedAgent):
    agent_type = "implementation_planning"
    OutputSchema = ImplementationPlanOutput

    system_prompt = (
        "You are a senior software architect. Based on the story analysis and "
        "available repository context, produce a detailed, actionable implementation plan. "
        "Steps must be concrete and reference actual file paths where known. "
        "Adhere to the provided coding standards."
    )

    def _build_chain(self):
        parser = PydanticOutputParser(pydantic_object=ImplementationPlanOutput)
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt + "\n\n{format_instructions}"),
            ("human", (
                "Story Analysis:\n{story_analysis}\n\n"
                "Repository Structure (excerpt):\n{repo_context}\n\n"
                "Coding Standards:\n{coding_standards}\n\n"
                "Produce a detailed implementation plan."
            )),
        ]).partial(format_instructions=parser.get_format_instructions())
        return prompt | self.llm | parser

    def _parse_output(self, raw_result) -> dict:
        if isinstance(raw_result, ImplementationPlanOutput):
            return raw_result.model_dump()
        return {"content": str(raw_result)}
