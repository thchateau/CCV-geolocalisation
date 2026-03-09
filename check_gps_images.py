#!/usr/bin/env python3
"""
Script pour lister les images avec coordonnées GPS dans leurs métadonnées EXIF
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pathlib import Path

def get_gps_info(image_path):
    """Extrait les coordonnées GPS des métadonnées EXIF de l'image"""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif() if hasattr(image, '_getexif') else None
        
        if not exif_data:
            return None
        
        gps_info = {}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == 'GPSInfo':
                for gps_tag in value:
                    gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    gps_info[gps_tag_name] = value[gps_tag]
        
        if not gps_info or 'GPSLatitude' not in gps_info or 'GPSLongitude' not in gps_info:
            return None
        
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
        
    except Exception as e:
        return None

def main():
    """Liste toutes les images avec coordonnées GPS"""
    images_dir = Path("images")
    
    if not images_dir.exists():
        print(f"❌ Le dossier '{images_dir}' n'existe pas")
        return
    
    # Extensions d'images supportées
    extensions = ['*.jpeg', '*.jpg', '*.JPEG', '*.JPG', '*.png', '*.PNG']
    image_files = []
    for ext in extensions:
        image_files.extend(images_dir.glob(ext))
    
    if not image_files:
        print(f"❌ Aucune image trouvée dans '{images_dir}'")
        return
    
    print(f"\n📁 Analyse du dossier: {images_dir}")
    print(f"📊 Nombre total d'images: {len(image_files)}\n")
    print("=" * 80)
    
    images_with_gps = []
    images_without_gps = []
    
    for img_path in sorted(image_files):
        gps_coords = get_gps_info(img_path)
        
        if gps_coords:
            images_with_gps.append((img_path.name, gps_coords))
            print(f"✅ {img_path.name}")
            print(f"   📍 Latitude: {gps_coords[0]:.6f}")
            print(f"   📍 Longitude: {gps_coords[1]:.6f}")
            print(f"   🔗 https://www.openstreetmap.org/?mlat={gps_coords[0]}&mlon={gps_coords[1]}&zoom=15")
            print()
        else:
            images_without_gps.append(img_path.name)
    
    # Résumé
    print("=" * 80)
    print(f"\n📈 RÉSUMÉ:")
    print(f"   ✅ Images avec GPS: {len(images_with_gps)}")
    print(f"   ❌ Images sans GPS: {len(images_without_gps)}")
    
    if images_without_gps:
        print(f"\n⚠️  Images sans coordonnées GPS:")
        for img_name in images_without_gps:
            print(f"   • {img_name}")
    
    if images_with_gps:
        print(f"\n✨ {len(images_with_gps)} image(s) utilisable(s) pour le jeu de géolocalisation!")
    else:
        print("\n⚠️  Aucune image avec GPS trouvée. Le jeu ne pourra pas démarrer.")

if __name__ == "__main__":
    main()
