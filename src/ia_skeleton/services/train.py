"""Model training service."""

from ia_skeleton.ingest import load_dataset


def train_model(dataset_path: str) -> int:
    """Train a model on the dataset located at ``dataset_path``.

    This is a placeholder implementation that simply loads the dataset
    and returns the number of records.
    """
    dataset = load_dataset(dataset_path)
    # Placeholder for actual training logic
    return len(dataset)
