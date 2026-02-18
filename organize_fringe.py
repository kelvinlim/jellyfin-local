#!/usr/bin/env python3
"""
Organize Fringe Season 4 files into Jellyfin-compatible structure.
Copies files from FringeS04 to Media/Shows/Fringe/Season 04/
"""

import os
import shutil
import re
import argparse
from pathlib import Path


def parse_episode_info(filename):
    """
    Extract season and episode number from filename.
    Expected format: "Fringe S04E01 Episode Title (quality).ext"
    """
    pattern = r'Fringe S(\d{2})E(\d{2})'
    match = re.search(pattern, filename)
    
    if match:
        season = match.group(1)
        episode = match.group(2)
        return season, episode
    return None, None


def get_episode_title(filename):
    """Extract episode title from filename."""
    # Pattern: "Fringe S04E01 Title (quality).ext"
    pattern = r'Fringe S\d{2}E\d{2}\s+(.+?)\s+\(.*?\)'
    match = re.search(pattern, filename)
    
    if match:
        return match.group(1).strip()
    return None


def create_jellyfin_filename(season, episode, title, extension):
    """
    Create Jellyfin-compatible filename.
    Format: Fringe - S04E01 - Episode Title.ext
    """
    if title:
        return f"Fringe - S{season}E{episode} - {title}{extension}"
    else:
        return f"Fringe - S{season}E{episode}{extension}"


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Organize TV show files into Jellyfin-compatible structure'
    )
    parser.add_argument(
        'source',
        help='Source folder containing the video files'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without actually copying files'
    )
    args = parser.parse_args()
    
    dry_run = args.dry_run
    
    # Define paths
    script_dir = Path(__file__).parent
    source_dir = Path(args.source)
    
    # If source is relative, make it relative to script directory
    if not source_dir.is_absolute():
        source_dir = script_dir / source_dir
    
    dest_base = script_dir / "Media" / "Shows" / "Fringe"
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be copied\n")
    
    print(f"Source directory: {source_dir}")
    print(f"Destination base: {dest_base}")
    print()
    
    # Check if source directory exists
    if not source_dir.exists():
        print(f"Error: Source directory '{source_dir}' does not exist!")
        return
    
    # Get all video files
    video_extensions = {'.m4v', '.mp4', '.mkv', '.avi'}
    files = []
    
    for file in source_dir.iterdir():
        if file.is_file():
            # Skip .part files
            if file.name.endswith('.part'):
                continue
            # Check for video files
            if file.suffix in video_extensions:
                files.append(file)
    
    if not files:
        print("No video files found in source directory!")
        return
    
    print(f"Found {len(files)} video files to process\n")
    
    # Process each file
    copied_count = 0
    skipped_count = 0
    
    for file in sorted(files):
        season, episode = parse_episode_info(file.name)
        
        if not season or not episode:
            print(f"⚠ Skipping (couldn't parse): {file.name}")
            skipped_count += 1
            continue
        
        # Get episode title
        title = get_episode_title(file.name)
        
        # Determine file extension
        extension = file.suffix
        
        # Create season directory
        season_dir = dest_base / f"Season {season}"
        
        if not dry_run:
            season_dir.mkdir(parents=True, exist_ok=True)
        
        # Create new filename
        new_filename = create_jellyfin_filename(season, episode, title, extension)
        dest_file = season_dir / new_filename
        
        # Copy file
        try:
            print(f"{'[DRY RUN] ' if dry_run else ''}Copying: {file.name}")
            print(f"     To: {dest_file.relative_to(script_dir)}")
            
            if not dry_run:
                shutil.copy2(file, dest_file)
            copied_count += 1
            print(f"     {'✓ Would copy' if dry_run else '✓ Success'}\n")
            
        except Exception as e:
            print(f"     ✗ Error: {e}\n")
            skipped_count += 1
    
    # Summary
    print("=" * 60)
    if dry_run:
        print(f"Dry run complete!")
        print(f"  Would copy: {copied_count} files")
    else:
        print(f"Processing complete!")
        print(f"  Successfully copied: {copied_count} files")
    print(f"  Skipped: {skipped_count} files")
    print(f"  Destination: {dest_base.relative_to(script_dir)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
