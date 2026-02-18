# Jellyfin Podman Quick Reference

## Getting Started (First Time)

```bash
cd /home/kelvin/Jellyfin
podman compose up -d
# Then open http://localhost:8096 in your browser
```

## Essential Commands

### Container Management

| Action | Command |
|--------|---------|
| **Start** | `podman compose up -d` |
| **Stop** | `podman compose down` |
| **Restart** | `podman compose restart` |
| **Status** | `podman ps \| grep jellyfin` |
| **View Logs** | `podman logs jellyfin` |
| **Follow Logs** (real-time) | `podman logs -f jellyfin` |
| **Container Shell** | `podman exec -it jellyfin bash` |
| **Resource Usage** | `podman stats jellyfin` |

### Access Jellyfin

- **Web Interface**: http://localhost:8096
- **Default Port**: 8096

### Media Organization

| Media Type | Container Path | Content Structure |
|---|---|---|
| **TV Shows** | `/media/Shows` | `Show Name/Season XX/s##e##.mkv` |
| **Movies** | `/media/Movies` | `Movie Name (YYYY)/Movie Name (YYYY).mkv` |
| **Music** | `/media/Music` | Artist/Album/Song.mp3 |

### Maintenance

| Task | Command |
|---|---|
| **Clear Cache** (safe) | `rm -rf ./cache/*` |
| **Clear Transcode Cache** | `rm -rf ./cache/transcodes/*` |
| **Clear Image Cache** | `rm -rf ./cache/images/*` |
| **View Cache Size** | `du -sh ./cache/` |
| **Backup Config** | `tar -czf jellyfin-backup-$(date +%Y%m%d).tar.gz ./config/` |

## Path Mapping Reference

**Remember**: Use container paths when configuring in Jellyfin UI!

```
Host Path                        → Container Path
./config                         → /config
./cache                          → /cache
/home/kelvin/Jellyfin/Media      → /media
/home/kelvin/Jellyfin/Media/Shows → /media/Shows
/home/kelvin/Jellyfin/Media/Movies → /media/Movies
```

## Library Setup in Jellyfin

1. Open http://localhost:8096
2. **Settings** → **Libraries**
3. Click **+** → Select content type
4. Use these container paths:
   - TV Shows: `/media/Shows`
   - Movies: `/media/Movies`
   - Music: `/media/Music`

## Folder Structure Quick Check

```bash
# Verify your media folders exist
ls -la ./Media/

# Check folder sizes
du -sh ./config/ ./cache/ ./Media/

# List shows 
ls ./Media/Shows/

# List movies
ls ./Media/Movies/
```

## Troubleshooting Quick Fixes

### Container won't start?
```bash
podman logs jellyfin
```

### Port 8096 in use?
```bash
sudo lsof -i :8096
```

### Media not showing?
1. Check container paths: `/media/Shows`, `/media/Movies`
2. Check file permissions: `ls -la ./Media/`
3. Restart container: `podman compose restart`

### Slow performance?
```bash
# Clear cache
rm -rf ./cache/*

# Restart
podman compose restart
```

## File Organization Examples

### TV Show Example
```
Media/Shows/Fringe/Season 01/Fringe - s01e01 - Pilot.mkv
Media/Shows/Fringe/Season 01/Fringe - s01e02 - The Same Old Story.mkv
Media/Shows/Fringe/Season 02/Fringe - s02e01 - A New Day in the Old Town.mkv
```

### Movie Example
```
Media/Movies/The Motorcycle Diaries (2004)/The Motorcycle Diaries (2004).mkv
Media/Movies/Inception (2010)/Inception (2010).mkv
```

## Quick Docker-Compose Edits

### Change Port (if 8096 conflicts)
Edit `docker-compose.yml` and add:
```yaml
ports:
  - "8097:8096"  # Access on port 8097 instead
```

### Add External Media Storage
Edit `docker-compose.yml` volumes:
```yaml
volumes:
  - ./config:/config
  - ./cache:/cache
  - /home/kelvin/Jellyfin/Media:/media
  - /mnt/external/movies:/media/Movies-External
```

Then rebuild:
```bash
podman compose down
podman compose up -d
```

## Helpful Scripts in This Directory

- **organize_shows.py** - Reorganize shows into season folders
- **organize_fringe.py** - Fringe-specific organization

Usage:
```bash
python organize_shows.py
```

## Directory Important Notes

| Directory | Backup? | Can Delete? | Purpose |
|---|---|---|---|
| `./config/` | ✓ YES | ✗ NO | Settings/Database - KEEP! |
| `./cache/` | ✗ NO | ✓ YES | Thumbnails/Transcodes - Safe to delete |
| `./Media/` | - | - | Your actual media files |

## Common Jellyfin Settings

After starting Jellyfin (http://localhost:8096):

1. **Admin User** - Create first account (automatically admin)
2. **Libraries** - Add `/media/Shows`, `/media/Movies`, `/media/Music`
3. **Display** - Set language, date format
4. **Playback** - Configure transcoding, bitrate limits
5. **Scheduled Tasks** - Enable metadata refresh (off-peak hours)

## Docker Compose File Location
- **Main config**: `/home/kelvin/Jellyfin/docker-compose.yml`
- **Server config** (persist): `/home/kelvin/Jellyfin/config/config/`

For full documentation, see [SETUP_GUIDE.md](SETUP_GUIDE.md) or [Media/README.md](Media/README.md)
