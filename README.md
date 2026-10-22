# Indicateurs de santé périnatale en France

Application Streamlit d’exploration des naissances et de la mortinatalité sur 2012–2023. Projet de Marwa MCHAREK, élaboré à partir du template pédagogique DATAROCKSTARS. Cette version comprend des corrections et ajouts préparés avec une assistance IA ; les choix doivent être compris et vérifiés avant leur présentation au jury.

## Démarrage sous Windows (terminal PowerShell de VS Code)

Utiliser Python 3.12. Ouvrir le dossier contenant main.py, puis :

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe setup.py
.venv\Scripts\python.exe -m streamlit run main.py
```

Ouvrir http://localhost:8501. Créer un compte depuis Connexion / Inscription. Aucun compte ni mot de passe par défaut n’est fourni.

## Linux / macOS

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python setup.py
.venv/bin/python -m streamlit run main.py
```

Le script setup.sh est une alternative si python3 désigne Python 3.12. Le script run.sh réutilise cet environnement. L’activation manuelle de l’environnement est facultative avec ces commandes.

## Fonctionnalités

- Consultation des naissances par France, régions et départements.
- Consultation de la mortinatalité par France, régions et DROM.
- Analyse croisée, classements et statistiques SQL.
- Exports CSV/ZIP conditionnés à la connexion.
- Inscription et connexion sécurisées, expiration de session et limitation des tentatives.
- Mes analyses enregistrées : création, consultation, renommage et suppression de configurations personnelles de classement régional, stockées avec TinyDB.

Les unités et limites scientifiques doivent être interprétées à partir des sources. Les marqueurs * et ** présents dans trois cellules DROM sont conservés dans SQLite ; leur signification doit être confirmée dans la documentation source. Les comparaisons restent descriptives et ne démontrent pas de causalité.

## Données et reconstruction

Les CSV et Excel d’origine du dossier reçu sont conservés. La base dérivée data/perinatalite.db inclut les tables historiques et trois tables relationnelles normalisées. Elle contient 19 territoires de mortinatalité, 4 indicateurs et 912 observations (y compris les valeurs manquantes).

Pour reconstruire cette base depuis les CSV préparés, application arrêtée :

```bash
python -m scripts.rebuild_database --force
```

Cette commande ne refait pas le nettoyage des Excel ; elle reproduit l’étape CSV préparés vers SQLite. Les notebooks initiaux restent disponibles pour la préparation amont.

## Comptes et fichiers privés

Une nouvelle installation crée data/private/users.db et data/private/saved_analyses.json. Pour un hébergement, PERINATAL_RUNTIME_DIR permet de choisir un répertoire privé persistant. Si un ancien data/users.db existe, le modèle le conserve comme base de comptes : faire une sauvegarde avant la mise à jour. Ne pas déplacer ou supprimer cette base en cours d’utilisation.

Les comptes réels, journaux privés, fichiers TinyDB et fichiers session.json sont exclus de l’archive distribuée. Ils ne doivent pas être ajoutés à Git. Les sauvegardes sont privées elles aussi.

## Tests

Dans l’environnement du projet :

```bash
python -m pip install -r requirements-dev.txt
python -m pytest --cov=src --cov-report=term --junitxml=reports/junit.xml
```

Résultat de validation : 66 tests réussis, couverture de lignes sous src arrondie à 82 %, sous Linux / Python 3.12.14. Les tests UI utilisent le moteur Streamlit AppTest, sans navigateur réel. Windows, Docker, le pipeline GitHub distant et un hébergement public ne sont pas validés par cette exécution.

## Documentation

- COMMENCER_ICI.md : installation et lecture conseillée.
- docs/conception.md : besoins, parcours, architecture et schémas.
- docs/plan_tests.md : scénarios, critères et preuves.
- docs/deploiement.md : local, Docker, stockage et retour arrière.
- docs/correspondance_CDA.md : compétences, preuves et limites.
- rapport/ : chapitres 7 à 10 actualisés, prêts à copier dans le rapport.
- reports/ : résultats automatisés de cette version.

## Provenance

Le projet initial utilise le template Streamlit fourni par DATAROCKSTARS (Marouan K., Bilel O., Matis C.). Les données et analyses proviennent du projet périnatalité fourni. Aucun entretien utilisateur réel, travail d’équipe Scrum ou déploiement public n’est revendiqué par les documents ajoutés.
