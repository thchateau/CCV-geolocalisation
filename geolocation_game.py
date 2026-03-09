import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import random
from pathlib import Path
from geopy.distance import geodesic
import piexif
import io

# Configuration de la page
st.set_page_config(
    page_title="Combronde c'est vous ! Connaissez vous votre commune ?",
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
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: 3px solid var(--orange);
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Cadres pour images */
    .stImage {
        border: 4px solid var(--marron);
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        overflow: hidden;
    }
    
    /* Cadres pour cartes Folium */
    iframe {
        border: 4px solid var(--vert-olive) !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
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
    
    /* Admin button */
    .admin-icon {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 999;
        font-size: 1.5rem;
        cursor: pointer;
        background: var(--marron);
        color: white;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

def get_gps_info(image_path):
    """Extrait les coordonnées GPS des métadonnées EXIF de l'image"""
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
            
            if gps_info and 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
                # Conversion des coordonnées GPS
                def convert_to_degrees(value):
                    d, m, s = value
                    return d + (m / 60.0) + (s / 3600.0)
                
                lat = convert_to_degrees(gps_info['GPSLatitude'])
                if gps_info.get('GPSLatitudeRef') == 'S':
                    lat = -lat
                
                lon = convert_to_degrees(gps_info['GPSLongitude'])
                if gps_info.get('GPSLongitudeRef') == 'W':
                    lon = -lon
                
                return (lat, lon)
        
        # Pas de coordonnées GPS trouvées
        return None
        
    except Exception as e:
        return None

def set_gps_info(image_path, lat, lon):
    """Ajoute les coordonnées GPS aux métadonnées EXIF d'une image"""
    try:
        # Convertir les coordonnées décimales en format GPS
        def to_deg(value, is_lat):
            abs_value = abs(value)
            deg = int(abs_value)
            min_float = (abs_value - deg) * 60
            min_val = int(min_float)
            sec = (min_float - min_val) * 60
            
            return (deg, min_val, sec)
        
        lat_deg = to_deg(lat, True)
        lon_deg = to_deg(lon, False)
        
        lat_ref = 'N' if lat >= 0 else 'S'
        lon_ref = 'E' if lon >= 0 else 'W'
        
        # Créer les données GPS
        gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef: lat_ref,
            piexif.GPSIFD.GPSLatitude: [(lat_deg[0], 1), (lat_deg[1], 1), (int(lat_deg[2] * 100), 100)],
            piexif.GPSIFD.GPSLongitudeRef: lon_ref,
            piexif.GPSIFD.GPSLongitude: [(lon_deg[0], 1), (lon_deg[1], 1), (int(lon_deg[2] * 100), 100)],
        }
        
        # Charger l'image et ses EXIF existants
        image = Image.open(image_path)
        
        try:
            exif_data = image.info.get('exif')
            if exif_data:
                exif_dict = piexif.load(exif_data)
            else:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        except:
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        
        exif_dict['GPS'] = gps_ifd
        exif_bytes = piexif.dump(exif_dict)
        
        # Convertir en RGB si nécessaire (pour JPEG)
        if image.mode in ('RGBA', 'P', 'LA'):
            image = image.convert('RGB')
        
        # Sauvegarder l'image avec les nouvelles coordonnées
        image.save(image_path, "JPEG", exif=exif_bytes, quality=95)
        return True
        
    except Exception as e:
        st.error(f"Erreur lors de l'ajout des coordonnées GPS: {e}")
        return False

def check_admin_password(password):
    """Vérifie le mot de passe admin"""
    return password == "Cpt2Combronde63!"

def init_game():
    """Initialise une nouvelle partie"""
    images_dir = Path("images")
    image_files = list(images_dir.glob("*.jpeg")) + list(images_dir.glob("*.jpg")) + \
                  list(images_dir.glob("*.JPEG")) + list(images_dir.glob("*.JPG"))
    
    if not image_files:
        st.error("Aucune image trouvée dans le dossier 'images'")
        return
    
    # Filtrer les images qui ont des coordonnées GPS valides
    valid_images = []
    for img_file in image_files:
        gps_coords = get_gps_info(img_file)
        if gps_coords:
            valid_images.append((img_file, gps_coords))
    
    if not valid_images:
        st.error("Aucune image avec coordonnées GPS trouvée dans le dossier 'images'")
        return
    
    # Choisir une image aléatoire parmi celles avec GPS
    selected_image, gps_coords = random.choice(valid_images)
    
    st.session_state.current_image = str(selected_image)
    st.session_state.target_coords = gps_coords
    st.session_state.game_started = True
    st.session_state.game_won = False
    st.session_state.distance = None
    st.session_state.marker_position = [45.9803, 3.0889]  # Réinitialiser la position du marqueur
    st.session_state.map_zoom = 13  # Réinitialiser le zoom
    st.session_state.map_key = 0  # Réinitialiser la clé de la carte

# Initialisation de la session
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
    st.session_state.game_won = False
    st.session_state.distance = None
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'show_admin_login' not in st.session_state:
    st.session_state.show_admin_login = False

# Interface principale
# Logo et en-tête
col_logo1, col_logo2, col_logo3 = st.columns([1, 1, 1])
with col_logo2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)

st.markdown("""
    <div class="main-header">
        <h1>🗺️ Combrondaires : connaissez-vous votre commune ?</h1>
        <p>Trouvez où cette photo a été prise sur la carte de Combronde!</p>
    </div>
""", unsafe_allow_html=True)

# Bouton admin dans le coin supérieur droit
col_admin, col_spacer = st.columns([20, 1])
with col_spacer:
    if st.button("⚙️", help="Administration"):
        st.session_state.show_admin_login = True

# Interface Admin
if st.session_state.show_admin_login:
    with st.sidebar:
        st.title("⚙️ Administration")
        
        if not st.session_state.admin_logged_in:
            st.subheader("🔐 Connexion")
            password = st.text_input("Mot de passe:", type="password", key="admin_password")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Connexion"):
                    if check_admin_password(password):
                        st.session_state.admin_logged_in = True
                        st.rerun()
                    else:
                        st.error("Mot de passe incorrect!")
            with col2:
                if st.button("Annuler"):
                    st.session_state.show_admin_login = False
                    st.rerun()
        else:
            st.success("✅ Connecté en tant qu'admin")
            
            if st.button("🚪 Déconnexion"):
                st.session_state.admin_logged_in = False
                st.session_state.show_admin_login = False
                st.rerun()
            
            st.divider()
            
            # Import d'image
            st.subheader("📤 Importer une image")
            uploaded_file = st.file_uploader("Choisir une image", type=['jpg', 'jpeg', 'png'], key="upload")
            
            if uploaded_file:
                # Sauvegarder temporairement l'image
                temp_path = Path("images") / uploaded_file.name
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
                
                # Vérifier si l'image a des coordonnées GPS
                gps_coords = get_gps_info(temp_path)
                
                if gps_coords:
                    st.success(f"✅ Image avec GPS: {gps_coords[0]:.6f}, {gps_coords[1]:.6f}")
                    if st.button("💾 Sauvegarder l'image"):
                        st.success(f"Image '{uploaded_file.name}' ajoutée avec succès!")
                else:
                    st.warning("⚠️ Cette image n'a pas de coordonnées GPS")
                    st.info("📍 Cliquez sur la carte pour définir la position")
                    
                    # Initialiser la position pour la géolocalisation manuelle
                    if 'admin_marker_position' not in st.session_state:
                        st.session_state.admin_marker_position = [45.9803, 3.0889]
                    if 'admin_map_zoom' not in st.session_state:
                        st.session_state.admin_map_zoom = 13
                    
                    # Carte pour définir la position
                    admin_map = folium.Map(
                        location=st.session_state.admin_marker_position,
                        zoom_start=st.session_state.admin_map_zoom,
                        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                        attr='Esri'
                    )
                    
                    folium.Marker(
                        location=st.session_state.admin_marker_position,
                        icon=folium.Icon(color='blue', icon='info-sign'),
                        draggable=False
                    ).add_to(admin_map)
                    
                    admin_map_data = st_folium(
                        admin_map,
                        width=None,
                        height=400,
                        returned_objects=["last_clicked", "zoom"],
                        key=f"admin_map_{st.session_state.get('admin_map_key', 0)}"
                    )
                    
                    # Mise à jour de la position du marqueur admin
                    if admin_map_data and admin_map_data.get('last_clicked') is not None:
                        new_lat = admin_map_data['last_clicked']['lat']
                        new_lng = admin_map_data['last_clicked']['lng']
                        
                        if (st.session_state.admin_marker_position[0] != new_lat or 
                            st.session_state.admin_marker_position[1] != new_lng):
                            st.session_state.admin_marker_position = [new_lat, new_lng]
                            
                            if admin_map_data.get('zoom'):
                                st.session_state.admin_map_zoom = admin_map_data['zoom']
                            
                            st.session_state.admin_map_key = st.session_state.get('admin_map_key', 0) + 1
                            st.rerun()
                    
                    st.write(f"📍 Position: {st.session_state.admin_marker_position[0]:.6f}, {st.session_state.admin_marker_position[1]:.6f}")
                    
                    if st.button("💾 C'est ICI - Sauvegarder avec cette position"):
                        # Ajouter les coordonnées GPS à l'image
                        if set_gps_info(temp_path, st.session_state.admin_marker_position[0], st.session_state.admin_marker_position[1]):
                            st.success(f"✅ Image '{uploaded_file.name}' sauvegardée avec GPS!")
                            st.session_state.admin_marker_position = [45.9803, 3.0889]
                            st.session_state.admin_map_key = 0
                        else:
                            st.error("❌ Erreur lors de la sauvegarde")

# Bouton pour démarrer/redémarrer
if not st.session_state.game_started or st.session_state.game_won:
    if st.button("🎮 Nouvelle Partie" if st.session_state.game_won else "🎮 Démarrer"):
        init_game()
        st.rerun()

if st.session_state.game_started and not st.session_state.game_won:
    # Layout responsive : côte à côte sur grands écrans, empilé sur petits écrans
    col_image, col_map = st.columns([1, 1], gap="medium")
    
    # Colonne Image
    with col_image:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📸 Photo mystère")
        image = Image.open(st.session_state.current_image)
        st.image(image, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Affichage de la distance si une tentative a été faite
        if st.session_state.distance is not None:
            st.markdown(f"""
                <div class="distance-display">
                    📏 Distance: {st.session_state.distance:.2f} mètres
                </div>
            """, unsafe_allow_html=True)
            if st.session_state.distance >= 50:
                st.warning("🔍 Trop loin! Continuez à chercher...")
            else:
                st.info("🎯 Très proche! Affinez votre position!")
    
    # Colonne Carte
    with col_map:
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
            height=500,
            returned_objects=["last_clicked", "zoom"],
            key=f"map_{st.session_state.get('map_key', 0)}"
        )
        
        # Afficher les coordonnées du marqueur en temps réel
        st.caption(f"📍 Position du marqueur: {st.session_state.marker_position[0]:.6f}, {st.session_state.marker_position[1]:.6f}")
        
        # Bouton de validation centré
        if st.button("📍 C'est ICI!", type="primary", use_container_width=True):
            user_coords = tuple(st.session_state.marker_position)
            
            # Calcul de la distance
            distance = geodesic(st.session_state.target_coords, user_coords).meters
            st.session_state.distance = distance
            
            if distance < 50:
                st.session_state.game_won = True
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
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
