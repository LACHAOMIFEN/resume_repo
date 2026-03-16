from __future__ import annotations

from dataclasses import dataclass
import json
import re
import subprocess


@dataclass
class Issue:
    title: str
    body: str


URL_RE = re.compile(r"https?://github\.com/([^/]+)/([^/]+)/issues/(\d+)")
SHORT_RE = re.compile(r"([^/\s]+)/([^#\s]+)#(\d+)$")


def _extract_ref(issue_input: str) -> tuple[str, str, int] | None:
    s = issue_input.strip()
    m = URL_RE.search(s)
    if m:
        owner, repo, num = m.groups()
        return owner, repo, int(num)
    m = SHORT_RE.search(s)
    if m:
        owner, repo, num = m.groups()
        return owner, repo, int(num)
    return None


def _fetch_issue_with_gh(owner: str, repo: str, number: int) -> Issue:
    cmd = [
        "gh",
        "issue",
        "view",
        str(number),
        "--repo",
        f"{owner}/{repo}",
        "--json",
        "title,body",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15, check=True)
    except FileNotFoundError as e:
        raise RuntimeError("`gh` CLI not found. Install GitHub CLI first.") from e
    except subprocess.CalledProcessError as e:
        msg = (e.stderr or e.stdout or "").strip()
        raise RuntimeError(f"Failed to fetch issue via gh: {msg}") from e

    data = json.loads(proc.stdout)
    return Issue(title=data.get("title", f"Issue #{number}"), body=data.get("body", ""))


def parse_issue_input(issue_input: str) -> Issue:
    """Parse plain issue text OR GitHub issue refs.

    Supports:
    - Free text (fallback)
    - https://github.com/owner/repo/issues/123
    - owner/repo#123
    """
    ref = _extract_ref(issue_input)
    if ref:
        owner, repo, num = ref
        return _fetch_issue_with_gh(owner, repo, num)

    return Issue(title="Input Issue", body=issue_input.strip())
