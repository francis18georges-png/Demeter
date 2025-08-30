# IA — Squelette Gate 0
Squelette minimal pour lancer le plan par étapes : policies, CI, observabilité, golden sets, simulateur, SBOM, snapshots.

## Modules IA
- `intent_router` : détermine l'intention d'une requête utilisateur (import de fichier ou question libre).
- `min_echo` : service d'écho minimal utilisé pour les tests de connectivité.

## Procédure d'entraînement
1. Préparer un corpus d'exemples d'intentions.
2. Entraîner un modèle `scikit-learn` (ex. `LogisticRegression`) et l'enregistrer dans `artifacts/model.joblib`.
3. Mettre à jour le service pour charger ce modèle au démarrage.

## Procédure d'inférence
1. Lancer le serveur :
   ```bash
   uvicorn ia_skeleton.services.app.webui:app
   ```
2. Envoyer une requête à l'endpoint `/chat` :
   ```bash
   curl -X POST "http://localhost:8000/chat" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "q=Bonjour"
   ```
   Réponse attendue :
   ```json
   {"intent": "chat", "echo": "Bonjour"}
   ```
