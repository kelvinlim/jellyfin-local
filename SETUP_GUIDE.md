# Jellyfin Podman Setup Guide

## Quick Start

```bash
cd /home/kelvin/Jellyfin
podman compose up -d
```

Access Jellyfin at `http://localhost:8096`

---

## Complete Setup Instructions

### 1. Prerequisites

Ensure you have installed:

```bash
# Install Podman
sudo apt install podman podman-compose  # Ubuntu/Debian
# or
sudo dnf install podman podman-compose  # Fedora/RHEL

# Verify installation
podman --version
podman-compose --version
```

### 2. Directory Structure Overview

Your Jellyfin setup uses three main directory categories:

```
/home/kelvin/Jellyfin/
├── config/          → Jellyfin configuration (persisted)
├── cache/           → Thumbnails, transcodes, metadata (can be cleared)
├── Media/           → Your media library
│   ├── Movies/
│   ├── Music/
│   └── Shows/
└── docker-compose.yml
```

**Key Principle**: Keep these directories separate for easy management and backups.

### 3. Understanding docker-compose.yml

The `docker-compose.yml` file defines how the container runs:

```yaml
services:
  jellyfin:
    image: jellyfin/jellyfin              # Official Jellyfin image
    container_name: jellyfin              # Container name
    network_mode: host                    # Direct host network access
    volumes:
      - ./config:/config                  # Persist config
      - ./cache:/cache                    # Persist cache/transcodes
      - /home/kelvin/Jellyfin/Media:/media  # Media library
    restart: 'unless-stopped'             # Auto-restart on failure
```

**Why these settings?**
- `network_mode: host` - Direct access to port 8096, best performance
- Volume mounts - Persist settings and data across container restarts
- `restart: unless-stopped` - Survives system reboots automatically

### 4. Container Volume Mapping

When Jellyfin runs in the container, paths are remapped:

| **Host Location** | **Container Path** | **Purpose** |
|---|---|---|
| `./config` | `/config` | Jellyfin settings & database |
| `./cache` | `/cache` | Thumbnails, metadata, transcodes |
| `/home/kelvin/Jellyfin/Media` | `/media` | Your media library |

**Important**: When adding libraries in Jellyfin's web UI, use the **container paths** (`/media/Shows`, `/media/Movies`), not the host paths.

### 5. Folder Organization Requirements

#### Media Library Structure

Jellyfin requires specific folder structures to properly recognize content:

##### TV Shows
```
Media/Shows/Show Name/Season 01/Show Name - s01e01 - Title.mkv
```

Example with existing shows:
```
Media/Shows/
├── Fringe/
│   ├── Season 01/
│   │   ├── Fringe - s01e01 - Pilot.mkv
│   │   ├── Fringe - s01e02 - The Same Old Story.mkv
│   │   └── ...
│   └── Season 02/
│       └── ...
└── Battlestar Galactica/
    └── Season 01/
        └── ...
```

##### Movies
```
Media/Movies/Movie Name (Year)/Movie Name (Year).mkv
```

Example:
```
Media/Movies/
└── The Motorcycle Diaries (2004)/
    └── The Motorcycle Diaries (2004).mkv
```

#### Config Folder Contents

This folder persists all settings (backed up automatically):

- **config/config/** - Configuration files (database.xml, encoding.xml, network settings)
- **config/data/** - Application data (playlists, device info)
- **config/log/** - Application logs (useful for debugging)
- **config/metadata/** - Cached metadata organized by genre and studio
- **config/plugins/** - Plugin configurations

#### Cache Folder Contents

This can be safely deleted (regenerates on access):

- **cache/images/** - Resized thumbnails and artwork
- **cache/imagesbyname/** - Image name index
- **cache/omdb/** - OMDB metadata cache (JSON files)
- **cache/transcodes/** - Temporary video transcode files

### 6. Running Jellyfin

#### Start the Container
```bash
cd /home/kelvin/Jellyfin
podman compose up -d
```

The `-d` flag runs it in the background (detached mode).

#### Verify Container is Running
```bash
podman ps | grep jellyfin
```

You should see the `jellyfin` container listed.

#### View Real-Time Logs
```bash
podman logs -f jellyfin
```

Press `Ctrl+C` to exit logs.

#### Stop the Container
```bash
podman compose down
```

This stops the container but preserves all data in `config/` and `cache/`.

#### Restart the Container
```bash
podman compose restart
```

### 7. Initial Jellyfin Configuration

1. **Open Browser**: Navigate to `http://localhost:8096`

2. **Create Admin Account**
   - Set username and password
   - This becomes your main admin user

3. **Add Media Libraries**
   - Click **Settings** → **Libraries**
   - Click **+** to add a new library
   - Select content type:
     - TV Shows
     - Movies
     - Music
   - Click **Add Folders** and select:
     - `/media/Shows` for TV shows
     - `/media/Movies` for movies
     - `/media/Music` for music
   - Click **OK**

4. **Configure Display**
   - **Settings** → **Display**
   - Set language, date/time format, etc.

5. **Media Playback Settings**
   - **Settings** → **Playback**
   - Configure transcoding if needed
   - Set default subtitle language

6. **Metadata & Search**
   - **Settings** → **Libraries**
   - Configure metadata providers (TMDB, OMDB, etc.)

### 8. Adding Media to Your Library

#### Using the Python Organize Scripts

Two helper scripts are included:

- **organize_shows.py** - Reorganize shows into season folders
- **organize_fringe.py** - Fringe-specific folder reorganization

Example usage:
```bash
python organize_shows.py
```

These scripts help move files into the required folder structure.

#### Manual Organization

If organizing manually, ensure files follow this pattern:

```
Show Name - s01e01 - Episode Title.mkv
Show Name - s01e02 - Episode Title.mkv
```

The season number (s01, s02) and episode number (e01, e02) help Jellyfin identify episodes correctly.

### 9. Common Operations

#### Clear Cache (Freeing Disk Space)
```bash
rm -rf ./cache/*
```
Jellyfin will regenerate thumbnails and metadata on next access (slower initially).

#### Access Container Shell (For Debugging)
```bash
podman exec -it jellyfin bash
```

#### Check Container Resource Usage
```bash
podman stats jellyfin
```

#### View All Container Info
```bash
podman compose ps -a
```

#### Restart and Rebuild Container
```bash
podman compose down
podman compose up -d
```

### 10. Backup & Restore

#### Backup Configuration
```bash
tar -czf jellyfin-backup-$(date +%Y%m%d).tar.gz ./config/
```

#### Restore Configuration
```bash
tar -xzf jellyfin-backup-YYYYMMDD.tar.gz
```

**Note**: Cache (`./cache/`) doesn't need backing up as it's regenerated.

### 11. Troubleshooting

#### Container Won't Start
```bash
podman logs jellyfin
```
Check the error message. Common issues:
- Port 8096 already in use
- Permission issues on directories

#### Port 8096 Already in Use
```bash
sudo lsof -i :8096
# Kill the process using it, or use a different port
```

#### Media Libraries Not Found
- Ensure you're using container paths: `/media/Shows`, `/media/Movies`
- Not host paths: `/home/kelvin/Jellyfin/Media/Shows`
- Check folder permissions (container user must read them)

#### Slow Performance
- Ensure shows are in the correct folder structure
- Clear cache: `rm -rf ./cache/*`
- Check disk I/O: `iotop` or `iostat`

#### Out of Space
- Clear cache: `rm -rf ./cache/transcodes/*`
- Check what's in `./cache/images/`: `du -sh ./cache/images/`

### 12. Performance Tips

1. **Use Host Networking** - Already configured; provides best performance
2. **SSD Storage** - If possible, store media on an SSD for faster access
3. **Metadata Caching** - Configured in cache folder; reduces API calls
4. **Transcode Settings** - Configure bitrate based on your network speed
5. **Scheduled Tasks** - Let Jellyfin run metadata updates during off-peak hours

### 13. Advanced: Modifying docker-compose.yml

#### Add More Storage Paths

```yaml
volumes:
  - ./config:/config
  - ./cache:/cache
  - /home/kelvin/Jellyfin/Media:/media
  - /mnt/external-drive/Movies:/media/Movies-External  # Add external storage
```

#### Expose Different Port

```yaml
ports:
  - "8096:8096"  # Change first number for external port
```

#### Add Environment Variables

```yaml
environment:
  JELLYFIN_CACHE_DIR: /cache
  JELLYFIN_CONFIG_DIR: /config
```

After modifying docker-compose.yml:
```bash
podman compose down
podman compose up -d
```

### 14. Additional Resources

- **Official Jellyfin Docs**: https://docs.jellyfin.org/
- **Podman Documentation**: https://podman.io/
- **Media Server Best Practices**: See [Media/README.md](Media/README.md) for detailed media organization

---

## Summary

| Task | Command |
|---|---|
| Start Jellyfin | `podman compose up -d` |
| Stop Jellyfin | `podman compose down` |
| View Logs | `podman logs jellyfin` |
| Access Jellyfin | `http://localhost:8096` |
| Clear Cache | `rm -rf ./cache/*` |
| Check Status | `podman ps \| grep jellyfin` |

Happy streaming!
