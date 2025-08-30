# IA — Squelette Gate 0
Squelette minimal pour lancer le plan par étapes : policies, CI, observabilité, golden sets, simulateur, SBOM, snapshots.

## Modèle de classification d'intentions

Le dossier `src/ia_skeleton/services/app` contient un module `model.py`
exposant trois fonctions simples :

* `train_model(data_path: str) -> None` — prépare le modèle à partir de
  données d'entraînement.
* `load_model(model_path: str) -> TrainedModel` — charge un modèle existant
  depuis le disque.
* `predict(text: str, model: TrainedModel) -> Intent` — retourne l'intention
  (`"upload_file"`, `"ask_question"` ou `"unknown"`) correspondant au texte
  fourni.

`webui.py` charge automatiquement le modèle à l'initialisation et
`intent_router.route` délègue désormais la classification à `predict`.

```python
from ia_skeleton.services.app.model import load_model, predict

model = load_model("model.pkl")
intent = predict("upload my file", model)
```
