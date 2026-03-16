from __future__ import annotations

import os
from pathlib import Path

# File extensions to include when scanning repo
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
    ".c", ".cpp", ".h", ".hpp", ".rb", ".php", ".swift", ".kt",
    ".scala", ".sh", ".bash", ".yaml", ".yml", ".toml", ".json",
    ".md", ".txt", ".cfg", ".ini",
}

IGNORE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", ".ruff_cache", "dist", "build", ".tox",
    ".mypy_cache", ".eggs", "*.egg-info",
}

MAX_FILE_SIZE = 50_000  # bytes
MAX_TOTAL_CHARS = 120_000


def scan_repo(repo_path: str, max_total: int = MAX_TOTAL_CHARS) -> str:
    """Read key files from a local repo and return a combined context string."""
    root = Path(repo_path).resolve()
    if not root.is_dir():
        return f"(repo path not found: {repo_path})"

    collected: list[str] = []
    total = 0

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored dirs
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.endswith(".egg-info")]

        for fname in sorted(filenames):
            fpath = Path(dirpath) / fname
            if fpath.suffix not in CODE_EXTENSIONS:
                continue
            if fpath.stat().st_size > MAX_FILE_SIZE:
                continue

            rel = fpath.relative_to(root)
            try:
                content = fpath.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            chunk = f"### {rel}\n```\n{content}\n```\n"
            if total + len(chunk) > max_total:
                collected.append(f"\n(... truncated, {max_total} char limit reached)\n")
                return "\n".join(collected)

            collected.append(chunk)
            total += len(chunk)

    if not collected:
        return "(no code files found in repo)"

    return "\n".join(collected)


def build_tree(repo_path: str) -> str:
    """Build a simple directory tree string."""
    root = Path(repo_path).resolve()
    if not root.is_dir():
        return f"(repo path not found: {repo_path})"

    lines: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.endswith(".egg-info")]
        rel = Path(dirpath).relative_to(root)
        depth = len(rel.parts)
        indent = "  " * depth
        lines.append(f"{indent}{Path(dirpath).name}/")
        for f in sorted(filenames):
            if Path(f).suffix in CODE_EXTENSIONS:
                lines.append(f"{indent}  {f}")
    return "\n".join(lines)
