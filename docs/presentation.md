# Plan de présentation

## 1. Le problème

Une application peut fonctionner correctement tout en contenant une faille de
sécurité. Si elle est publiée sans contrôle, un utilisateur peut exploiter cette
faille.

## 2. GitHub Actions

GitHub Actions exécute automatiquement des tâches après un `push`. Une machine
temporaire, appelée runner, récupère le projet et exécute le workflow YAML.

## 3. ZAP Action dans la pipeline

Le workflow démarre `app.py` sur le runner. L'action
`zaproxy/action-full-scan` lance ensuite ZAP contre cette copie temporaire de
l'application.

## 4. Démonstration

1. La version saine est poussée et publiée.
2. La ligne `displayed_query = escape(query)` est remplacée par
   `displayed_query = query`.
3. Une nouvelle version est poussée.
4. ZAP détecte la faille XSS.
5. La pipeline devient rouge.
6. GitHub Pages conserve l'ancienne version saine.
7. La ligne `displayed_query = escape(query)` est remise.
8. La pipeline devient verte et la nouvelle version est publiée.

## 5. Phrase à dire

> GitHub accepte le commit, mais la pipeline empêche son déploiement tant que
> le scan de sécurité ZAP échoue. La sécurité devient ainsi une étape
> automatique du développement logiciel.
