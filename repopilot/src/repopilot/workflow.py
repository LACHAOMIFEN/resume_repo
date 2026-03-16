from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass

from repopilot.agents import CodeProposal, Plan, ReviewResult, TestResult


@dataclass
class CheckExec:
    name: str
    passed: bool
    output: str


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


def _run_check(cmd: list[str], timeout: int = 60) -> CheckExec:
    name = " ".join(cmd)
    if shutil.which(cmd[0]) is None:
        return CheckExec(name=name, passed=False, output=f"missing binary: {cmd[0]}")

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return CheckExec(name=name, passed=False, output="timeout")

    out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return CheckExec(name=name, passed=(proc.returncode == 0), output=out.strip()[:1200])


def tester(proposal: CodeProposal, checks: list[list[str]] | None = None) -> TestResult:
    checks = checks or [["pytest", "-q"], ["ruff", "check", "."]]
    results = [_run_check(c) for c in checks]
    passed = all(r.passed for r in results)
    notes = " | ".join([f"{r.name}: {'ok' if r.passed else 'fail'}" for r in results])
    return TestResult(passed=passed, checks=[r.name for r in results], notes=notes)


def reviewer(proposal: CodeProposal, test: TestResult) -> ReviewResult:
    if not test.passed:
        return ReviewResult(
            merge_ready=False,
            risks=["Quality gate failed (tests/lint)", "Potential regression risk"],
            comments=["Fix failing checks before opening PR"],
        )
    return ReviewResult(merge_ready=True, risks=[], comments=["Looks good for PR draft"])


def run_pipeline(issue_text: str, retries: int = 1) -> dict:
    p = planner(issue_text)
    c = coder(p)

    attempts = []
    t = None
    for i in range(max(1, retries + 1)):
        t = tester(c)
        attempts.append({"attempt": i + 1, "passed": t.passed, "notes": t.notes})
        if t.passed:
            break

    assert t is not None
    r = reviewer(c, t)
    return {
        "plan": p.model_dump(),
        "code": c.model_dump(),
        "test": t.model_dump(),
        "review": r.model_dump(),
        "attempts": attempts,
    }
