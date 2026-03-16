import json
import typer

from repopilot.artifacts import write_artifacts
from repopilot.github import parse_issue_input
from repopilot.workflow import run_pipeline

app = typer.Typer(help="RepoPilot CLI")


@app.command()
def run(
    issue: str = typer.Option(..., help="Issue text | issue URL | owner/repo#num"),
    out_dir: str = typer.Option("artifacts", help="Output directory for branch/patch/pr draft"),
):
    parsed = parse_issue_input(issue)
    seed_text = f"{parsed.title}\n\n{parsed.body}".strip()
    result = run_pipeline(seed_text)
    result["input_issue"] = {"title": parsed.title, "body": parsed.body}

    artifacts = write_artifacts(
        out_dir=out_dir,
        issue_title=parsed.title,
        issue_body=parsed.body,
        issue_ref=issue,
        result=result,
    )
    result["artifacts"] = artifacts

    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
