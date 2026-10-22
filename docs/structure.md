# Structure

- main.py : configuration et navigation.
- utils.py : navigation et présentation communes.
- src/config.py : chemins et répertoire privé.
- src/views/ : interface Streamlit.
- src/controllers/ : orchestration et validation.
- src/models/ : accès aux données, sécurité et stockage.
- data/processed/ : CSV préparés conservés.
- data/perinatalite.db : données d’analyse dérivées.
- data/private/ : fichiers privés créés à l’exécution, absents du ZIP.
- scripts/ : reconstruction, sauvegarde et restauration.
- tests/ : tests unitaires, intégration et interface.
- reports/ : preuves de validation.
- rapport/ : chapitres 7 à 10.
- .github/workflows/ci.yml : intégration continue préparée.
- Dockerfile et compose.yaml : déploiement local conteneurisé préparé.
