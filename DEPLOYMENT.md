# 📦 Guide de déploiement sur GitHub

## Étape 1 : Créer un dépôt sur GitHub

1. Allez sur https://github.com
2. Cliquez sur le bouton "+" en haut à droite puis "New repository"
3. Remplissez les informations :
   - **Repository name** : `CCV-geolocalisation` (ou un autre nom)
   - **Description** : "Jeu de géolocalisation interactif pour Combronde (Puy-de-Dôme)"
   - **Visibilité** : Public ou Private selon votre choix
   - Ne cochez pas "Initialize with README" (car vous en avez déjà un)
4. Cliquez sur "Create repository"

## Étape 2 : Pousser le code sur GitHub

GitHub vous donnera des instructions. Utilisez celles-ci :

```bash
cd /Users/chateau/dev/sandbox/CCV
git remote add origin https://github.com/VOTRE_USERNAME/CCV-geolocalisation.git
git branch -M main
git push -u origin main
```

Remplacez `VOTRE_USERNAME` par votre nom d'utilisateur GitHub.

## Étape 3 : Déployer sur Streamlit Cloud (gratuit)

1. Allez sur https://share.streamlit.io/
2. Connectez-vous avec votre compte GitHub
3. Cliquez sur "New app"
4. Sélectionnez :
   - **Repository** : `VOTRE_USERNAME/CCV-geolocalisation`
   - **Branch** : `main`
   - **Main file path** : `geolocation_game.py`
5. Cliquez sur "Deploy!"

Votre application sera disponible à une URL comme :
`https://VOTRE_USERNAME-ccv-geolocalisation.streamlit.app`

## 🔧 Configuration pour Streamlit Cloud

Streamlit Cloud lira automatiquement le fichier `requirements.txt` pour installer les dépendances.

## ⚠️ Important

- Les images dans le dossier `images/` seront publiques si le dépôt est public
- Assurez-vous que les photos ne contiennent pas d'informations sensibles
- Le fichier PowerPoint n'est pas inclus dans le dépôt (voir `.gitignore`)

## 🔄 Mettre à jour l'application

Après chaque modification :

```bash
cd /Users/chateau/dev/sandbox/CCV
git add .
git commit -m "Description de vos modifications"
git push
```

Streamlit Cloud redéploiera automatiquement votre application !
