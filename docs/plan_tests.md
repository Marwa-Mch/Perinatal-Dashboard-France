# Plan de tests et résultats

Environnement de référence : Linux, Python 3.12.14, installation isolée des dépendances. Exécution le 21 octobre 2026. Résultat : 66 tests réussis ; couverture des lignes de src arrondie à 82 %. La couverture ne prouve pas l’absence de défauts.

| Famille | Vérification et résultat attendu | Preuve |
|---|---|---|
| Comptes | Inscription valide puis connexion ; mauvais mot de passe refusé | tests/test_auth.py |
| Validation | E-mail incorrect, mot de passe trop court, doublon refusés | tests/test_auth.py |
| Migration | SHA-256 remplacé par Argon2id après connexion réussie | tests/test_auth.py |
| Sessions | Expiration inactive/absolue et nettoyage à la déconnexion | tests/test_auth.py |
| Tentatives | Blocage après cinq tentatives, partagé entre sessions ; fin de fenêtre | tests/test_auth.py |
| SQLite comptes | Commit, unicité, clés étrangères et paramètres SQL | tests/test_database.py |
| Métier SQL | A=5, B=10, C=manquant : top 1=B/10 ; moyenne=7,5 ; effectif=2 | tests/test_analysis.py |
| Entrées SQL | Année, limite et indicateur invalides refusés | tests/test_analysis.py |
| Qualité | Vide, doublon géographique, négatif et texte invalide refusés | tests/test_analysis.py |
| Annotations | 2,9** devient 2,9 sans altérer le CSV d’origine | tests/test_analysis.py |
| Cohérence réelle | CSV préparés comparés aux trois tables SQLite | tests/test_data_consistency.py |
| Calculs | Variation de 100 à 80 = -20 % ; base nulle indisponible | tests/test_transformations.py |
| Export | Années et nombres de naissances exportés sans décimales | tests/test_transformations.py |
| NoSQL | Création, lecture, renommage, suppression et isolation entre comptes | tests/test_saved.py |
| Concurrence | Douze écritures documentaires concurrentes conservées | tests/test_saved.py |
| Sauvegarde | Sauvegarde et restauration sur des fichiers de test | tests/test_backup.py |
| Interface | Huit pages, six changements de filtres, inscription, analyse enregistrée et déconnexion | tests/test_ui.py |

Les tests de comptes et de documents utilisent des répertoires temporaires. Les tests de cohérence lisent uniquement la base d’analyse distribuée. Le chargement des pages utilise AppTest et non un navigateur réel. Les graphiques ne font pas l’objet d’une comparaison visuelle pixel par pixel. Les téléchargements sont contrôlés au niveau du code et du contenu préparé, pas par téléchargement dans un navigateur.

## Reproduire

```bash
python -m pip install -r requirements-lock.txt -r requirements-dev.txt
python -m scripts.rebuild_database --force
python -m pytest --junitxml=reports/junit.xml --cov=src --cov-report=term --cov-report=xml:reports/coverage.xml
```

Les fichiers reports/junit.xml et reports/coverage.xml sont les preuves de l’exécution locale de cette version. Une nouvelle exécution les remplace. Le pipeline GitHub Actions est configuré, mais aucun résultat d’exécution distante n’est fourni.

## Recette manuelle à terminer sur la machine et l’hébergement retenus

- Installation sous Windows avec Python 3.12.
- Navigation au clavier et affichage sur petit écran.
- Lisibilité des graphiques et unités en comparaison avec les sources.
- Téléchargement effectif des CSV/ZIP dans le navigateur.
- Persistance des comptes et configurations après redémarrage de l’hébergement.
- Construction et lancement Docker ; disponibilité HTTPS une fois hébergée.
- Test de charge et essai de restauration avec une sauvegarde de l’installation réelle.

Ces contrôles non réalisés ne doivent pas être présentés comme réussis dans le rapport.
