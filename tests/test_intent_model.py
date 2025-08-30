import math
from collections import Counter
import pytest

class IntentModel:
    """Very small multinomial naive Bayes classifier."""

    def __init__(self):
        self.class_counts: Counter[str] = Counter()
        self.word_counts: dict[str, Counter[str]] = {}
        self.vocab: set[str] = set()

    def fit(self, texts, labels):
        for text, label in zip(texts, labels):
            self.class_counts[label] += 1
            words = text.lower().split()
            self.vocab.update(words)
            wc = self.word_counts.setdefault(label, Counter())
            wc.update(words)
        return self

    def predict(self, texts):
        total_docs = sum(self.class_counts.values())
        results = []
        for text in texts:
            t = text.strip().lower()
            if not t:
                results.append("unknown")
                continue
            words = t.split()
            best_label = None
            best_score = float("-inf")
            for label in self.class_counts:
                score = math.log(self.class_counts[label] / total_docs)
                wc = self.word_counts[label]
                total_words = sum(wc.values())
                for w in words:
                    score += math.log((wc.get(w, 0) + 1) / (total_words + len(self.vocab)))
                if score > best_score:
                    best_score = score
                    best_label = label
            results.append(best_label or "unknown")
        return results

@pytest.fixture
def dummy_dataset():
    texts = [
        "please upload my file",
        "can you upload the document",
        "what is your name",
        "how does this work",
    ]
    labels = [
        "upload_file",
        "upload_file",
        "ask_question",
        "ask_question",
    ]
    return texts, labels

@pytest.fixture
def intent_model(dummy_dataset):
    texts, labels = dummy_dataset
    model = IntentModel().fit(texts, labels)
    return model

def test_model_trains_on_dummy_data(intent_model, dummy_dataset):
    texts, labels = dummy_dataset
    assert intent_model.predict(texts) == list(labels)

def test_model_predicts_examples(intent_model):
    preds = intent_model.predict([
        "could you upload this file?",
        "what time is it?",
        "",
    ])
    assert preds == ["upload_file", "ask_question", "unknown"]
