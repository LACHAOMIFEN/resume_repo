from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass

from repopilot.agents import CodeProposal, Plan, ReviewResult, TestResult
from repopilot.llm import chat
from repopilot.repo_context import build_tree, scan_repo


@dataclass
class CheckExec:
    name: str
    passed: bool
    output: str


# ---------------------------------------------------------------------------
# Planner Agent
# ---------------------------------------------------------------------------

def planner(issue_text: str, repo_path: str | None = None) -> Plan:
    context = ""
    if repo_path:
        context = f"\n\n## Repo structure\n{build_tree(repo_path)}"

    resp = chat([
        {
            "role": "system",
            "content": (
                "You are PlannerAgent. Given a GitHub issue description and optional repo context, "
                "break it down into atomic tasks with clear acceptance criteria.\n"
                "Return ONLY valid JSON with this schema:\n"
                '{"tasks": ["task1", ...], "acceptance_criteria": ["criterion1", ...]}'
            ),
        },
        {
            "role": "user",
            "content": f"## Issue\n{issue_text}{context}",
        },
    ])
    data = _parse_json(resp)
    return Plan(
        tasks=data.get("tasks", ["Analyze issue", "Implement fix", "Add tests"]),
        acceptance_criteria=data.get("acceptance_criteria", ["Tests pass"]),
    )


# ---------------------------------------------------------------------------
# Coder Agent
# ---------------------------------------------------------------------------

def coder(plan: Plan, issue_text: str, repo_path: str | None = None) -> CodeProposal:
    repo_context = ""
    if repo_path:
        repo_context = f"\n\n## Repo source code\n{scan_repo(repo_path)}"

    task_list = "\n".join(f"- {t}" for t in plan.tasks)
    criteria = "\n".join(f"- {c}" for c in plan.acceptance_criteria)

    resp = chat([
        {
            "role": "system",
            "content": (
                "You are CoderAgent. Given the plan, issue, and repo source code, "
                "propose minimal safe code changes as a unified diff patch.\n"
                "Return ONLY valid JSON with this schema:\n"
                "{\n"
                '  "summary": "one-line summary of changes",\n'
                '  "files_touched": ["path/to/file1.py", ...],\n'
                '  "patch_preview": "unified diff content"\n'
                "}\n"
                "The patch_preview should be a valid unified diff (--- a/... +++ b/... format)."
            ),
        },
        {
            "role": "user",
            "content": (
                f"## Issue\n{issue_text}\n\n"
                f"## Plan\n{task_list}\n\n"
                f"## Acceptance Criteria\n{criteria}"
                f"{repo_context}"
            ),
        },
    ])
    data = _parse_json(resp)
    return CodeProposal(
        summary=data.get("summary", "Proposed code changes"),
        files_touched=data.get("files_touched", []),
        patch_preview=data.get("patch_preview", "(no patch generated)"),
    )


# ---------------------------------------------------------------------------
# Tester Agent (real execution, unchanged)
# ---------------------------------------------------------------------------

def _run_check(cmd: list[str], timeout: int = 120) -> CheckExec:
    name = " ".join(cmd)
    if shutil.which(cmd[0]) is None:
        return CheckExec(name=name, passed=False, output=f"missing binary: {cmd[0]}")

    env = os.environ.copy()
    src_path = os.path.abspath("src")
    env["PYTHONPATH"] = src_path + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return CheckExec(name=name, passed=False, output="timeout")

    out = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
    return CheckExec(name=name, passed=(proc.returncode == 0), output=out.strip()[:1200])


def tester(
    proposal: CodeProposal,
    checks: list[list[str]] | None = None,
    execute_checks: bool = True,
) -> TestResult:
    checks = checks or [[sys.executable, "-m", "pytest", "-q", "tests"], ["ruff", "check", "."]]
    if not execute_checks:
        names = [" ".join(c) for c in checks]
        return TestResult(passed=True, checks=names, notes="check execution skipped (test mode)")

    results = [_run_check(c) for c in checks]
    passed = all(r.passed for r in results)
    summary = " | ".join([f"{r.name}: {'ok' if r.passed else 'fail'}" for r in results])
    failed_details = [f"{r.name} => {r.output[:320]}" for r in results if not r.passed]
    notes = summary + (" || " + " || ".join(failed_details) if failed_details else "")
    return TestResult(passed=passed, checks=[r.name for r in results], notes=notes)


# ---------------------------------------------------------------------------
# Reviewer Agent
# ---------------------------------------------------------------------------

def reviewer(proposal: CodeProposal, test: TestResult) -> ReviewResult:
    resp = chat([
        {
            "role": "system",
            "content": (
                "You are ReviewerAgent. Evaluate the proposed code changes and test results.\n"
                "Consider: correctness, risk of regressions, code quality, and test coverage.\n"
                "Return ONLY valid JSON with this schema:\n"
                "{\n"
                '  "merge_ready": true/false,\n'
                '  "risks": ["risk1", ...],\n'
                '  "comments": ["comment1", ...]\n'
                "}"
            ),
        },
        {
            "role": "user",
            "content": (
                f"## Code Changes\n"
                f"Summary: {proposal.summary}\n"
                f"Files: {', '.join(proposal.files_touched)}\n\n"
                f"## Patch\n```diff\n{proposal.patch_preview}\n```\n\n"
                f"## Test Results\n"
                f"Passed: {test.passed}\n"
                f"Checks: {', '.join(test.checks)}\n"
                f"Notes: {test.notes}"
            ),
        },
    ])
    data = _parse_json(resp)

    # Fallback: if tests failed, never mark as merge_ready regardless of LLM output
    merge_ready = data.get("merge_ready", False)
    if not test.passed:
        merge_ready = False

    return ReviewResult(
        merge_ready=merge_ready,
        risks=data.get("risks", []),
        comments=data.get("comments", []),
    )


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(
    issue_text: str,
    retries: int = 1,
    execute_checks: bool = True,
    repo_path: str | None = None,
) -> dict:
    p = planner(issue_text, repo_path=repo_path)
    c = coder(p, issue_text, repo_path=repo_path)

    attempts = []
    t = None
    for i in range(max(1, retries + 1)):
        t = tester(c, execute_checks=execute_checks)
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    text = text.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last fence lines
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        return {}
