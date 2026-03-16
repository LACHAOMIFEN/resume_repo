import json
import typer

from repopilot.github import parse_issue_input
from repopilot.workflow import run_pipeline

app = typer.Typer(help="RepoPilot CLI")


@app.command()
def run(issue: str = typer.Option(..., help="Issue text | issue URL | owner/repo#num")):
    parsed = parse_issue_input(issue)
    seed_text = f"{parsed.title}\n\n{parsed.body}".strip()
    result = run_pipeline(seed_text)
    result["input_issue"] = {"title": parsed.title, "body": parsed.body}
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
