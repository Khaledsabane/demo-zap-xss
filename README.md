# Démonstration XSS bloquée avant publication

Ce projet montre comment intégrer un contrôle de sécurité dans une pipeline
GitHub Actions avant de publier un site sur GitHub Pages.

## Principe

```text
git push
    ↓
Tests Python
    ↓
Serveur temporaire app.py
    ↓
ZAP Full Scan
    ↓
Scan réussi : publication Pages
Scan échoué : publication bloquée
```

L'application contient une page de recherche. Dans la version vulnérable, la
valeur fournie par l'utilisateur est réinjectée directement dans le HTML. Un
script JavaScript peut donc être exécuté dans le navigateur : c'est une faille
XSS réfléchie.

Dans la version corrigée, `html.escape()` transforme les caractères spéciaux
en texte inoffensif.

## Architecture

- `site/` contient les fichiers statiques publiés sur GitHub Pages.
- `app.py` sert temporairement `site/` sur le runner GitHub et génère la page
  de recherche.
- `tests/test_app.py` vérifie le comportement vulnérable et corrigé.
- `zap.conf` rend l'alerte ZAP 40012 (Reflected XSS) bloquante.
- `.github/workflows/security.yml` exécute les tests, utilise l'action GitHub
  `zaproxy/action-full-scan` et publie `site/` uniquement si le scan réussit.

ZAP analyse l'application temporaire sur le runner, à l'adresse
`http://127.0.0.1:8000/`. Il ne scanne pas le code Python directement.

## Préparer le dépôt GitHub

1. Créer un dépôt GitHub public et vide.
2. Dans **Settings > Pages**, choisir **GitHub Actions** comme source.
3. Décompresser ce projet. Ouvrir un terminal dans le dossier qui contient
   directement `app.py`, `site/` et `.github/`.

## Tester localement

Python est nécessaire pour ces commandes. Docker n'est pas nécessaire pour le
test local ; ZAP sera exécuté dans Docker sur le runner GitHub.

```bash
python -m unittest discover -s tests -v
python app.py
```

Ouvrir ensuite :

```text
http://127.0.0.1:8000/
```

Dans le formulaire, rechercher un mot normal pour vérifier le fonctionnement.

La fonctionnalité de recherche dynamique est utilisée par le serveur Python
temporaire pendant le scan. GitHub Pages héberge uniquement les fichiers
statiques du dossier `site/`; il n'exécute pas `app.py`.

Pour afficher manuellement le comportement XSS dans l'environnement local,
utiliser uniquement cette application de démonstration :

```text
<script>alert('XSS')</script>
```

## Démonstration GitHub Actions

### 1. Publier la version saine

La version initiale doit contenir cette ligne dans `_search_page` :

```python
displayed_query = escape(query)
```

Puis exécuter :

```bash
git init
git branch -M main
git add .
git commit -m "Version saine initiale"
git remote add origin https://github.com/VOTRE_COMPTE/VOTRE_DEPOT.git
git push -u origin main
```

Le workflow doit effectuer les tests, réussir le scan ZAP, puis publier le
site sur une adresse de la forme :

```text
https://VOTRE_COMPTE.github.io/VOTRE_DEPOT/
```

### 2. Pousser la version vulnérable

Dans `app.py`, remplacer temporairement la ligne saine :

```python
# Version vulnérable : insertion directe de la saisie utilisateur
displayed_query = query
```

La différence est visible directement dans le diff GitHub : la saisie de
l'utilisateur est injectée dans le HTML sans être échappée.
Modifier également le titre de `site/index.html` afin de voir si la nouvelle
version est publiée, par exemple :

```html
NOUVELLE VERSION NON VALIDEE
```

Puis :

```bash
git add app.py site/index.html
git commit -m "Ajout volontaire d'une faille XSS"
git push
```

ZAP Action réalise un scan actif et recherche notamment la faille XSS réfléchie.
L'alerte 40012 est configurée en `FAIL` :

- `zap-security-check` échoue ;
- `prepare-pages` est ignoré ;
- `deploy` est ignoré ;
- l'ancien site sain reste en ligne.

Le commit est bien présent dans GitHub, mais il n'est pas publié sur GitHub
Pages.

Le rapport ZAP est disponible dans l'artefact `rapport-zap` de l'exécution
GitHub Actions.

### 3. Corriger puis republier

Remplacer à nouveau la ligne vulnérable par :

```python
displayed_query = escape(query)
```

Puis :

```bash
git add app.py
git commit -m "Correction de la faille XSS"
git push
```

Le scan doit réussir et la nouvelle version doit être publiée.

## Explication de la correction

Version vulnérable :

```python
displayed_query = query
```

Version corrigée :

```python
displayed_query = escape(query)
```

La version vulnérable insère la saisie utilisateur comme du HTML. La version
corrigée transforme `<` et `>` en caractères affichables afin que le navigateur
ne puisse pas interpréter la saisie comme du JavaScript.

## Limites et précautions

- Le scan actif doit être utilisé uniquement sur cette application de test.
- ZAP scanne l'application web en fonctionnement ; il ne lit pas directement
  le code source Python.
- Le scan recherche les vulnérabilités qu'il sait détecter sur les pages et
  paramètres découverts ; il ne garantit pas l'absence de toutes les failles.
- `app.py` n'est pas publié sur GitHub Pages. Seul le dossier `site/` est
  déployé.
