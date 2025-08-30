import pytest
from datasets import Dataset
from ia_skeleton.ingest import load_dataset
from ia_skeleton.services.train import train_model


def test_load_dataset_csv(tmp_path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    ds = load_dataset(str(csv_path))
    assert isinstance(ds, Dataset)
    assert ds.num_rows == 2
    assert ds[0]["a"] == "1"


def test_load_dataset_jsonl(tmp_path):
    jsonl_path = tmp_path / "data.jsonl"
    jsonl_path.write_text('{"a":1,"b":2}\n{"a":3,"b":4}\n', encoding="utf-8")
    ds = load_dataset(str(jsonl_path))
    assert isinstance(ds, Dataset)
    assert ds.num_rows == 2
    assert ds[1]["b"] == 4


def test_train_model_uses_load_dataset(tmp_path, monkeypatch):
    data_path = tmp_path / "data.csv"
    data_path.write_text("x\n1\n", encoding="utf-8")

    called = {}

    def fake_loader(path: str):
        called["path"] = path
        return Dataset.from_list([{ "x": 1 }])

    monkeypatch.setattr("ia_skeleton.services.train.load_dataset", fake_loader)
    result = train_model(str(data_path))
    assert called["path"] == str(data_path)
    assert result == 1
