from __future__ import annotations

"""Utility functions for training and using the intent classification model."""

from typing import TypedDict, Literal

Intent = Literal["upload_file", "ask_question", "unknown"]


class TrainedModel(TypedDict):
    """Minimal representation of a trained model."""
    path: str


def train_model(data_path: str) -> None:
    """Train a model using data stored at ``data_path``.

    This function is a placeholder for the training logic.
    """
    # Training logic would go here in a real project
    return None


def load_model(model_path: str) -> TrainedModel:
    """Load a trained model from ``model_path``.

    The skeleton simply records the path as the model artefact.
    """
    return {"path": model_path}


def predict(text: str, model: TrainedModel) -> Intent:
    """Classify ``text`` into an intent using ``model``.

    The current implementation uses simple keyword heuristics as a stand-in for a
    proper ML model.
    """
    t = (text or "").strip().lower()
    if any(k in t for k in ["upload", "import", "fichier", "file"]):
        return "upload_file"
    if t:
        return "ask_question"
    return "unknown"
