from dataclasses import dataclass


@dataclass
class Issue:
    title: str
    body: str


def parse_issue_input(issue: str) -> Issue:
    """Accepts plain text for MVP. Later: support URL/number via GitHub API."""
    return Issue(title="Input Issue", body=issue)
