from repopilot.agents import Plan, CodeProposal, ReviewResult, TestResult


def planner(issue_text: str) -> Plan:
    return Plan(
        tasks=["Reproduce bug", "Implement minimal fix", "Add regression test"],
        acceptance_criteria=["Tests pass", "No new lint errors"],
    )


def coder(plan: Plan) -> CodeProposal:
    return CodeProposal(
        summary="Proposed minimal fix based on plan",
        files_touched=["src/module.py", "tests/test_module.py"],
        patch_preview="diff --git a/src/module.py b/src/module.py ...",
    )


def tester(proposal: CodeProposal) -> TestResult:
    return TestResult(passed=True, checks=["pytest", "ruff"], notes="Mock run success")


def reviewer(proposal: CodeProposal, test: TestResult) -> ReviewResult:
    if not test.passed:
        return ReviewResult(merge_ready=False, risks=["Tests failing"], comments=["Fix tests first"])
    return ReviewResult(merge_ready=True, risks=[], comments=["Looks good for PR draft"])


def run_pipeline(issue_text: str) -> dict:
    p = planner(issue_text)
    c = coder(p)
    t = tester(c)
    r = reviewer(c, t)
    return {
        "plan": p.model_dump(),
        "code": c.model_dump(),
        "test": t.model_dump(),
        "review": r.model_dump(),
    }
