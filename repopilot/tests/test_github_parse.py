import json

from repopilot.github import parse_issue_input


def test_parse_plain_text():
    out = parse_issue_input("fix parser bug")
    assert out.title == "Input Issue"
    assert "fix parser bug" in out.body


def test_parse_short_ref_with_mock(monkeypatch):
    class P:
        stdout = json.dumps({"title": "Bug title", "body": "Bug body"})

    def fake_run(*args, **kwargs):
        return P()

    monkeypatch.setattr("subprocess.run", fake_run)
    out = parse_issue_input("owner/repo#12")
    assert out.title == "Bug title"
    assert out.body == "Bug body"
