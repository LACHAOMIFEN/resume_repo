from unittest.mock import patch

from repopilot.workflow import run_pipeline


def _fake_chat(messages, **kwargs):
    """Return valid JSON for any agent call."""
    system = messages[0].get("content", "")
    if "PlannerAgent" in system:
        return '{"tasks": ["Analyze issue", "Fix bug"], "acceptance_criteria": ["Tests pass"]}'
    if "CoderAgent" in system:
        return '{"summary": "Fix bug", "files_touched": ["src/main.py"], "patch_preview": "--- a/src/main.py\\n+++ b/src/main.py"}'
    if "ReviewerAgent" in system:
        return '{"merge_ready": true, "risks": [], "comments": ["LGTM"]}'
    return "{}"


@patch("repopilot.workflow.chat", side_effect=_fake_chat)
def test_pipeline_has_review(mock_chat):
    out = run_pipeline("Fix parser edge case", retries=0, execute_checks=False)
    assert "review" in out
    assert "attempts" in out
    assert isinstance(out["review"]["merge_ready"], bool)
    assert mock_chat.call_count == 3  # planner + coder + reviewer
