# 🗺️ Jeu de Géolocalisation - Combronde

Un jeu interactif de géolocalisation développé avec Streamlit et OpenStreetMap. Trouvez où les photos ont été prises sur la carte de Combronde (Puy-de-Dôme) !

![Logo Combronde](logo.png)

## 🎮 Fonctionnalités

- 📸 Affichage d'une photo mystère
- 🗺️ Carte OpenStreetMap interactive (vue satellite)
- 🖱️ Cliquez sur la carte pour positionner votre choix
- 📏 Calcul de la distance entre votre choix et la position réelle
- 🎯 Gagnez si vous êtes à moins de 50 mètres !
- 🎨 Interface personnalisée aux couleurs de Combronde

## 🚀 Installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/VOTRE_USERNAME/CCV.git
cd CCV
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Ajoutez vos photos dans le dossier `images/` (avec coordonnées GPS dans les métadonnées EXIF)

## 🎯 Utilisation

Lancez l'application :
```bash
streamlit run geolocation_game.py
```

Puis ouvrez votre navigateur à l'adresse indiquée (généralement http://localhost:8501)

## 📋 Prérequis

- Python 3.7+
- Photos avec coordonnées GPS dans les métadonnées EXIF

## 🛠️ Technologies utilisées

- [Streamlit](https://streamlit.io/) - Framework d'application web
- [Folium](https://python-visualization.github.io/folium/) - Cartes interactives
- [Pillow](https://pillow.readthedocs.io/) - Traitement d'images
- [Geopy](https://geopy.readthedocs.io/) - Calcul de distances géographiques

## 📝 License

Ce projet est open source.

## 🏛️ À propos

Développé pour la commune de Combronde (Puy-de-Dôme, France).
