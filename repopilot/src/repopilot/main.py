import json
import typer

from repopilot.workflow import run_pipeline

app = typer.Typer(help="RepoPilot CLI")


@app.command()
def run(issue: str = typer.Option(..., help="Issue text or summary")):
    result = run_pipeline(issue)
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
