# Installation, déploiement et exploitation

## État validé

Installation dans un environnement virtuel neuf, contrôle pip check sans conflit, 66 tests réussis. Démarrage du serveur Streamlit lié à 127.0.0.1 dans l’environnement de validation : point de santé /_stcore/health = ok et page HTTP = 200. Ces contrôles ne constituent pas un hébergement public ni une recette dans un navigateur.

## Local

Suivre le README. Le lancement utilise Python 3.12 et requirements-lock.txt. Le fichier requirements.txt fixe les dépendances directes ; requirements-lock.txt fixe aussi les dépendances transitives du système de référence. La résolution et les paquets spécifiques à Windows restent à vérifier sur Windows.

setup.py crée le schéma des comptes sans compte administrateur par défaut et reconstruit la base d’analyse seulement si elle est absente. Pour reconstruire une base dérivée existante, arrêter l’application puis utiliser python -m scripts.rebuild_database --force. Cette reconstruction ne modifie ni les comptes ni les documents personnels.

## Configuration privée

PERINATAL_RUNTIME_DIR désigne le répertoire persistant pour les nouvelles installations. Par défaut : data/private/. Si un ancien data/users.db existe, il reste prioritaire pour préserver les comptes. Le répertoire choisi doit rester hors des fichiers publiés et disposer de droits adaptés au compte de service. Les mots de passe, adresses et sauvegardes ne doivent pas être committés. La conservation des comptes, des logs et des documents doit être définie avant une ouverture à des utilisateurs réels.

## Docker préparé

```bash
docker compose up --build -d
docker compose logs dashboard
docker compose down
```

Le service est exposé uniquement sur http://127.0.0.1:8501. Le volume private-data conserve les nouvelles données privées après un redémarrage. Ne pas utiliser docker compose down -v si ce volume doit être conservé. L’image utilise un compte non privilégié. Un contrôle de santé interroge Streamlit. Le .dockerignore exclut les données privées.

Les conteneurs et leur contrôle de santé sont préparés mais n’ont pas été exécutés localement : Docker n’est pas disponible dans l’environnement de validation. Le pipeline les testera lorsqu’il sera lancé sur GitHub.

Pour une exposition distante : mettre en place un reverse proxy HTTPS compatible WebSocket, le stockage persistant, les droits et les sauvegardes, puis effectuer une recette. Aucune publication ni ouverture de port public n’a été réalisée. Le fait d’héberger l’application n’implique pas que tout son contenu est privé : la consultation des indicateurs reste libre par conception.

## Sauvegarde et restauration hors conteneur

Arrêter l’application avant de lancer les commandes avec le Python de son environnement.

```bash
python -m scripts.backup create backups/avant-mise-a-jour --confirm-stopped
python -m scripts.backup restore backups/avant-mise-a-jour --confirm-stopped
```

Le dossier de sauvegarde doit être nouveau. SQLite est copié avec l’API backup ; les documents sont copiés sous verrou et validés comme JSON. Une restauration valide les sources avant de remplacer les fichiers. La restauration remplace les données actuelles : conserver une copie préalable. Les deux bases ne partagent pas de transaction distribuée ; l’arrêt de l’application est nécessaire pour une sauvegarde cohérente de l’ensemble. Les verrous ne suffisent pas à rendre le remplacement sûr pendant l’utilisation.

Dans Docker, le volume doit être sauvegardé à l’arrêt du service par l’exploitant ; la procédure CLI ci-dessus est validée pour les fichiers locaux, pas pour l’administration des volumes Docker.

## Retour arrière et journaux

Avant mise à jour : sauvegarder le code précédent et les fichiers privés, arrêter le service, installer la nouvelle version et lancer les tests. Après mise à jour : vérifier santé, navigation, connexion et persistance. En cas d’échec : arrêter la nouvelle version, remettre le code précédent et restaurer sa sauvegarde compatible, puis redémarrer. Les évolutions de schéma doivent être prises en compte avant de réutiliser une ancienne version.

Les erreurs sont envoyées aux journaux serveur avec logging ; l’utilisateur reçoit un message simplifié. Ne pas publier les traces internes. Définir la rotation et la rétention des journaux sur l’hébergement réel.

## Intégration continue

.github/workflows/ci.yml installe les dépendances, reconstruit la base dérivée, exécute les tests, conserve les résultats puis prépare une construction et un test de santé Docker. Le workflow ne publie aucune image et ne déploie rien. Il remplace le pipeline initial obsolète. L’exécution distante et une véritable livraison continue restent à réaliser sur le dépôt et l’hébergement retenus.

Références : https://docs.streamlit.io/deploy/tutorials/docker et https://docs.github.com/en/actions
