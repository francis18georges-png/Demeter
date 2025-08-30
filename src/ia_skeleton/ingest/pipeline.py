from __future__ import annotations

"""Dataset loading pipeline."""

from pathlib import Path
import csv
import json
from typing import List, Dict
from datasets import Dataset


def load_dataset(path: str) -> Dataset:
    """Load a dataset from a CSV or JSONL file.

    Args:
        path: Path to the dataset file.

    Returns:
        A :class:`datasets.Dataset` containing the data.

    Raises:
        FileNotFoundError: If the path does not exist.
        ValueError: If the file extension is unsupported.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    ext = file_path.suffix.lower()
    records: List[Dict[str, object]]
    if ext == ".csv":
        with file_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            records = list(reader)
    elif ext == ".jsonl":
        with file_path.open(encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
    else:
        raise ValueError(f"Unsupported dataset format: {ext}")

    return Dataset.from_list(records)
