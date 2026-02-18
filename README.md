# Jellyfin Local

A self-hosted [Jellyfin](https://jellyfin.org/) media server running via Podman (Docker-compatible).

## Requirements

- [Podman](https://podman.io/) + `podman-compose`

```bash
sudo apt install podman podman-compose   # Ubuntu/Debian
sudo dnf install podman podman-compose   # Fedora/RHEL
```

## Quick Start

```bash
podman compose up -d
```

Open **http://localhost:8096** in your browser.

## Directory Structure

```
.
├── docker-compose.yml   # Container configuration
├── config/              # Jellyfin settings & database (back this up)
├── cache/               # Thumbnails, transcodes, metadata (safe to delete)
└── Media/               # Media library (symlinked or mounted separately)
    ├── Movies/
    ├── Music/
    └── Shows/
```

## Common Commands

| Action | Command |
|--------|---------|
| Start | `podman compose up -d` |
| Stop | `podman compose down` |
| Logs | `podman logs -f jellyfin` |
| Shell | `podman exec -it jellyfin bash` |

## Media Naming Conventions

- **TV Shows**: `Shows/Show Name/Season XX/s##e##.mkv`
- **Movies**: `Movies/Movie Name (YYYY)/Movie Name (YYYY).mkv`
- **Music**: `Music/Artist/Album/Song.mp3`

When adding libraries in the Jellyfin UI, use the container paths (`/media/Shows`, `/media/Movies`, `/media/Music`).

## Further Reading

- [SETUP_GUIDE.md](SETUP_GUIDE.md) — full setup walkthrough
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) — command cheat sheet
