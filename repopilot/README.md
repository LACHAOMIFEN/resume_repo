# RepoPilot

A resume-ready multi-agent project: **Issue → Plan → Code → Test → Review**.

## Stack
- Python 3.11+
- `openai-agents` (or your preferred agent runtime)
- `gh` CLI (optional, for GitHub integration)

## Quickstart
```bash
cd repopilot
python -m venv .venv
source .venv/bin/activate
pip install '.[dev]'
cp .env.example .env
python -m repopilot.main --issue "Fix failing unit tests in parser" --retries 1
# artifacts will be generated under ./artifacts
# gate checks auto-inject PYTHONPATH=src
```

## Input Formats
- Plain text: `--issue "Fix parser edge case"`
- Issue URL: `--issue "https://github.com/owner/repo/issues/123"`
- Short ref: `--issue "owner/repo#123"`

## Generated Artifacts
After each run, RepoPilot writes:
- `artifacts/branch_name.txt`
- `artifacts/patch_preview.diff`
- `artifacts/pr_draft.md`
- `artifacts/summary.md` (one-file dry-run report)

## PR Command (safe preview)
Print a draft PR command without executing it:
```bash
python -m repopilot.main --issue "owner/repo#123" --repo owner/repo --print-pr-command
```

## Milestones
1. Local simulation workflow (no GitHub required)
2. GitHub issue fetch ✅
3. Branch/patch generation
4. Test gate + reviewer gate
5. PR draft output

## Project Structure
- `src/repopilot/agents.py` Agent role contracts
- `src/repopilot/workflow.py` Orchestration pipeline
- `src/repopilot/github.py` GitHub/gh integration wrappers
- `src/repopilot/main.py` CLI entrypoint
- `configs/agents.yaml` Role prompts/configs
- `docs/ROADMAP.md` Step-by-step build plan
