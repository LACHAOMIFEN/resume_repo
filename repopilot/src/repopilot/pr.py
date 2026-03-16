from __future__ import annotations


def build_pr_create_command(*, repo: str, branch_name: str, base: str = "main", title: str = "chore: automated issue fix draft") -> str:
    return (
        f"gh pr create --repo {repo} --draft "
        f"--base {base} --head {branch_name} "
        f"--title \"{title}\" --body-file artifacts/pr_draft.md"
    )
