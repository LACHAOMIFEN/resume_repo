from repopilot.workflow import run_pipeline


def test_pipeline_has_review():
    out = run_pipeline("Fix parser edge case", retries=0)
    assert "review" in out
    assert "attempts" in out
    assert isinstance(out["review"]["merge_ready"], bool)
