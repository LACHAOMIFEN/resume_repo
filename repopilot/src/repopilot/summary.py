from __future__ import annotations

from pathlib import Path


def render_summary(*, result: dict) -> str:
    issue = result.get("input_issue", {})
    test = result.get("test", {})
    review = result.get("review", {})
    artifacts = result.get("artifacts", {})
    attempts = result.get("attempts", [])

    lines = [
        "# RepoPilot Dry-Run Summary",
        "",
        "## Issue",
        f"- Title: {issue.get('title', '')}",
        f"- Body: {issue.get('body', '') or '(empty)'}",
        "",
        "## Quality Gates",
        f"- Passed: **{test.get('passed', False)}**",
        f"- Checks: {', '.join(test.get('checks', []))}",
        f"- Notes: {test.get('notes', '')}",
        "",
        "## Review",
        f"- Merge Ready: **{review.get('merge_ready', False)}**",
    ]
    for r in review.get("risks", []):
        lines.append(f"- Risk: {r}")
    for c in review.get("comments", []):
        lines.append(f"- Comment: {c}")

    lines += ["", "## Attempts"]
    for a in attempts:
        lines.append(f"- Attempt {a.get('attempt')}: {'PASS' if a.get('passed') else 'FAIL'} — {a.get('notes', '')}")

    lines += ["", "## Artifacts"]
    lines.append(f"- Branch Name: `{artifacts.get('branch_name', '')}`")
    lines.append(f"- branch_name.txt: `{artifacts.get('branch', '')}`")
    lines.append(f"- patch_preview.diff: `{artifacts.get('patch', '')}`")
    lines.append(f"- pr_draft.md: `{artifacts.get('pr_draft', '')}`")

    if result.get("pr_command"):
        lines += ["", "## PR Command", "```bash", result["pr_command"], "```"]

    return "\n".join(lines) + "\n"


def write_summary(out_dir: str | Path, result: dict) -> str:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    p = out / "summary.md"
    p.write_text(render_summary(result=result), encoding="utf-8")
    return str(p)
