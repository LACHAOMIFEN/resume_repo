from pydantic import BaseModel


class Plan(BaseModel):
    tasks: list[str]
    acceptance_criteria: list[str]


class CodeProposal(BaseModel):
    summary: str
    files_touched: list[str]
    patch_preview: str


class TestResult(BaseModel):
    passed: bool
    checks: list[str]
    notes: str = ""


class ReviewResult(BaseModel):
    merge_ready: bool
    risks: list[str]
    comments: list[str]
