from pathlib import Path
def test_policy():
    txt = Path('policies/policy.yaml').read_text(encoding='utf-8')
    assert 'auto_editable' in txt and 'web_allowlist' in txt
