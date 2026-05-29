#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path

def create_symlink_tree(source_dir: str, dest_dir: str, dry_run: bool = False):
    src = Path(source_dir).resolve()
    dst = Path(dest_dir).expanduser().resolve()

    if not src.is_dir():
        print(f"Source directory does not exist: {src}")
        return False

    if dry_run:
        print("DRY RUN MODE - No symlinks will be created.\n")

    dst.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        link_path = dst / item.name
        
        # Handle existing symlinks
        if link_path.is_symlink():
            current_target = link_path.resolve()
            expected_target = src / item.name
            if current_target == expected_target:
                print(f"Symlink already correct: {link_path}")
                continue
            else:
                print(f"Updating outdated symlink: {link_path}")
                if not dry_run:
                    link_path.unlink()

        if not link_path.exists():
            target = src / item.name
            try:
                if dry_run:
                    print(f"Would create: {link_path} -> {target}")
                else:
                    os.symlink(target, str(link_path))
                    print(f"Created symlink: {link_path} -> {target}")
            except Exception as e:
                print(f"Failed to create symlink for '{item.name}': {e}")

    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create symlinks from source media dirs to a host directory.")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without creating symlinks")
    args = parser.parse_args()

    # Configuring paths here
    MAPPING = {
        "/data/media/TV": "~/Symlinks/TV",
        "/mnt/data1/A":   "~/Symlinks/A"
    }

    print("Starting symlink generation...\n")
    for src, dst in MAPPING.items():
        create_symlink_tree(src, dst, dry_run=args.dry_run)
        print()  # spacing
