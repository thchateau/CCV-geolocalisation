import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import random
from pathlib import Path
from geopy.distance import geodesic

# Configuration de la page
st.set_page_config(
    page_title="Jeu de Géolocalisation - Combronde",
    page_icon="🗺️",
    layout="wide"
)

# CSS personnalisé avec les couleurs du logo (marron, vert olive, orange)
st.markdown("""
    <style>
    /* Couleurs principales inspirées du logo Combronde */
    :root {
        --marron: #6B3E3E;
        --vert-olive: #9CA76C;
        --orange: #E87722;
        --beige: #F5F1E8;
    }
    
    /* En-tête personnalisé */
    .main-header {
        background: linear-gradient(135deg, var(--vert-olive) 0%, var(--marron) 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: var(--beige);
        text-align: center;
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    /* Boutons personnalisés */
    .stButton > button {
        background: linear-gradient(135deg, var(--orange) 0%, var(--marron) 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    
    /* Cartes de sections */
    .section-card {
        background-color: var(--beige);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid var(--orange);
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Messages personnalisés */
    .stAlert {
        border-radius: 10px;
    }
    
    /* Distance */
    .distance-display {
        background: linear-gradient(135deg, var(--marron) 0%, var(--vert-olive) 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    /* Logo container */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

def get_gps_info(image_path):
    """Extrait les coordonnées GPS des métadonnées EXIF de l'image ou génère des coordonnées fictives"""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif() if hasattr(image, '_getexif') else None
        
        if exif_data:
            gps_info = {}
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == 'GPSInfo':
                    for gps_tag in value:
                        gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                        gps_info[gps_tag_name] = value[gps_tag]
            
            if gps_info:
                # Conversion des coordonnées GPS
                def convert_to_degrees(value):
                    d, m, s = value
                    return d + (m / 60.0) + (s / 3600.0)
                
                lat = convert_to_degrees(gps_info['GPSLatitude'])
                if gps_info['GPSLatitudeRef'] == 'S':
                    lat = -lat
                
                lon = convert_to_degrees(gps_info['GPSLongitude'])
                if gps_info['GPSLongitudeRef'] == 'W':
                    lon = -lon
                
                return (lat, lon)
        
        # Si pas de GPS, générer des coordonnées aléatoires autour de Combronde
        import hashlib
        hash_val = int(hashlib.md5(str(image_path).encode()).hexdigest(), 16)
        random.seed(hash_val)
        lat = 45.9803 + random.uniform(-0.05, 0.05)  # ±5km environ
        lon = 3.0889 + random.uniform(-0.07, 0.07)
        return (lat, lon)
        
    except Exception as e:
        st.error(f"Erreur lors de la lecture de l'image: {e}")
        return None

def init_game():
    """Initialise une nouvelle partie"""
    images_dir = Path("images")
    image_files = list(images_dir.glob("*.jpeg")) + list(images_dir.glob("*.jpg")) + \
                  list(images_dir.glob("*.JPEG")) + list(images_dir.glob("*.JPG"))
    
    if not image_files:
        st.error("Aucune image trouvée dans le dossier 'images'")
        return
    
    # Choisir une image aléatoire
    selected_image = random.choice(image_files)
    gps_coords = get_gps_info(selected_image)
    
    if gps_coords:
        st.session_state.current_image = str(selected_image)
        st.session_state.target_coords = gps_coords
        st.session_state.game_started = True
        st.session_state.game_won = False
        st.session_state.distance = None
        st.session_state.marker_position = [45.9803, 3.0889]  # Réinitialiser la position du marqueur
        st.session_state.map_zoom = 13  # Réinitialiser le zoom
        st.session_state.map_key = 0  # Réinitialiser la clé de la carte
    else:
        st.error("Erreur lors du chargement de l'image")

# Initialisation de la session
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
    st.session_state.game_won = False
    st.session_state.distance = None

# Interface principale
# Logo et en-tête
col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
with col_logo2:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)

st.markdown("""
    <div class="main-header">
        <h1>🗺️ Jeu de Géolocalisation</h1>
        <p>Trouvez où cette photo a été prise sur la carte de Combronde!</p>
    </div>
""", unsafe_allow_html=True)

# Bouton pour démarrer/redémarrer
if not st.session_state.game_started or st.session_state.game_won:
    if st.button("🎮 Nouvelle Partie" if st.session_state.game_won else "🎮 Démarrer"):
        init_game()
        st.rerun()

if st.session_state.game_started and not st.session_state.game_won:
    # Affichage de l'image
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📸 Photo mystère")
    image = Image.open(st.session_state.current_image)
    st.image(image, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Carte en dessous
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("🗺️ Carte OpenStreetMap")
    st.write("🖱️ Cliquez sur la carte pour positionner la loupe rouge")
    
    # Initialiser la position du marqueur si pas déjà fait
    if 'marker_position' not in st.session_state:
        st.session_state.marker_position = [45.9803, 3.0889]
    if 'map_zoom' not in st.session_state:
        st.session_state.map_zoom = 13
    
    # Création de la carte centrée sur le marqueur
    m = folium.Map(
        location=st.session_state.marker_position,
        zoom_start=st.session_state.map_zoom,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri'
    )
    
    # Ajout d'un marqueur mobile (loupe rouge)
    folium.Marker(
        location=st.session_state.marker_position,
        icon=folium.Icon(color='red', icon='search'),
        draggable=False
    ).add_to(m)
    
    # Affichage de la carte avec click listener
    map_data = st_folium(
        m,
        width=None,
        height=600,
        returned_objects=["last_clicked", "zoom"],
        key=f"map_{st.session_state.get('map_key', 0)}"
    )
    
    # Mettre à jour la position du marqueur si l'utilisateur a cliqué
    if map_data and map_data.get('last_clicked') is not None:
        new_lat = map_data['last_clicked']['lat']
        new_lng = map_data['last_clicked']['lng']
        
        # Vérifier que la position a changé pour éviter les boucles infinies
        if (st.session_state.marker_position[0] != new_lat or 
            st.session_state.marker_position[1] != new_lng):
            st.session_state.marker_position = [new_lat, new_lng]
            
            # Sauvegarder le niveau de zoom actuel
            if map_data.get('zoom'):
                st.session_state.map_zoom = map_data['zoom']
            
            st.session_state.map_key = st.session_state.get('map_key', 0) + 1
            st.rerun()
    
    # Bouton de validation
    if st.button("📍 C'est ICI!", type="primary"):
        user_coords = tuple(st.session_state.marker_position)
        
        # Calcul de la distance
        distance = geodesic(st.session_state.target_coords, user_coords).meters
        st.session_state.distance = distance
        
        if distance < 50:
            st.session_state.game_won = True
            st.rerun()
    
    # Affichage de la distance si une tentative a été faite
    if st.session_state.distance is not None:
        st.markdown(f"""
            <div class="distance-display">
                📏 Distance: {st.session_state.distance:.2f} mètres
            </div>
        """, unsafe_allow_html=True)
        if st.session_state.distance >= 50:
            st.warning("🔍 Trop loin! Continuez à chercher...")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Écran de victoire
if st.session_state.game_won:
    st.balloons()
    st.markdown("""
        <div class="section-card" style="border-left-color: var(--vert-olive); background: linear-gradient(135deg, #f0f9e8 0%, var(--beige) 100%);">
            <h2 style="color: var(--vert-olive); text-align: center;">🎉 Bravo! Vous avez gagné! 🎉</h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="distance-display" style="background: linear-gradient(135deg, var(--vert-olive) 0%, var(--orange) 100%);">
            🎯 Vous étiez à seulement {st.session_state.distance:.2f} mètres de la position réelle!
        </div>
    """, unsafe_allow_html=True)
    
    # Afficher la vraie position
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📍 Position réelle")
    victory_map = folium.Map(
        location=st.session_state.target_coords,
        zoom_start=17,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri'
    )
    folium.Marker(
        location=st.session_state.target_coords,
        popup='Position réelle',
        icon=folium.Icon(color='green', icon='check')
    ).add_to(victory_map)
    st_folium(victory_map, width=None, height=400)
    st.markdown('</div>', unsafe_allow_html=True)
