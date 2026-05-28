#!/usr/bin/env python3
import os
import re
from pathlib import Path

def extract_show_info(dirname):
    m = re.match(r'(.+?)\s*\((\d{4})\)', dirname)
    return (m.group(1).strip(), int(m.group(2))) if m else None

def extract_episode_info(filename):
    for pattern in [r'[Ss](\d{1,2})[Ee](\d{1,2})', r'(\d{1,2})[xX](\d{1,2})']:
        m = re.search(pattern, filename)
        if m: return int(m.group(1)), int(m.group(2))
    return None, None

def clean_title(filename):
    base = re.sub(r'\.(mkv|mp4|avi|webm)$', '', filename, flags=re.I)
    base = re.sub(r'[Ss]\d{1,2}[Ee]\d{1,2}\s*[-_.\s]*', '', base)
    base = re.sub(r'\(\d{4}\)|\[\d{4}\]|1080p|720p|WEB-DL|x265|x264|HEVC|AC3|EAC3|t3nzin', '', base, flags=re.I)
    return re.sub(r'[-_.\s]+', ' ', base).strip()

def create_symlink_library(src_dirs, dst_base):
    video_exts = {'.mkv', '.mp4', '.avi', '.webm'}
    for src_dir in src_dirs:
        if not Path(src_dir).is_dir(): continue
        print(f"Scanning: {src_dir}")

        for show_dir in Path(src_dir).iterdir():
            if not show_dir.is_dir(): continue
            info = extract_show_info(show_dir.name)
            if not info: continue
            show_name, year = info

            dst_show = Path(dst_base) / f"{show_name} ({year})"
            dst_show.mkdir(parents=True, exist_ok=True)

            for season_dir in show_dir.iterdir():
                if not season_dir.is_dir(): continue
                sm = re.search(r'Season\s*(\d+)', season_dir.name, re.I)
                if not sm: continue
                season_num = int(sm.group(1))

                dst_season = dst_show / f"Season {season_num:02d}"
                dst_season.mkdir(parents=True, exist_ok=True)

                for file in season_dir.iterdir():
                    if not file.is_file() or file.suffix.lower() not in video_exts: continue

                    ep_num, _ = extract_episode_info(file.name)
                    title = clean_title(file.name)

                    if ep_num is None:
                        m_ep = re.search(r'E(\d{1,2})|Episode\s*(\d{1,2})', file.name, re.I)
                        ep_num = int(m_ep.group(1) or m_ep.group(2)) if m_ep else 0

                    title_upper = title.upper()
                    if 'SPECIAL' in title_upper: season_num = 0
                    elif any(kw in title_upper for kw in ['OP', 'OPENING', 'ED', 'ENDING']): ep_num = 98
                    elif any(kw in title_upper for kw in ['EXTRA', 'BONUS', 'COMMENTARY']): ep_num = 99

                    ext = file.suffix.lower()
                    new_name = f"{show_name} - S{season_num:02d}E{ep_num:02d} - {title}{ext}"
                    dst_file = dst_season / new_name

                    if not dst_file.exists():
                        try:
                            os.symlink(file.resolve(), dst_file)
                        except OSError as e:
                            print(f" Skipped {file.name}: {e}")

if __name__ == "__main__":
    SRC_DIRS = ["/mnt/data1/TV", "/mnt/data1/A"]
    DST_BASE = "/mnt/data1/Symlinks"
    create_symlink_library(SRC_DIRS, DST_BASE)
    print("Symlink library created.")
