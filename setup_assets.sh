#!/bin/bash

# Configuration
MASTER_FONTS_DIR="data/maps/fonts"
MASTER_SPRITES_DIR="data/maps/sprites"
PUBLIC_FONTS_DIR="public/fonts"
PUBLIC_SPRITES_DIR="public/sprites"

echo "🚀 Déploiement des assets vers $PUBLIC_FONTS_DIR et $PUBLIC_SPRITES_DIR..."

# 1. Gestion des Sprites
echo "🎨 Déploiement des sprites..."
if [ -d "$MASTER_SPRITES_DIR" ]; then
    mkdir -p "$PUBLIC_SPRITES_DIR"
    cp -v "$MASTER_SPRITES_DIR"/* "$PUBLIC_SPRITES_DIR/"
else
    echo "⚠️ Warning: Dossier master sprites $MASTER_SPRITES_DIR non trouvé."
fi

# 2. Gestion des Polices
echo "🔤 Déploiement des polices..."
if [ -d "$MASTER_FONTS_DIR" ]; then
    mkdir -p "$PUBLIC_FONTS_DIR"
    # Parcourir tous les fichiers zip dans le dossier des polices master
    find "$MASTER_FONTS_DIR" -maxdepth 1 -name "*.zip" | while read -r zipfile; do
        fontname=$(basename "$zipfile" .zip)
        target_dir="$PUBLIC_FONTS_DIR/$fontname"
        echo "📦 Extraction de $fontname..."
        mkdir -p "$target_dir"
        unzip -o -q "$zipfile" -d "$target_dir"
    done
    
    # Copier fontstacks.json
    if [ -f "$MASTER_FONTS_DIR/fontstacks.json" ]; then
        cp -v "$MASTER_FONTS_DIR/fontstacks.json" "$PUBLIC_FONTS_DIR/"
    fi
else
    echo "❌ Erreur: Le dossier master fonts $MASTER_FONTS_DIR n'existe pas."
    exit 1
fi

echo "✨ Terminé ! Les dossiers publics sont à jour."
