# Serveur de Cartes (Self-Hosted)

Ce projet héberge localement des cartes vectorielles (MBTiles) avec deux serveurs de tuiles (**Martin** et **Tileserver-GL**) et une interface web.

## Démarrage Rapide

### Prérequis
- Docker & Docker Compose
- Python 3 (pour la génération des cartes)
- Espace disque suffisant (~10GB)

### Lancement
```bash
docker compose up -d
```

3 conteneurs :
- **Nginx (Port 8257)** : Interface web (`http://localhost:8257`)
- **Tileserver-GL (Port 8258)** : Serveur de tuiles avec rendu
- **Martin (Port 3233)** : Serveur de tuiles rapide (Rust)

## Assets (`setup_assets.sh`)

Déploie les polices et sprites depuis `data/maps/` vers `public/` :
```bash
./setup_assets.sh
```
- **Polices** : Dézippe `data/maps/fonts/*.zip` vers `public/fonts/`
- **Sprites** : Copie `data/maps/sprites/` vers `public/sprites/`

## Génération des Cartes

### Script : `extract_unified_focus_z14.py`

Situé dans `data/maps/`, il extrait une zone régionale (France, Corse, Luxembourg, Suisse, Baden-Württemberg) en zoom détaillé Z0-14, et le reste du monde en Z0-8.

```bash
cd data/maps
python3 extract_unified_focus_z14.py
```

### Configuration (`map_config.json`)
Définit la zone géographique (Bounding Box) et les niveaux de zoom.

### Fichier de sortie
- `unified_focus_z14.mbtiles` : Carte complète avec tous les calques.

### Source des données
Le script attend un fichier Planet MBTiles. Sources :
- [OpenMapTiles](https://openmaptiles.org/downloads/planet/)
- [Geofabrik](https://download.geofabrik.de/) (extraits régionaux)

## Architecture Docker

- **`web` (Nginx)** : Sert les pages HTML et les assets statiques (styles, fonts, sprites).
- **`tileserver`** : Configuré via `config.json`, sert les tuiles TMS/XYZ.
- **`martin`** : Sert les tuiles vectorielles depuis `unified_focus_z14.mbtiles`.
