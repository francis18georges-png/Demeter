"""Routing logic for user intents."""

from .model import Intent, TrainedModel, predict


def route(text: str, model: TrainedModel) -> Intent:
    """Route ``text`` to a specific intent using ``model``."""
    return predict(text, model)
