#!/usr/bin/env python3
"""
Organize TV show files into Jellyfin-compatible structure.
Supports multiple shows and flexible filename patterns.
"""

import os
import shutil
import re
import argparse
from pathlib import Path


class ShowOrganizer:
    """Handles organizing TV show files into Jellyfin structure."""
    
    # Define show configurations
    SHOWS = {
        'fringe': {
            'name': 'Fringe',
            'patterns': [
                r'Fringe\s+S(\d{2})E(\d{2})\s+(.+?)\s+\(.*?\)',
            ],
            'output_name': 'Fringe',
        },
        'battlestar': {
            'name': 'Battlestar Galactica',
            'patterns': [
                r'BSG\s+S(\d{2})E(\d{2})\s+(.+?)\s+\(.*?\)',
            ],
            'output_name': 'Battlestar Galactica',
        },
    }
    
    def __init__(self, show_key):
        if show_key not in self.SHOWS:
            raise ValueError(f"Unknown show: {show_key}. Available: {list(self.SHOWS.keys())}")
        self.show_config = self.SHOWS[show_key]
        self.show_key = show_key
    
    def parse_episode_info(self, filename):
        """
        Extract season, episode, and title from filename.
        Tries each pattern defined for this show.
        """
        for pattern in self.show_config['patterns']:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                season = match.group(1)
                episode = match.group(2)
                title = match.group(3).strip() if len(match.groups()) >= 3 else None
                return season, episode, title
        
        return None, None, None
    
    def create_jellyfin_filename(self, season, episode, title, extension):
        """
        Create Jellyfin-compatible filename.
        Format: ShowName - S01E01 - Episode Title.ext
        """
        show_name = self.show_config['name']
        if title:
            return f"{show_name} - S{season}E{episode} - {title}{extension}"
        else:
            return f"{show_name} - S{season}E{episode}{extension}"
    
    def organize(self, source_dir, dest_parent=None, dry_run=False):
        """
        Organize TV show files.
        
        Args:
            source_dir: Source folder containing video files
            dest_parent: Parent directory for all shows (default: ./Media/Shows)
            dry_run: If True, don't actually copy files
        """
        source_dir = Path(source_dir)
        
        # If source is relative, make it relative to script directory
        if not source_dir.is_absolute():
            source_dir = Path(__file__).parent / source_dir
        
        # Set destination parent
        if dest_parent is None:
            dest_parent = Path(__file__).parent / "Media" / "Shows"
        else:
            dest_parent = Path(dest_parent)
        
        dest_base = dest_parent / self.show_config['output_name']
        
        if dry_run:
            print("🔍 DRY RUN MODE - No files will be copied\n")
        
        print(f"Show: {self.show_config['name']}")
        print(f"Source directory: {source_dir}")
        print(f"Destination base: {dest_base}")
        print()
        
        # Check if source directory exists
        if not source_dir.exists():
            print(f"Error: Source directory '{source_dir}' does not exist!")
            return False
        
        # Get all video files
        video_extensions = {'.m4v', '.mp4', '.mkv', '.avi', '.ts'}
        files = []
        
        for file in source_dir.iterdir():
            if file.is_file():
                # Skip .part files and other non-video files
                if file.name.endswith('.part'):
                    continue
                if file.suffix.lower() in video_extensions:
                    files.append(file)
        
        if not files:
            print("No video files found in source directory!")
            return False
        
        print(f"Found {len(files)} video files to process\n")
        
        # Process each file
        copied_count = 0
        skipped_count = 0
        
        for file in sorted(files):
            season, episode, title = self.parse_episode_info(file.name)
            
            if not season or not episode:
                print(f"⚠ Skipping (couldn't parse): {file.name}")
                skipped_count += 1
                continue
            
            # Determine file extension
            extension = file.suffix
            
            # Create season directory
            season_dir = dest_base / f"Season {season}"
            
            if not dry_run:
                season_dir.mkdir(parents=True, exist_ok=True)
            
            # Create new filename
            new_filename = self.create_jellyfin_filename(season, episode, title, extension)
            dest_file = season_dir / new_filename
            
            # Copy file
            try:
                print(f"{'[DRY RUN] ' if dry_run else ''}Copying: {file.name}")
                print(f"     To: Season {season}/{new_filename}")
                
                if not dry_run:
                    shutil.copy2(file, dest_file)
                copied_count += 1
                print(f"     {'✓ Would copy' if dry_run else '✓ Success'}\n")
                
            except Exception as e:
                print(f"     ✗ Error: {e}\n")
                skipped_count += 1
        
        # Summary
        print("=" * 70)
        if dry_run:
            print(f"Dry run complete!")
            print(f"  Would copy: {copied_count} files")
        else:
            print(f"Processing complete!")
            print(f"  Successfully copied: {copied_count} files")
        print(f"  Skipped: {skipped_count} files")
        print(f"  Destination: {dest_base}")
        print("=" * 70)
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Organize TV show files into Jellyfin-compatible structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Organize Fringe files
  python organize_shows.py fringe FringeS04
  
  # Organize Battlestar Galactica files with dry-run
  python organize_shows.py battlestar "Battlestar Galactica Season 1" --dry-run
  
  # Organize with custom destination
  python organize_shows.py fringe FringeS04 --dest /path/to/media/Shows
        """
    )
    parser.add_argument(
        'show',
        help=f"Show to organize: {', '.join(ShowOrganizer.SHOWS.keys())}"
    )
    parser.add_argument(
        'source',
        help='Source folder containing the video files'
    )
    parser.add_argument(
        '--dest', '-d',
        help='Destination parent directory (default: ./Media/Shows)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without actually copying files'
    )
    
    args = parser.parse_args()
    
    try:
        organizer = ShowOrganizer(args.show.lower())
        organizer.organize(
            source_dir=args.source,
            dest_parent=args.dest,
            dry_run=args.dry_run
        )
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
