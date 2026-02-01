#!/usr/bin/env python3
"""
Asset Catalog — CLI Scanner
Standalone tool to create / update .db files compatible with the desktop app.

Usage:
    python scan_assets.py                        # interactive mode
    python scan_assets.py /path/to/folder        # quick scan → scan.db
    python scan_assets.py /path/to/folder my.db  # scan into specific db
"""

import os, sys, sqlite3, json, time
from pathlib import Path
from datetime import datetime

DEFAULT_CATEGORIES = {
    "Archives":          [".zip",".rar",".7z",".tar",".gz",".bz2",".xz"],
    "After Effects":     [".aep",".aet",".ffx"],
    "Videos - MP4":      [".mp4"],
    "Videos - MOV":      [".mov"],
    "Videos - AVI":      [".avi"],
    "Videos - Other":    [".mkv",".m4v",".wmv",".flv",".webm",".mpg",".mpeg"],
    "Images - PNG":      [".png"],
    "Images - JPG":      [".jpg",".jpeg"],
    "Images - Other":    [".webp",".tiff",".tif",".gif",".bmp",".heic",".svg"],
    "Icons":             [".ico"],
    "Audio":             [".mp3",".wav",".aac",".flac",".ogg",".m4a",".wma",".aiff",".opus"],
    "Photoshop":         [".psd",".psb",".abr",".asl",".grd",".pat"],
    "Blender":           [".blend",".blend1"],
    "Vegas":             [".veg",".vf"],
    "Premiere":          [".prproj",".prel"],
    "Documents":         [".pdf",".doc",".docx",".txt",".rtf",".md",".odt"],
    "Spreadsheets":      [".xlsx",".xls",".csv",".ods"],
    "Fonts":             [".ttf",".otf",".woff",".woff2"],
    "3D Models":         [".obj",".fbx",".dae",".stl",".3ds",".gltf",".glb"],
    "Code":              [".py",".js",".html",".css",".cpp",".java",".c",".h",".ts",".json",".xml"],
    "Other":             [],
}

def ensure_db(path):
    conn = sqlite3.connect(str(path))
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, path TEXT UNIQUE, extension TEXT,
        category TEXT, size INTEGER,
        modified_date TEXT, created_date TEXT, file_hash TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE, extensions TEXT)""")
    c.execute("SELECT COUNT(*) FROM categories")
    if c.fetchone()[0] == 0:
        for n, exts in DEFAULT_CATEGORIES.items():
            c.execute("INSERT INTO categories (name,extensions) VALUES (?,?)",
                      (n, json.dumps(exts)))
    c.execute("CREATE INDEX IF NOT EXISTS idx_files_name ON files(name COLLATE NOCASE)")
    conn.commit()
    conn.close()

def get_category(ext, cats):
    e = ext.lower()
    for name, exts in cats.items():
        if e in (x.lower() for x in exts):
            return name
    return "Other"

def load_cats(db_path):
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("SELECT name, extensions FROM categories").fetchall()
    conn.close()
    return {r[0]: json.loads(r[1]) for r in rows}

def scan(root, db_path):
    ensure_db(db_path)
    cats = load_cats(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.execute("DELETE FROM files")
    conn.commit()

    print(f"\n  Counting files in: {root}")
    all_files = []
    for r, _, fnames in os.walk(root):
        for fn in fnames:
            all_files.append(os.path.join(r, fn))
    total = len(all_files)
    print(f"  Found {total:,} files. Scanning...\n")

    batch, bs, errors = [], 800, 0
    t0 = time.time()
    for i, fp in enumerate(all_files):
        try:
            st = os.stat(fp)
            ext = Path(fp).suffix.lower()
            batch.append((
                Path(fp).name, fp, ext,
                get_category(ext, cats),
                st.st_size,
                datetime.fromtimestamp(st.st_mtime).isoformat(),
                datetime.fromtimestamp(st.st_ctime).isoformat(),
                None
            ))
            if len(batch) >= bs:
                conn.executemany(
                    "INSERT OR REPLACE INTO files "
                    "(name,path,extension,category,size,modified_date,created_date,file_hash) "
                    "VALUES (?,?,?,?,?,?,?,?)", batch)
                conn.commit()
                batch.clear()
        except Exception:
            errors += 1

        if (i + 1) % 500 == 0 or i + 1 == total:
            pct = (i + 1) / total * 100
            bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
            print(f"\r  {bar}  {pct:5.1f}%  ({i+1:,}/{total:,})", end="", flush=True)

    if batch:
        conn.executemany(
            "INSERT OR REPLACE INTO files "
            "(name,path,extension,category,size,modified_date,created_date,file_hash) "
            "VALUES (?,?,?,?,?,?,?,?)", batch)
        conn.commit()
    conn.close()

    elapsed = time.time() - t0
    print(f"\n\n  ✓ Done in {elapsed:.1f}s  —  {total - errors:,} indexed, {errors} skipped")
    print(f"  Database: {db_path}\n")

def main():
    print("\n  ═══════════════════════════════════════")
    print("             EAM  —  CLI Scanner           ")
    print("  ═══════════════════════════════════════\n")

    if len(sys.argv) >= 2:
        root = sys.argv[1]
        db_out = sys.argv[2] if len(sys.argv) >= 3 else "scan.db"
    else:
        root = input("  Directory to scan: ").strip().strip('"')
        db_out = input("  Output .db file [scan.db]: ").strip() or "scan.db"

    if not os.path.isdir(root):
        print(f"  ✗ Not a directory: {root}")
        sys.exit(1)

    db_path = Path(db_out).with_suffix(".db")
    scan(root, db_path)

if __name__ == "__main__":
    main()
