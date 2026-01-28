#!/usr/bin/env python3
"""
Extraction unifiée FOCUS (FR + CH + BW en Z14, Monde en Z8)
"""
import sqlite3
import os
import math

import json

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "map_config.json")
    with open(config_path, "r") as f:
        return json.load(f)

def lon2tile(lon, zoom):
    return int((lon + 180.0) / 360.0 * (2.0 ** zoom))

def lat2tile(lat, zoom):
    return int((1.0 - math.log(math.tan(lat * math.pi / 180.0) + 1.0 / math.cos(lat * math.pi / 180.0)) / math.pi) / 2.0 * (2.0 ** zoom))

def get_tile_range(zoom, bbox):
    x_min = lon2tile(bbox[0], zoom)
    x_max = lon2tile(bbox[2], zoom)
    y_min = lat2tile(bbox[3], zoom)
    y_max = lat2tile(bbox[1], zoom)
    return x_min, x_max, y_min, y_max

def extract_focus(input_file, output_file):
    print(f"🚀 Démarrage de l'extraction vers {output_file}...", flush=True)
    config = load_config()
    bbox_focus = config["bbox"]
    
    if os.path.exists(output_file):
        os.remove(output_file)

    # Zone LARGE pour le fond de carte (Z0-8)
    bbox_world = [-180, -85, 180, 85]

    conn = sqlite3.connect(output_file)
    cursor = conn.cursor()

    # Structure
    cursor.execute('CREATE TABLE metadata (name text, value text)')
    cursor.execute('CREATE TABLE tiles (zoom_level integer, tile_column integer, tile_row integer, tile_data blob)')
    cursor.execute('CREATE UNIQUE INDEX tile_index on tiles (zoom_level, tile_column, tile_row)')

    # Attacher la source
    cursor.execute(f"ATTACH DATABASE '{input_file}' AS source")

    # Metadata
    print("📝 Copie des métadonnées...", flush=True)
    cursor.execute("INSERT INTO metadata SELECT * FROM source.metadata")
    cursor.execute("INSERT OR REPLACE INTO metadata VALUES ('name', 'Unified FR-CH-BW Focus Z14')")
    cursor.execute("INSERT OR REPLACE INTO metadata VALUES ('description', 'Z0-8 World, Z9-14 FR+CH+BW Only')")
    cursor.execute("INSERT OR REPLACE INTO metadata VALUES ('maxzoom', '14')")
    conn.commit()

    # 1. Zooms 0 à 8 (Monde / Zone très large)
    print("📥 Extraction Zooms 0-8 (Monde)...", flush=True)
    for z in range(0, 9):
        cursor.execute(f"INSERT OR IGNORE INTO tiles SELECT * FROM source.tiles WHERE zoom_level = ?", (z,))
        print(f"   Zoom {z} copié.", flush=True)
        conn.commit()

    # 2. Zooms 9 à 14 (Zone FOCUS uniquement)
    print("🎯 Extraction Zooms 9-14 (FR + CH + BW uniquement)...", flush=True)
    for z in range(9, 15):
        xm, xM, ym, yM = get_tile_range(z, bbox_focus)
        # MBTiles uses TMS
        tm_y_min = (2**z - 1) - yM
        tm_y_max = (2**z - 1) - ym
        
        cursor.execute(f"""
            INSERT OR IGNORE INTO tiles 
            SELECT * FROM source.tiles 
            WHERE zoom_level = ? AND tile_column BETWEEN ? AND ? AND tile_row BETWEEN ? AND ?
        """, (z, xm, xM, tm_y_min, tm_y_max))
        print(f"   Zoom {z} focus copié.", flush=True)
        conn.commit()

    cursor.execute("DETACH DATABASE source")
    conn.close()
    
    size_gb = os.path.getsize(output_file) / (1024*1024*1024)
    print(f"🎉 Fichier final FOCUS prêt : {output_file} ({size_gb:.2f} GB)", flush=True)

if __name__ == '__main__':
    # On repart du fichier source complet pour être sûr de tout avoir
    # Source NAS pour être sûr des données
    source = "/mnt/nas/tmp/planet_openfreemap.mbtiles"
    target = "unified_focus_z14.mbtiles"
    extract_focus(source, target)
