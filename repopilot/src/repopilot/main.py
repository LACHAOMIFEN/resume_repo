import json
import typer

from repopilot.artifacts import write_artifacts
from repopilot.github import parse_issue_input
from repopilot.pr import build_pr_create_command
from repopilot.summary import write_summary
from repopilot.workflow import run_pipeline

app = typer.Typer(help="RepoPilot CLI")


@app.command()
def run(
    issue: str = typer.Option(..., help="Issue text | issue URL | owner/repo#num"),
    out_dir: str = typer.Option("artifacts", help="Output directory for branch/patch/pr draft"),
    retries: int = typer.Option(1, min=0, help="Retry times when quality gates fail"),
    repo: str = typer.Option("", help="owner/repo for PR command generation"),
    base: str = typer.Option("main", help="base branch for PR command"),
    print_pr_command: bool = typer.Option(False, "--print-pr-command", help="Print gh pr create command"),
):
    parsed = parse_issue_input(issue)
    seed_text = f"{parsed.title}\n\n{parsed.body}".strip()
    result = run_pipeline(seed_text, retries=retries)
    result["input_issue"] = {"title": parsed.title, "body": parsed.body}

    artifacts = write_artifacts(
        out_dir=out_dir,
        issue_title=parsed.title,
        issue_body=parsed.body,
        issue_ref=issue,
        result=result,
    )
    result["artifacts"] = artifacts

    if print_pr_command and repo:
        pr_cmd = build_pr_create_command(
            repo=repo,
            branch_name=artifacts["branch_name"],
            base=base,
            title=f"fix: {parsed.title}",
        )
        result["pr_command"] = pr_cmd

    summary_path = write_summary(out_dir=out_dir, result=result)
    result.setdefault("artifacts", {})["summary"] = summary_path

    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
