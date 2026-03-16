from __future__ import annotations

from pathlib import Path
import re


def make_branch_name(issue_title: str, issue_ref: str | None = None) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", issue_title.strip().lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)[:48] or "issue"
    if issue_ref:
        num = re.sub(r"\D+", "", issue_ref)
        if num:
            return f"fix/issue-{num}-{slug}"
    return f"fix/{slug}"


def render_pr_draft(*, issue_title: str, issue_body: str, result: dict, branch_name: str) -> str:
    plan = result["plan"]
    code = result["code"]
    test = result["test"]
    review = result["review"]

    lines = [
        f"# PR Draft: {issue_title}",
        "",
        "## Background",
        issue_body or "(No issue body provided)",
        "",
        "## Proposed Branch",
        f"`{branch_name}`",
        "",
        "## Plan",
    ]
    lines += [f"- [ ] {t}" for t in plan.get("tasks", [])]
    lines += ["", "## Acceptance Criteria"]
    lines += [f"- {c}" for c in plan.get("acceptance_criteria", [])]
    lines += ["", "## Code Changes"]
    lines += [f"- Summary: {code.get('summary', '')}"]
    lines += [f"- Files touched: {', '.join(code.get('files_touched', []))}"]
    lines += ["", "## Validation"]
    lines += [f"- Passed: **{test.get('passed')}**"]
    lines += [f"- Checks: {', '.join(test.get('checks', []))}"]
    lines += [f"- Notes: {test.get('notes', '')}"]
    lines += ["", "## Reviewer Notes"]
    lines += [f"- Merge ready: **{review.get('merge_ready')}**"]
    for r in review.get("risks", []):
        lines.append(f"- Risk: {r}")
    for c in review.get("comments", []):
        lines.append(f"- Comment: {c}")

    return "\n".join(lines) + "\n"


def write_artifacts(*, out_dir: str | Path, issue_title: str, issue_body: str, issue_ref: str | None, result: dict) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    branch_name = make_branch_name(issue_title, issue_ref)
    patch_preview = result["code"].get("patch_preview", "") + "\n"
    pr_md = render_pr_draft(
        issue_title=issue_title,
        issue_body=issue_body,
        result=result,
        branch_name=branch_name,
    )

    (out / "branch_name.txt").write_text(branch_name + "\n", encoding="utf-8")
    (out / "patch_preview.diff").write_text(patch_preview, encoding="utf-8")
    (out / "pr_draft.md").write_text(pr_md, encoding="utf-8")

    return {
        "branch": str(out / "branch_name.txt"),
        "patch": str(out / "patch_preview.diff"),
        "pr_draft": str(out / "pr_draft.md"),
        "branch_name": branch_name,
    }
