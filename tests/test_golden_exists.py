from pathlib import Path
def test_golden_present():
    assert Path('bench/golden/queries.jsonl').exists()
    assert Path('bench/golden/answers.jsonl').exists()
