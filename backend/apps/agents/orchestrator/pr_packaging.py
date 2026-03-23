"""
PR Packaging Agent — drafts a pull request title, description,
review checklist, and labels from the change set and plan.
"""

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from .base import BoundedAgent


class PRPackagingOutput(BaseModel):
    title: str = Field(description="Pull request title (under 72 characters)")
    body: str = Field(description="Full PR description in Markdown")
    labels: list[str] = Field(default_factory=list)
    review_checklist: list[str] = Field(description="Items reviewers should verify")
    testing_notes: str = Field(description="How to test this change")
    breaking_changes: list[str] = Field(default_factory=list)
    linked_issues: list[str] = Field(default_factory=list)


class PRPackagingAgent(BoundedAgent):
    agent_type = "pr_packaging"
    OutputSchema = PRPackagingOutput

    system_prompt = (
        "You are a developer writing a pull request for a code change. "
        "Produce a clear, professional PR description following enterprise standards. "
        "The title must be under 72 characters. The body must use Markdown. "
        "Include a review checklist specific to the changes made."
    )

    def _build_chain(self):
        parser = PydanticOutputParser(pydantic_object=PRPackagingOutput)
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt + "\n\n{format_instructions}"),
            ("human", (
                "Story: {jira_issue_key} — {story_summary}\n\n"
                "Implementation Plan Summary:\n{plan_summary}\n\n"
                "Files Changed:\n{files_changed}\n\n"
                "Diff Summary:\n{diff_summary}\n\n"
                "Draft the pull request."
            )),
        ]).partial(format_instructions=parser.get_format_instructions())
        return prompt | self.llm | parser

    def _parse_output(self, raw_result) -> dict:
        if isinstance(raw_result, PRPackagingOutput):
            return raw_result.model_dump()
        return {"content": str(raw_result)}
