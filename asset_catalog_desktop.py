#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║                        EAM Desktop  v1.0                     ║
║   Themes • Auto-Organizer • Animated GIF • Modern UI         ║
║                                                              ║
║   pip install PySide6 Pillow                                 ║
║   python asset_catalog_desktop.py                            ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys, os, sqlite3, json, csv, hashlib, subprocess, platform, mimetypes
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ── Dependency gate ────────────────────────────────────────────
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QSplitter, QListView, QLabel, QPushButton, QLineEdit, QComboBox,
        QProgressBar, QTabBar, QFileDialog, QMenu, QToolBar, QStatusBar,
        QScrollArea, QFrame, QDialog, QDialogButtonBox, QTextEdit,
        QAbstractItemView, QStyle, QStyledItemDelegate, QToolButton,
        QSizePolicy, QMessageBox, QGroupBox, QPlainTextEdit, QSlider,
        QStackedWidget, QSpacerItem, QTreeWidget, QTreeWidgetItem,
        QHeaderView
    )
    from PySide6.QtCore import (
        Qt, QThread, Signal, QSize, QRect, QRectF, QModelIndex, QTimer,
        QUrl, QAbstractListModel, QEvent, QPoint, QSortFilterProxyModel,
        QMimeData, QByteArray, Property
    )
    from PySide6.QtGui import (
        QPixmap, QIcon, QPainter, QColor, QFont, QFontMetrics, QPen,
        QBrush, QLinearGradient, QPainterPath, QFontDatabase, QImage,
        QAction, QCursor, QDesktopServices, QPalette, QKeySequence,
        QShortcut, QMovie, QRadialGradient
    )
except ImportError:
    print("━" * 60)
    print("  PySide6 is required.  Install it with:")
    print("    pip install PySide6")
    print("━" * 60)
    sys.exit(1)

try:
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PySide6.QtMultimediaWidgets import QVideoWidget
    HAS_MEDIA = True
except Exception:
    HAS_MEDIA = False

try:
    from PIL import Image as PILImage
    HAS_PIL = True
except Exception:
    HAS_PIL = False


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

APP_NAME    = "EAM"
APP_VERSION = "1.0"
DATA_DIR    = Path.home() / ".asset_catalog"
DB_DIR      = DATA_DIR / "databases"
THUMB_DIR   = DATA_DIR / "thumbnails"
CONFIG_PATH = DATA_DIR / "config.json"

for _d in (DATA_DIR, DB_DIR, THUMB_DIR):
    _d.mkdir(parents=True, exist_ok=True)

THUMB_SIZE = (180, 130)
PAGE_SIZE = 120
SEARCH_DEBOUNCE_MS = 250

DEFAULT_CATEGORIES = {
    "Archives":      [".zip",".rar",".7z",".tar",".gz",".bz2",".xz"],
    "After Effects": [".aep",".aet",".ffx"],
    "Videos - MP4":  [".mp4"], "Videos - MOV": [".mov"], "Videos - AVI": [".avi"],
    "Videos - Other":[".mkv",".m4v",".wmv",".flv",".webm",".mpg",".mpeg"],
    "Images - PNG":  [".png"], "Images - JPG": [".jpg",".jpeg"],
    "Images - Other":[".webp",".tiff",".tif",".gif",".bmp",".heic",".svg"],
    "Icons":         [".ico"],
    "Audio":         [".mp3",".wav",".aac",".flac",".ogg",".m4a",".wma",".aiff",".opus",".alac"],
    "Photoshop":     [".psd",".psb",".abr",".asl",".grd",".pat"],
    "Blender":       [".blend",".blend1"], "Vegas": [".veg",".vf"],
    "Premiere":      [".prproj",".prel"],
    "Documents":     [".pdf",".doc",".docx",".txt",".rtf",".md",".odt"],
    "Spreadsheets":  [".xlsx",".xls",".csv",".ods"],
    "Fonts":         [".ttf",".otf",".woff",".woff2"],
    "3D Models":     [".obj",".fbx",".dae",".stl",".3ds",".gltf",".glb"],
    "Code":          [".py",".js",".html",".css",".cpp",".java",".c",
                      ".h",".ts",".jsx",".tsx",".json",".xml",".yaml"],
    "Other":         [],
}

IMAGE_EXTS = {".png",".jpg",".jpeg",".gif",".webp",".bmp",".tiff",".tif",".ico",".svg",".heic"}
VIDEO_EXTS = {".mp4",".mov",".avi",".mkv",".webm",".flv",".wmv",".m4v",".mpg",".mpeg"}
AUDIO_EXTS = {".mp3",".wav",".aac",".flac",".ogg",".m4a",".wma",".aiff",".opus",".alac"}
FONT_EXTS  = {".ttf",".otf",".woff",".woff2"}
TEXT_EXTS  = {".txt",".json",".xml",".csv",".log",".md",".py",".js",".html",".css",
              ".cpp",".java",".c",".h",".ts",".yaml",".toml",".ini",".cfg",".sh",".bat",".rtf"}

CAT_COLORS = {
    "Videos":"#8b5cf6","Images":"#06b6d4","Audio":"#22c55e","Fonts":"#ec4899",
    "Archives":"#f59e0b","Documents":"#f97316","Spreadsheets":"#84cc16",
    "Code":"#14b8a6","3D":"#ef4444","Photoshop":"#3b82f6","After":"#a855f7",
    "Blender":"#f97316","Premiere":"#8b5cf6","Vegas":"#6366f1","Icons":"#06b6d4",
}

def cat_color(category: str) -> str:
    for key, col in CAT_COLORS.items():
        if key.lower() in category.lower(): return col
    return "#64748b"


# ═══════════════════════════════════════════════════════════════
# THEME SYSTEM  – 7 themes
# ═══════════════════════════════════════════════════════════════

THEMES = {
    "Dark": {
        "bg_primary":"#0f0f17","bg_secondary":"#1a1a2e","bg_panel":"#13132a",
        "bg_card":"#252642","bg_card_hover":"#2e2e52","bg_card_selected":"#332e5c",
        "bg_input":"#1a1a2e","bg_thumb":"#1a1a2e",
        "border":"#252642","border_light":"#333355",
        "accent":"#7c3aed","accent_hover":"#9b59ef","accent_pressed":"#6d28d9","accent_text":"#c4b5fd",
        "text_primary":"#e2e8f0","text_secondary":"#94a3b8","text_muted":"#64748b",
        "scrollbar":"#333355","danger":"#ef4444",
        "grad_start":"#7c3aed","grad_end":"#06b6d4",
    },
    "Light": {
        "bg_primary":"#f1f5f9","bg_secondary":"#ffffff","bg_panel":"#f8fafc",
        "bg_card":"#ffffff","bg_card_hover":"#f1f5f9","bg_card_selected":"#ede9fe",
        "bg_input":"#ffffff","bg_thumb":"#e2e8f0",
        "border":"#e2e8f0","border_light":"#cbd5e1",
        "accent":"#7c3aed","accent_hover":"#6d28d9","accent_pressed":"#5b21b6","accent_text":"#7c3aed",
        "text_primary":"#1e293b","text_secondary":"#475569","text_muted":"#94a3b8",
        "scrollbar":"#cbd5e1","danger":"#ef4444",
        "grad_start":"#7c3aed","grad_end":"#06b6d4",
    },
    "Midnight": {
        "bg_primary":"#060610","bg_secondary":"#0c0c1d","bg_panel":"#0a0a18",
        "bg_card":"#12122a","bg_card_hover":"#1a1a38","bg_card_selected":"#1e1e44",
        "bg_input":"#0c0c1d","bg_thumb":"#0e0e20",
        "border":"#16163a","border_light":"#222252",
        "accent":"#3b82f6","accent_hover":"#60a5fa","accent_pressed":"#2563eb","accent_text":"#93c5fd",
        "text_primary":"#e2e8f0","text_secondary":"#94a3b8","text_muted":"#475569",
        "scrollbar":"#222252","danger":"#f87171",
        "grad_start":"#3b82f6","grad_end":"#8b5cf6",
    },
    "Extra Dark": {
        "bg_primary":"#000000","bg_secondary":"#0a0a0a","bg_panel":"#050505",
        "bg_card":"#141414","bg_card_hover":"#1c1c1c","bg_card_selected":"#221a30",
        "bg_input":"#0a0a0a","bg_thumb":"#0e0e0e",
        "border":"#1a1a1a","border_light":"#2a2a2a",
        "accent":"#a855f7","accent_hover":"#c084fc","accent_pressed":"#9333ea","accent_text":"#d8b4fe",
        "text_primary":"#f8fafc","text_secondary":"#a1a1aa","text_muted":"#52525b",
        "scrollbar":"#2a2a2a","danger":"#f87171",
        "grad_start":"#a855f7","grad_end":"#ec4899",
    },
    "Purple": {
        "bg_primary":"#120820","bg_secondary":"#1a0e30","bg_panel":"#160b28",
        "bg_card":"#241545","bg_card_hover":"#2e1a58","bg_card_selected":"#3a2068",
        "bg_input":"#1a0e30","bg_thumb":"#1e1040",
        "border":"#2a1650","border_light":"#3d2270",
        "accent":"#c084fc","accent_hover":"#d8b4fe","accent_pressed":"#a855f7","accent_text":"#e9d5ff",
        "text_primary":"#f3e8ff","text_secondary":"#c4b5fd","text_muted":"#7c3aed",
        "scrollbar":"#3d2270","danger":"#fb7185",
        "grad_start":"#c084fc","grad_end":"#f472b6",
    },
    "Glass Dark": {
        "bg_primary":"#0e1018","bg_secondary":"#161a26","bg_panel":"#131720",
        "bg_card":"#1c2030","bg_card_hover":"#242838","bg_card_selected":"#262a42",
        "bg_input":"#161a26","bg_thumb":"#181c28",
        "border":"#2a2e40","border_light":"#363a50",
        "accent":"#06b6d4","accent_hover":"#22d3ee","accent_pressed":"#0891b2","accent_text":"#67e8f9",
        "text_primary":"#e2e8f0","text_secondary":"#94a3b8","text_muted":"#64748b",
        "scrollbar":"#363a50","danger":"#f87171",
        "grad_start":"#06b6d4","grad_end":"#8b5cf6",
    },
    "Glass Light": {
        "bg_primary":"#e8ecf4","bg_secondary":"#f0f4fa","bg_panel":"#edf1f8",
        "bg_card":"#f6f8fc","bg_card_hover":"#eef2fa","bg_card_selected":"#ddd6fe",
        "bg_input":"#f6f8fc","bg_thumb":"#dfe4ee",
        "border":"#d0d5e0","border_light":"#bfc5d2",
        "accent":"#7c3aed","accent_hover":"#6d28d9","accent_pressed":"#5b21b6","accent_text":"#6d28d9",
        "text_primary":"#1e293b","text_secondary":"#475569","text_muted":"#94a3b8",
        "scrollbar":"#bfc5d2","danger":"#ef4444",
        "grad_start":"#7c3aed","grad_end":"#06b6d4",
    },
}


def build_qss(t):
    return f"""
QWidget {{ background:{t['bg_primary']}; color:{t['text_primary']};
    font-family:"Segoe UI","SF Pro Display","Helvetica Neue",Arial,sans-serif; font-size:13px; }}
#topBar {{ background:{t['bg_secondary']}; border-bottom:1px solid {t['border']}; }}
QTabBar::tab {{ background:{t['bg_card']}; color:{t['text_secondary']}; padding:7px 20px;
    margin-right:2px; border-top-left-radius:8px; border-top-right-radius:8px;
    border:1px solid {t['border_light']}; border-bottom:none; min-width:60px; }}
QTabBar::tab:selected {{ background:{t['bg_card_selected']}; color:{t['accent_text']}; border-color:{t['accent']}; }}
QTabBar::tab:hover:!selected {{ background:{t['bg_card_hover']}; color:{t['text_primary']}; }}
QTabBar::close-button {{ image:none; subcontrol-position:right; padding:2px; }}
QTabBar::close-button:hover {{ background:{t['danger']}; border-radius:3px; }}
#addTabBtn {{ background:{t['bg_card']}; color:{t['accent']}; border:1px dashed {t['accent']};
    border-radius:6px; font-size:18px; font-weight:bold; padding:4px 10px; }}
#addTabBtn:hover {{ background:{t['bg_card_hover']}; }}
#searchBox {{ background:{t['bg_input']}; border:1px solid {t['border_light']}; border-radius:10px;
    padding:7px 14px; color:{t['text_primary']}; selection-background-color:{t['accent']}; }}
#searchBox:focus {{ border-color:{t['accent']}; }}
QComboBox {{ background:{t['bg_input']}; border:1px solid {t['border_light']}; border-radius:8px;
    padding:6px 12px; color:{t['text_primary']}; min-height:18px; }}
QComboBox:hover {{ border-color:{t['accent']}; }}
QComboBox::drop-down {{ border:none; width:20px; }}
QComboBox QAbstractItemView {{ background:{t['bg_secondary']}; border:1px solid {t['border_light']};
    border-radius:6px; color:{t['text_primary']}; selection-background-color:{t['bg_card_selected']};
    selection-color:{t['accent_text']}; padding:4px; }}
#accentBtn {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {t['accent']},stop:1 {t['grad_end']});
    color:#ffffff; border:none; border-radius:8px; padding:7px 16px; font-weight:600; }}
#accentBtn:hover {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {t['accent_hover']},stop:1 {t['grad_end']}); }}
#accentBtn:pressed {{ background:{t['accent_pressed']}; }}
#secondaryBtn {{ background:{t['bg_card']}; color:{t['accent_text']}; border:1px solid {t['border_light']};
    border-radius:8px; padding:7px 16px; }}
#secondaryBtn:hover {{ background:{t['bg_card_hover']}; border-color:{t['accent']}; }}
SidebarWidget {{ background:{t['bg_panel']}; border-right:1px solid {t['border']}; }}
#sideHead {{ color:{t['text_muted']}; font-size:10px; font-weight:700; letter-spacing:1.5px; padding:6px 0 2px 0; }}
#statBig {{ font-size:24px; font-weight:700; color:{t['accent_text']}; }}
#statSmall {{ font-size:12px; color:{t['text_secondary']}; margin-bottom:4px; }}
#catBtn {{ background:transparent; color:{t['text_secondary']}; border:none; border-radius:8px;
    padding:7px 10px; text-align:left; font-size:12px; }}
#catBtn:hover {{ background:{t['bg_card']}; color:{t['text_primary']}; }}
#catBtn:checked {{ background:{t['bg_card_selected']}; color:{t['accent_text']}; font-weight:600; }}
QListView {{ background:{t['bg_primary']}; border:none; outline:none; }}
QListView::item {{ padding:0px; border:none; }}
QListView::item:selected {{ background:transparent; }}
QTreeWidget {{ background:{t['bg_primary']}; border:none; outline:none; color:{t['text_primary']}; font-size:12px; }}
QTreeWidget::item {{ padding:5px 4px; border-radius:4px; }}
QTreeWidget::item:hover {{ background:{t['bg_card_hover']}; }}
QTreeWidget::item:selected {{ background:{t['bg_card_selected']}; color:{t['accent_text']}; }}
QTreeWidget::branch {{ background:transparent; }}
QHeaderView::section {{ background:{t['bg_secondary']}; color:{t['text_muted']}; border:none;
    border-bottom:1px solid {t['border']}; padding:6px 12px; font-size:11px; font-weight:600; }}
PreviewPanel {{ background:{t['bg_panel']}; border-left:1px solid {t['border']}; }}
#previewTitle {{ font-size:15px; font-weight:600; color:{t['text_primary']}; }}
QPlainTextEdit {{ background:{t['bg_input']}; color:{t['text_secondary']}; border:1px solid {t['border']};
    border-radius:8px; padding:10px; font-family:"JetBrains Mono","Fira Code","Consolas",monospace; font-size:12px; }}
QScrollBar:vertical {{ background:transparent; width:7px; margin:0; }}
QScrollBar::handle:vertical {{ background:{t['scrollbar']}; border-radius:3px; min-height:30px; }}
QScrollBar::handle:vertical:hover {{ background:{t['accent']}; }}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical {{ height:0; background:transparent; }}
QScrollBar:horizontal {{ background:transparent; height:7px; }}
QScrollBar::handle:horizontal {{ background:{t['scrollbar']}; border-radius:3px; min-width:30px; }}
QScrollBar::handle:horizontal:hover {{ background:{t['accent']}; }}
QScrollBar::add-line:horizontal,QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,QScrollBar::sub-page:horizontal {{ width:0; background:transparent; }}
QScrollArea {{ background:transparent; border:none; }}
QProgressBar {{ background:{t['bg_secondary']}; border:none; border-radius:2px; }}
QProgressBar::chunk {{ background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 {t['grad_start']},stop:1 {t['grad_end']}); border-radius:2px; }}
#footer {{ background:{t['bg_panel']}; border-top:1px solid {t['border']}; }}
QStatusBar {{ background:{t['bg_primary']}; color:{t['text_muted']}; font-size:11px;
    border-top:1px solid {t['border']}; }}
QSlider::groove:horizontal {{ height:4px; background:{t['border_light']}; border-radius:2px; }}
QSlider::handle:horizontal {{ background:{t['accent']}; width:14px; height:14px; margin:-5px 0; border-radius:7px; }}
QSlider::handle:horizontal:hover {{ background:{t['accent_hover']}; }}
QMessageBox {{ background:{t['bg_secondary']}; }}
QMessageBox QLabel {{ color:{t['text_primary']}; }}
QFileDialog {{ background:{t['bg_secondary']}; }}
QVideoWidget {{ background:#000; border-radius:8px; }}
QToolTip {{ background:{t['bg_card']}; color:{t['text_primary']}; border:1px solid {t['border_light']};
    padding:5px 10px; border-radius:6px; }}
QSplitter::handle {{ background:{t['border']}; width:1px; }}
"""


def build_ctx_qss(t):
    return f"""
QMenu {{ background:{t['bg_secondary']}; border:1px solid {t['border_light']}; border-radius:10px; padding:6px; }}
QMenu::item {{ padding:8px 18px; border-radius:6px; color:{t['text_primary']}; }}
QMenu::item:selected {{ background:{t['bg_card_selected']}; color:{t['accent_text']}; }}
QMenu::separator {{ height:1px; background:{t['border']}; margin:4px 8px; }}
"""


def build_palette(t):
    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor(t["bg_secondary"]))
    pal.setColor(QPalette.WindowText,      QColor(t["text_primary"]))
    pal.setColor(QPalette.Base,            QColor(t["bg_panel"]))
    pal.setColor(QPalette.AlternateBase,   QColor(t["bg_secondary"]))
    pal.setColor(QPalette.Text,            QColor(t["text_primary"]))
    pal.setColor(QPalette.Button,          QColor(t["bg_card"]))
    pal.setColor(QPalette.ButtonText,      QColor(t["text_primary"]))
    pal.setColor(QPalette.Highlight,       QColor(t["accent"]))
    pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    pal.setColor(QPalette.ToolTipBase,     QColor(t["bg_card"]))
    pal.setColor(QPalette.ToolTipText,     QColor(t["text_primary"]))
    return pal


class ThemeManager:
    def __init__(self, app: QApplication):
        self._app = app
        self._current = "Dark"

    @property
    def current_name(self): return self._current

    @property
    def t(self): return THEMES[self._current]

    def apply(self, name: str):
        if name not in THEMES: name = "Dark"
        self._current = name
        t = THEMES[name]
        self._app.setStyleSheet(build_qss(t))
        self._app.setPalette(build_palette(t))

    @staticmethod
    def names(): return list(THEMES.keys())


# ═══════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════

def fmt_size(b):
    if not b or b < 0: return "0 B"
    for u in ("B","KB","MB","GB","TB"):
        if b < 1024: return f"{b:.1f} {u}" if u != "B" else f"{int(b)} B"
        b /= 1024
    return f"{b:.2f} PB"


def open_file_location(path: str):
    p = Path(path)
    if not p.exists(): return
    s = platform.system()
    try:
        if s == "Windows": subprocess.Popen(["explorer", "/select,", str(p)])
        elif s == "Darwin": subprocess.Popen(["open", "-R", str(p)])
        else: subprocess.Popen(["xdg-open", str(p.parent)])
    except Exception: pass


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try: return json.loads(CONFIG_PATH.read_text("utf-8"))
        except: pass
    return {}


def save_config(cfg: dict):
    try: CONFIG_PATH.write_text(json.dumps(cfg, indent=2), "utf-8")
    except: pass


# ═══════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════

class AssetDatabase:
    def __init__(self, db_path: Path):
        self.path = Path(db_path)
        self._init_db()

    def _conn(self):
        c = sqlite3.connect(str(self.path), check_same_thread=False)
        c.execute("PRAGMA journal_mode=WAL"); c.execute("PRAGMA synchronous=NORMAL")
        return c

    def _init_db(self):
        conn = self._conn(); c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, path TEXT UNIQUE,
            extension TEXT, category TEXT, size INTEGER,
            modified_date TEXT, created_date TEXT, file_hash TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, extensions TEXT)""")
        c.execute("SELECT COUNT(*) FROM categories")
        if c.fetchone()[0] == 0:
            for name, exts in DEFAULT_CATEGORIES.items():
                c.execute("INSERT INTO categories (name,extensions) VALUES (?,?)", (name, json.dumps(exts)))
        c.execute("CREATE INDEX IF NOT EXISTS idx_files_name ON files(name COLLATE NOCASE)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_files_cat  ON files(category)")
        conn.commit(); conn.close()

    def get_categories(self):
        conn = self._conn()
        rows = conn.execute("SELECT name, extensions FROM categories").fetchall()
        conn.close()
        return {r[0]: json.loads(r[1]) for r in rows}

    def category_for_ext(self, ext, cats):
        el = ext.lower()
        for name, exts in cats.items():
            if el in (e.lower() for e in exts): return name
        return "Other"

    def search(self, query="", category=None, extension=None, limit=PAGE_SIZE, offset=0, sort="name"):
        conn = self._conn(); where, params = ["1=1"], []
        if query: where.append("name LIKE ? COLLATE NOCASE"); params.append(f"%{query}%")
        if category and category != "All": where.append("category = ?"); params.append(category)
        if extension: where.append("extension = ?"); params.append(extension)
        w = " AND ".join(where)
        order = {"name":"name COLLATE NOCASE","size":"size DESC","date":"modified_date DESC"}.get(sort,"name COLLATE NOCASE")
        rows = conn.execute(f"SELECT id,name,path,extension,category,size,modified_date,created_date FROM files WHERE {w} ORDER BY {order} LIMIT ? OFFSET ?", params+[limit,offset]).fetchall()
        total = conn.execute(f"SELECT COUNT(*) FROM files WHERE {w}", params).fetchone()[0]
        conn.close()
        keys = ("id","name","path","extension","category","size","modified_date","created_date")
        return [dict(zip(keys, r)) for r in rows], total

    def stats(self):
        conn = self._conn()
        tf, ts = conn.execute("SELECT COUNT(*), COALESCE(SUM(size),0) FROM files").fetchone()
        by_cat = conn.execute("SELECT category, COUNT(*), COALESCE(SUM(size),0) FROM files GROUP BY category").fetchall()
        by_ext = conn.execute("SELECT extension, COUNT(*) FROM files GROUP BY extension ORDER BY COUNT(*) DESC LIMIT 30").fetchall()
        conn.close()
        return {"total_files":tf or 0,"total_size":ts or 0,
                "by_category":[{"category":r[0],"count":r[1],"size":r[2]} for r in by_cat],
                "by_extension":[{"extension":r[0],"count":r[1]} for r in by_ext]}

    def find_duplicates(self):
        conn = self._conn()
        rows = conn.execute("SELECT file_hash,COUNT(*),GROUP_CONCAT(path,'||') FROM files WHERE file_hash IS NOT NULL GROUP BY file_hash HAVING COUNT(*)>1").fetchall()
        conn.close()
        return [{"hash":r[0],"count":r[1],"paths":r[2].split("||")} for r in rows]

    def get_files_by_category(self, limit_per_cat=500):
        conn = self._conn()
        cats = conn.execute("SELECT DISTINCT category FROM files ORDER BY category").fetchall()
        groups = {}
        keys = ("id","name","path","extension","category","size","modified_date","created_date")
        for (cat,) in cats:
            rows = conn.execute("SELECT id,name,path,extension,category,size,modified_date,created_date FROM files WHERE category=? ORDER BY name LIMIT ?", (cat, limit_per_cat)).fetchall()
            total = conn.execute("SELECT COUNT(*) FROM files WHERE category=?", (cat,)).fetchone()[0]
            groups[cat] = {"files":[dict(zip(keys, r)) for r in rows], "total":total}
        conn.close(); return groups

    def get_folder_tree(self, limit=8000):
        conn = self._conn()
        keys = ("id","name","path","extension","category","size","modified_date","created_date")
        rows = conn.execute("SELECT id,name,path,extension,category,size,modified_date,created_date FROM files ORDER BY path LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [dict(zip(keys, r)) for r in rows]


# ═══════════════════════════════════════════════════════════════
# WORKERS
# ═══════════════════════════════════════════════════════════════

class ScanWorker(QThread):
    progress = Signal(int, int, str)
    finished_ok = Signal()
    def __init__(self, db_path, root_path, hash_small=False):
        super().__init__(); self.db_path=db_path; self.root=root_path; self.hash_small=hash_small; self._stop=False
    def stop(self): self._stop=True
    def run(self):
        db = AssetDatabase(self.db_path); cats = db.get_categories()
        self.progress.emit(0,0,"counting")
        all_files=[]
        for r,_,fnames in os.walk(self.root):
            for fn in fnames:
                all_files.append(os.path.join(r,fn))
                if self._stop: return
        total=len(all_files); self.progress.emit(0,total,"scanning")
        conn=db._conn(); conn.execute("DELETE FROM files"); conn.commit()
        batch,bs=[],800
        for i,fp in enumerate(all_files):
            if self._stop: conn.close(); return
            try:
                st=os.stat(fp); ext=Path(fp).suffix.lower(); cat=db.category_for_ext(ext,cats); fh=None
                if self.hash_small and st.st_size<10*1024*1024:
                    try: fh=hashlib.md5(open(fp,"rb").read()).hexdigest()
                    except: pass
                batch.append((Path(fp).name,fp,ext,cat,st.st_size,
                    datetime.fromtimestamp(st.st_mtime).isoformat(),
                    datetime.fromtimestamp(st.st_ctime).isoformat(),fh))
                if len(batch)>=bs:
                    conn.executemany("INSERT OR REPLACE INTO files (name,path,extension,category,size,modified_date,created_date,file_hash) VALUES (?,?,?,?,?,?,?,?)",batch)
                    conn.commit(); batch.clear()
            except: pass
            if i%200==0: self.progress.emit(i+1,total,"scanning")
        if batch:
            conn.executemany("INSERT OR REPLACE INTO files (name,path,extension,category,size,modified_date,created_date,file_hash) VALUES (?,?,?,?,?,?,?,?)",batch)
            conn.commit()
        conn.close(); self.progress.emit(total,total,"complete"); self.finished_ok.emit()


class ThumbWorker(QThread):
    ready = Signal(int, QImage)
    def __init__(self): super().__init__(); self._queue=[]; self._stop=False
    def enqueue(self, items): self._queue.extend(items)
    def clear_queue(self): self._queue.clear()
    def stop(self): self._stop=True
    def run(self):
        while not self._stop:
            if not self._queue: self.msleep(50); continue
            fid,fpath,ext = self._queue.pop(0)
            img = self._generate(fpath,ext)
            if img and not img.isNull(): self.ready.emit(fid,img)
    def _generate(self, fpath, ext):
        ext=ext.lower(); thumb_key=f"{abs(hash(fpath))}.jpg"; cached=THUMB_DIR/thumb_key
        if cached.exists(): return QImage(str(cached))
        if ext in IMAGE_EXTS and HAS_PIL and ext not in (".svg",".heic"):
            try:
                im=PILImage.open(fpath)
                if hasattr(im,'n_frames') and im.n_frames>1: im.seek(0)
                im.thumbnail(THUMB_SIZE)
                if im.mode in ("RGBA","P","LA"): im=im.convert("RGB")
                im.save(str(cached),"JPEG",quality=78); return QImage(str(cached))
            except: pass
        if ext in IMAGE_EXTS:
            try:
                qimg=QImage(fpath)
                if not qimg.isNull():
                    qimg=qimg.scaled(THUMB_SIZE[0],THUMB_SIZE[1],Qt.KeepAspectRatio,Qt.SmoothTransformation)
                    qimg.save(str(cached),"JPEG",78); return qimg
            except: pass
        return None


# ═══════════════════════════════════════════════════════════════
# DATA MODEL + DELEGATE
# ═══════════════════════════════════════════════════════════════

ROLE_FILEDATA  = Qt.UserRole + 1
ROLE_THUMBNAIL = Qt.UserRole + 2

class FileListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent); self._files=[]; self._thumbs={}
    def rowCount(self, parent=QModelIndex()): return len(self._files)
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row()>=len(self._files): return None
        f=self._files[index.row()]
        if role==Qt.DisplayRole: return f["name"]
        if role==ROLE_FILEDATA: return f
        if role==ROLE_THUMBNAIL: return self._thumbs.get(f["id"])
        return None
    def set_files(self, files):
        self.beginResetModel(); self._files=list(files); self._thumbs.clear(); self.endResetModel()
    def append_files(self, files):
        if not files: return
        first=len(self._files)
        self.beginInsertRows(QModelIndex(),first,first+len(files)-1); self._files.extend(files); self.endInsertRows()
    def set_thumbnail(self, fid, pixmap):
        self._thumbs[fid]=pixmap
        for i,f in enumerate(self._files):
            if f["id"]==fid:
                idx=self.index(i); self.dataChanged.emit(idx,idx,[ROLE_THUMBNAIL]); break
    def file_at(self, row): return self._files[row] if 0<=row<len(self._files) else None


class FileCardDelegate(QStyledItemDelegate):
    CARD_W=196; CARD_H=230; THUMB_H=132; PAD=10; ACCENT_W=3
    def __init__(self, parent=None):
        super().__init__(parent); self._hovered=QModelIndex(); self.theme=THEMES["Dark"]
    def set_hovered(self, idx): self._hovered=idx
    def set_theme(self, t): self.theme=t
    def sizeHint(self, option, index): return QSize(self.CARD_W, self.CARD_H)

    def paint(self, painter, option, index):
        painter.save(); painter.setRenderHint(QPainter.Antialiasing)
        t=self.theme; r=option.rect.adjusted(5,5,-5,-5)
        hovered = index==self._hovered
        selected = bool(option.state & QStyle.State_Selected)

        bg=QColor(t['bg_card'])
        if hovered: bg=QColor(t['bg_card_hover'])
        if selected: bg=QColor(t['bg_card_selected'])

        path=QPainterPath(); path.addRoundedRect(QRectF(r),12,12)
        grad=QLinearGradient(r.topLeft(),r.bottomRight())
        grad.setColorAt(0,bg); grad.setColorAt(1,bg.darker(108))
        painter.fillPath(path,QBrush(grad))

        if selected:
            painter.setPen(QPen(QColor(t['accent']),2)); painter.drawRoundedRect(QRectF(r),12,12)
        elif hovered:
            painter.setPen(QPen(QColor(t['border_light']),1)); painter.drawRoundedRect(QRectF(r),12,12)

        fd=index.data(ROLE_FILEDATA); thumb=index.data(ROLE_THUMBNAIL)

        # category accent strip
        if fd:
            cc=QColor(cat_color(fd.get("category","")))
            strip=QPainterPath(); strip.addRoundedRect(QRectF(r.x(),r.y()+8,self.ACCENT_W,r.height()-16),2,2)
            painter.fillPath(strip,cc)

        # thumbnail area
        tr=QRect(r.x()+self.PAD+self.ACCENT_W,r.y()+self.PAD,r.width()-2*self.PAD-self.ACCENT_W,self.THUMB_H)
        tp=QPainterPath(); tp.addRoundedRect(QRectF(tr),8,8)
        painter.setClipPath(tp); painter.fillPath(tp,QColor(t['bg_thumb']))

        if thumb and not thumb.isNull():
            sc=thumb.scaled(tr.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation)
            x=tr.x()+(tr.width()-sc.width())//2; y=tr.y()+(tr.height()-sc.height())//2
            painter.drawPixmap(x,y,sc)
            if hovered:
                ov=QPainterPath(); ov.addRoundedRect(QRectF(tr),8,8)
                painter.fillPath(ov,QColor(0,0,0,25))
        elif fd:
            ext_t=fd.get("extension","").upper(); cc=QColor(cat_color(fd.get("category","")))
            g2=QLinearGradient(tr.topLeft(),tr.bottomRight())
            g2.setColorAt(0,cc.darker(250)); g2.setColorAt(1,cc.darker(400))
            painter.fillPath(tp,QBrush(g2))
            painter.setPen(QColor(cc.lighter(160)))
            fnt=painter.font(); fnt.setPixelSize(20); fnt.setBold(True); painter.setFont(fnt)
            painter.drawText(tr,Qt.AlignCenter,ext_t or "FILE")
        painter.setClipping(False)

        # extension badge
        if fd:
            ext_s=fd.get("extension","").upper().lstrip(".")
            if ext_s:
                fnt=painter.font(); fnt.setPixelSize(9); fnt.setBold(True); painter.setFont(fnt)
                fm=QFontMetrics(fnt); bw=fm.horizontalAdvance(ext_s)+10; bh=16
                bx=tr.right()-bw-4; by=tr.bottom()-bh-4
                badge=QPainterPath(); badge.addRoundedRect(QRectF(bx,by,bw,bh),4,4)
                is_gif = fd.get("extension","").lower()==".gif"
                painter.fillPath(badge,QColor("#22c55e") if is_gif else QColor(0,0,0,140))
                painter.setPen(QColor("#ffffff"))
                painter.drawText(QRect(int(bx),int(by),int(bw),int(bh)),Qt.AlignCenter,"GIF" if is_gif else ext_s)

        # filename
        text_y=tr.bottom()+10
        text_r=QRect(r.x()+self.PAD+self.ACCENT_W,text_y,r.width()-2*self.PAD-self.ACCENT_W,18)
        painter.setPen(QColor(t['text_primary']))
        fnt=painter.font(); fnt.setPixelSize(12); fnt.setBold(False); painter.setFont(fnt)
        fm=QFontMetrics(fnt); name=fd["name"] if fd else (index.data(Qt.DisplayRole) or "")
        painter.drawText(text_r,Qt.AlignLeft|Qt.AlignVCenter,fm.elidedText(name,Qt.ElideMiddle,text_r.width()))

        # info line
        if fd:
            info_r=QRect(r.x()+self.PAD+self.ACCENT_W,text_r.bottom()+2,r.width()-2*self.PAD-self.ACCENT_W,14)
            painter.setPen(QColor(t['text_muted'])); fnt.setPixelSize(10); painter.setFont(fnt)
            painter.drawText(info_r,Qt.AlignLeft|Qt.AlignVCenter,f"{fmt_size(fd.get('size',0))}  •  {fd.get('category','')}")
        painter.restore()


# ═══════════════════════════════════════════════════════════════
# PREVIEW PANEL  (animated GIF via QMovie)
# ═══════════════════════════════════════════════════════════════

class PreviewPanel(QWidget):
    open_location = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(280); self._current_path=None; self._media_player=None
        self._audio_output=None; self._loaded_font_id=-1; self._gif_movie=None
        self._build_ui()

    def _build_ui(self):
        lay=QVBoxLayout(self); lay.setContentsMargins(14,14,14,14); lay.setSpacing(10)
        self.title=QLabel("No file selected"); self.title.setObjectName("previewTitle"); self.title.setWordWrap(True)
        lay.addWidget(self.title)
        sep=QFrame(); sep.setFrameShape(QFrame.HLine); sep.setStyleSheet("max-height:1px;")
        lay.addWidget(sep)

        # stack: 0=empty 1=image 2=video 3=audio 4=text 5=font 6=nopreview 7=gif
        self.stack=QStackedWidget(); self.stack.setMinimumHeight(200)

        self._empty=QLabel("Select a file to preview"); self._empty.setAlignment(Qt.AlignCenter)
        self._empty.setStyleSheet("color:#64748b; font-size:13px;"); self.stack.addWidget(self._empty)

        self._img_scroll=QScrollArea(); self._img_scroll.setWidgetResizable(True)
        self._img_label=QLabel(); self._img_label.setAlignment(Qt.AlignCenter)
        self._img_scroll.setWidget(self._img_label); self.stack.addWidget(self._img_scroll)

        if HAS_MEDIA:
            self._video_w=QVideoWidget(); self.stack.addWidget(self._video_w)
        else:
            lbl=QLabel("Video preview needs QtMultimedia"); lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color:#64748b"); self.stack.addWidget(lbl)

        self._audio_box=QWidget(); alay=QVBoxLayout(self._audio_box); alay.setAlignment(Qt.AlignCenter)
        self._audio_icon=QLabel("🎵"); self._audio_icon.setStyleSheet("font-size:52px")
        self._audio_icon.setAlignment(Qt.AlignCenter); alay.addWidget(self._audio_icon)
        self._audio_slider=QSlider(Qt.Horizontal); self._audio_slider.setRange(0,1000); alay.addWidget(self._audio_slider)
        ab=QHBoxLayout()
        self._audio_play=QPushButton("▶  Play"); self._audio_play.setObjectName("accentBtn")
        self._audio_stop=QPushButton("■  Stop"); self._audio_stop.setObjectName("secondaryBtn")
        ab.addWidget(self._audio_play); ab.addWidget(self._audio_stop); alay.addLayout(ab)
        self._audio_time=QLabel("0:00 / 0:00"); self._audio_time.setAlignment(Qt.AlignCenter)
        self._audio_time.setStyleSheet("color:#94a3b8; font-size:11px"); alay.addWidget(self._audio_time)
        self.stack.addWidget(self._audio_box)

        self._text_edit=QPlainTextEdit(); self._text_edit.setReadOnly(True)
        self._text_edit.setMaximumBlockCount(2000); self.stack.addWidget(self._text_edit)

        self._font_box=QWidget(); flay=QVBoxLayout(self._font_box)
        self._font_sample=QLabel(); self._font_sample.setAlignment(Qt.AlignCenter)
        self._font_sample.setWordWrap(True); self._font_sample.setMinimumHeight(100); flay.addWidget(self._font_sample)
        self._font_label=QLabel(); self._font_label.setAlignment(Qt.AlignCenter)
        self._font_label.setStyleSheet("color:#94a3b8; font-size:11px"); flay.addWidget(self._font_label)
        self.stack.addWidget(self._font_box)

        self._no_preview=QLabel("No preview available for this file type")
        self._no_preview.setAlignment(Qt.AlignCenter); self._no_preview.setStyleSheet("color:#64748b")
        self.stack.addWidget(self._no_preview)

        # 7 – animated GIF
        self._gif_label=QLabel(); self._gif_label.setAlignment(Qt.AlignCenter)
        self._gif_scroll=QScrollArea(); self._gif_scroll.setWidgetResizable(True)
        self._gif_scroll.setWidget(self._gif_label); self.stack.addWidget(self._gif_scroll)

        lay.addWidget(self.stack, 1)

        sep2=QFrame(); sep2.setFrameShape(QFrame.HLine); sep2.setStyleSheet("max-height:1px;")
        lay.addWidget(sep2)
        self._props=QLabel(); self._props.setWordWrap(True)
        self._props.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._props.setStyleSheet("font-size:11px; color:#94a3b8; line-height:1.6")
        lay.addWidget(self._props)

        btn_row=QHBoxLayout()
        self._btn_open=QPushButton("📂 Open Location"); self._btn_open.setObjectName("secondaryBtn")
        self._btn_copy=QPushButton("📋 Copy Path"); self._btn_copy.setObjectName("secondaryBtn")
        btn_row.addWidget(self._btn_open); btn_row.addWidget(self._btn_copy); lay.addLayout(btn_row)
        self._btn_open.clicked.connect(lambda: self.open_location.emit(self._current_path or ""))
        self._btn_copy.clicked.connect(lambda: QApplication.clipboard().setText(self._current_path or ""))

        if HAS_MEDIA:
            self._audio_play.clicked.connect(self._toggle_play)
            self._audio_stop.clicked.connect(self._stop_media)
            self._audio_slider.sliderMoved.connect(self._seek_media)

    def _ensure_player(self):
        if not HAS_MEDIA: return
        if self._media_player is None:
            self._media_player=QMediaPlayer(); self._audio_output=QAudioOutput()
            self._media_player.setAudioOutput(self._audio_output)
            self._media_player.positionChanged.connect(self._on_pos)
            self._media_player.durationChanged.connect(lambda d: None)

    def _toggle_play(self):
        if not HAS_MEDIA or not self._media_player: return
        if self._media_player.playbackState()==QMediaPlayer.PlayingState:
            self._media_player.pause(); self._audio_play.setText("▶  Play")
        else: self._media_player.play(); self._audio_play.setText("⏸  Pause")

    def _stop_media(self):
        if self._media_player: self._media_player.stop(); self._audio_play.setText("▶  Play")

    def _seek_media(self, val):
        if self._media_player and self._media_player.duration()>0:
            self._media_player.setPosition(int(val/1000*self._media_player.duration()))

    def _on_pos(self, pos):
        dur=self._media_player.duration() if self._media_player else 0
        if dur>0:
            self._audio_slider.blockSignals(True); self._audio_slider.setValue(int(pos/dur*1000)); self._audio_slider.blockSignals(False)
        self._audio_time.setText(f"{self._fmt_ms(pos)} / {self._fmt_ms(dur)}")

    @staticmethod
    def _fmt_ms(ms): s=max(0,ms//1000); return f"{s//60}:{s%60:02d}"

    def show_file(self, fd):
        self._release_media(); self._stop_gif()
        self._current_path=fd.get("path",""); ext=fd.get("extension","").lower()
        self.title.setText(fd.get("name",""))
        if self._loaded_font_id>=0: QFontDatabase.removeApplicationFont(self._loaded_font_id); self._loaded_font_id=-1
        path=fd.get("path",""); exists=os.path.exists(path)

        if ext==".gif" and exists: self._show_gif(path)
        elif ext in IMAGE_EXTS and exists: self._show_image(path)
        elif ext in VIDEO_EXTS and exists and HAS_MEDIA: self._show_video(path)
        elif ext in AUDIO_EXTS and exists and HAS_MEDIA: self._show_audio(path)
        elif ext in TEXT_EXTS and exists: self._show_text(path)
        elif ext in FONT_EXTS and exists: self._show_font(path, fd.get("name",""))
        elif exists: self.stack.setCurrentIndex(6)
        else: self._empty.setText("File not found on disk"); self.stack.setCurrentIndex(0)

        props=[]
        props.append(f"<b>Path:</b> {fd.get('path','')}")
        props.append(f"<b>Size:</b> {fmt_size(fd.get('size',0))}")
        props.append(f"<b>Category:</b> {fd.get('category','')}")
        props.append(f"<b>Extension:</b> {fd.get('extension','')}")
        for key,label in [("modified_date","Modified"),("created_date","Created")]:
            if fd.get(key):
                try: dt=datetime.fromisoformat(fd[key]); props.append(f"<b>{label}:</b> {dt.strftime('%Y-%m-%d  %H:%M')}")
                except: props.append(f"<b>{label}:</b> {fd[key]}")
        self._props.setText("<br>".join(props))

    def _show_gif(self, path):
        self._gif_movie=QMovie(path)
        if not self._gif_movie.isValid(): self._show_image(path); return
        # scale nicely
        w=max(200, self._gif_scroll.viewport().width()-20)
        size = self._gif_movie.scaledSize()
        if size.isEmpty():
            self._gif_movie.jumpToFrame(0)
            size = self._gif_movie.currentImage().size()
        if not size.isEmpty() and size.width() > 0:
            ratio = min(w / size.width(), 600 / size.height())
            if ratio < 1:
                self._gif_movie.setScaledSize(QSize(int(size.width()*ratio), int(size.height()*ratio)))
        self._gif_label.setMovie(self._gif_movie)
        self._gif_movie.start()
        self.stack.setCurrentIndex(7)

    def _stop_gif(self):
        if self._gif_movie: self._gif_movie.stop(); self._gif_label.setMovie(None); self._gif_movie=None

    def _show_image(self, path):
        pix=QPixmap(path)
        if pix.isNull(): self.stack.setCurrentIndex(6); return
        w=self._img_scroll.viewport().width()-10
        if pix.width()>w: pix=pix.scaledToWidth(w,Qt.SmoothTransformation)
        self._img_label.setPixmap(pix); self.stack.setCurrentIndex(1)

    def _show_video(self, path):
        self._ensure_player(); self._media_player.setVideoOutput(self._video_w)
        self._media_player.setSource(QUrl.fromLocalFile(path)); self._media_player.play(); self.stack.setCurrentIndex(2)

    def _show_audio(self, path):
        self._ensure_player(); self._media_player.setVideoOutput(None)
        self._media_player.setSource(QUrl.fromLocalFile(path))
        self._audio_play.setText("▶  Play"); self._audio_slider.setValue(0)
        self._audio_time.setText("0:00 / 0:00"); self.stack.setCurrentIndex(3)

    def _show_text(self, path):
        try: txt=Path(path).read_text("utf-8",errors="replace")[:50_000]
        except: txt="(unable to read file)"
        self._text_edit.setPlainText(txt); self.stack.setCurrentIndex(4)

    def _show_font(self, path, name):
        fid=QFontDatabase.addApplicationFont(path); self._loaded_font_id=fid
        if fid<0: self._font_sample.setText("Unable to load font"); self._font_label.setText(""); self.stack.setCurrentIndex(5); return
        families=QFontDatabase.applicationFontFamilies(fid)
        if families:
            family=families[0]; self._font_sample.setFont(QFont(family,32))
            self._font_sample.setText("ABCDEFGHIJKLM\nabcdefghijklm\n0123456789 !@#$")
            self._font_label.setText(f"{family}  —  {name}")
        else: self._font_sample.setText("Font loaded but no families found"); self._font_label.setText(name)
        self.stack.setCurrentIndex(5)

    def _release_media(self):
        if self._media_player: self._media_player.stop(); self._media_player.setSource(QUrl())

    def clear_preview(self):
        self._release_media(); self._stop_gif()
        self.title.setText("No file selected"); self._props.setText(""); self.stack.setCurrentIndex(0)


# ═══════════════════════════════════════════════════════════════
# ORGANIZER TREE
# ═══════════════════════════════════════════════════════════════

class OrganizerTree(QWidget):
    file_selected = Signal(dict)
    def __init__(self, parent=None):
        super().__init__(parent); lay=QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
        self.tree=QTreeWidget(); self.tree.setHeaderLabels(["Name","Size","Extension","Path"])
        self.tree.setColumnWidth(0,320); self.tree.setColumnWidth(1,90); self.tree.setColumnWidth(2,70)
        self.tree.setIndentation(20); self.tree.setAnimated(True); self.tree.setRootIsDecorated(True)
        self.tree.itemClicked.connect(self._on_click)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_ctx)
        lay.addWidget(self.tree)

    def populate_by_type(self, db):
        self.tree.clear()
        if not db: return
        groups = db.get_files_by_category()
        for cat in sorted(groups.keys()):
            info=groups[cat]; total=info["total"]; files=info["files"]
            ts=sum(f.get("size",0) for f in files)
            node=QTreeWidgetItem(self.tree)
            node.setText(0,f"📁 {cat}  ({total:,} files)"); node.setText(1,fmt_size(ts))
            node.setData(0,Qt.UserRole,None)
            for f in files:
                child=QTreeWidgetItem(node); child.setText(0,f["name"]); child.setText(1,fmt_size(f.get("size",0)))
                child.setText(2,f.get("extension","")); child.setText(3,f.get("path",""))
                child.setData(0,Qt.UserRole,f)
            if total>len(files):
                more=QTreeWidgetItem(node); more.setText(0,f"  … and {total-len(files):,} more")
                more.setData(0,Qt.UserRole,None)

    def populate_by_folder(self, db):
        self.tree.clear()
        if not db: return
        files=db.get_folder_tree()
        if not files: return
        tree_dict={}
        for f in files:
            parts=Path(f["path"]).parts; node=tree_dict
            for p in parts[:-1]: node=node.setdefault(p,{})
            node[parts[-1]]=f

        # find common prefix
        all_parts=[Path(f["path"]).parts for f in files]
        common=0
        if all_parts:
            ml=min(len(p) for p in all_parts)
            for i in range(ml-1):
                if len(set(p[i] for p in all_parts))==1: common=i+1
                else: break

        def count_f(d):
            c=0
            for v in d.values():
                if isinstance(v,dict):
                    if "id" in v: c+=1
                    else: c+=count_f(v)
            return c

        def add(parent, d):
            folders={k:v for k,v in d.items() if isinstance(v,dict) and "id" not in v}
            leaf={k:v for k,v in d.items() if isinstance(v,dict) and "id" in v}
            for name in sorted(folders):
                fc=count_f(folders[name]); n=QTreeWidgetItem(parent)
                n.setText(0,f"📁 {name}  ({fc} files)"); n.setData(0,Qt.UserRole,None)
                add(n,folders[name])
            for name in sorted(leaf):
                f=leaf[name]; ch=QTreeWidgetItem(parent)
                ch.setText(0,f.get("name",name)); ch.setText(1,fmt_size(f.get("size",0)))
                ch.setText(2,f.get("extension","")); ch.setText(3,f.get("path",""))
                ch.setData(0,Qt.UserRole,f)

        nd=tree_dict
        for i in range(common):
            keys=[k for k in nd if isinstance(nd[k],dict) and "id" not in nd[k]]
            if len(keys)==1: nd=nd[keys[0]]
            else: break
        add(self.tree.invisibleRootItem(),nd)

    def _on_click(self, item, col):
        fd=item.data(0,Qt.UserRole)
        if fd and isinstance(fd,dict) and "id" in fd: self.file_selected.emit(fd)

    def _on_ctx(self, pos):
        item=self.tree.itemAt(pos)
        if not item: return
        fd=item.data(0,Qt.UserRole)
        if not fd or "id" not in fd: return
        menu=QMenu(self)
        a_open=menu.addAction("📂  Open File Location")
        a_copy=menu.addAction("📋  Copy Path"); a_name=menu.addAction("📝  Copy Name")
        action=menu.exec(self.tree.viewport().mapToGlobal(pos))
        if action==a_open: open_file_location(fd["path"])
        elif action==a_copy: QApplication.clipboard().setText(fd["path"])
        elif action==a_name: QApplication.clipboard().setText(fd["name"])


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

class SidebarWidget(QWidget):
    category_selected = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent); self.setFixedWidth(230); self._build_ui()
    def _build_ui(self):
        lay=QVBoxLayout(self); lay.setContentsMargins(12,16,12,12); lay.setSpacing(6)
        h=QLabel("STATISTICS"); h.setObjectName("sideHead"); lay.addWidget(h)
        self.lbl_total=QLabel("0 files"); self.lbl_total.setObjectName("statBig"); lay.addWidget(self.lbl_total)
        self.lbl_size=QLabel("0 B"); self.lbl_size.setObjectName("statSmall"); lay.addWidget(self.lbl_size)
        sep=QFrame(); sep.setFrameShape(QFrame.HLine); sep.setStyleSheet("max-height:1px;"); lay.addWidget(sep)
        h2=QLabel("CATEGORIES"); h2.setObjectName("sideHead"); lay.addWidget(h2)
        self._cat_area=QScrollArea(); self._cat_area.setWidgetResizable(True)
        self._cat_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._cat_widget=QWidget(); self._cat_layout=QVBoxLayout(self._cat_widget)
        self._cat_layout.setContentsMargins(0,0,0,0); self._cat_layout.setSpacing(2)
        self._cat_area.setWidget(self._cat_widget); lay.addWidget(self._cat_area,1)
        self._cat_btns=[]

    def update_stats(self, stats):
        tf=stats.get("total_files",0); ts=stats.get("total_size",0)
        self.lbl_total.setText(f"{tf:,} files"); self.lbl_size.setText(fmt_size(ts))
        for btn in self._cat_btns: btn.setParent(None); btn.deleteLater()
        self._cat_btns.clear()
        ab=QPushButton(f"All  ({tf})"); ab.setObjectName("catBtn"); ab.setCheckable(True); ab.setChecked(True)
        ab.clicked.connect(lambda: self._on_cat("All")); self._cat_layout.addWidget(ab); self._cat_btns.append(ab)
        for c in sorted(stats.get("by_category",[]),key=lambda x:x["count"],reverse=True):
            btn=QPushButton(f"{c['category']}  ({c['count']})"); btn.setObjectName("catBtn"); btn.setCheckable(True)
            cn=c["category"]; btn.clicked.connect(lambda checked,n=cn: self._on_cat(n))
            self._cat_layout.addWidget(btn); self._cat_btns.append(btn)
        self._cat_layout.addStretch()

    def _on_cat(self, name):
        for btn in self._cat_btns:
            btn.setChecked(btn.text().startswith(name+" ") or (name=="All" and btn.text().startswith("All")))
        self.category_selected.emit(name)


# ═══════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self, theme_mgr):
        super().__init__(); self._tm=theme_mgr
        self.setWindowTitle(f"{APP_NAME}  v{APP_VERSION}"); self.resize(1340,820)
        self._dbs={}; self._active_db=None; self._scan_worker=None; self._thumb_worker=None
        self._current_cat="All"; self._current_ext=""; self._current_query=""
        self._offset=0; self._total=0; self._sort="name"; self._view_mode="grid"
        self._build_ui(); self._restore_state(); self._start_thumb_worker()

    def _build_ui(self):
        central=QWidget(); self.setCentralWidget(central)
        main_lay=QVBoxLayout(central); main_lay.setContentsMargins(0,0,0,0); main_lay.setSpacing(0)

        tb=QWidget(); tb.setObjectName("topBar"); tb.setFixedHeight(54)
        tbl=QHBoxLayout(tb); tbl.setContentsMargins(14,8,14,8); tbl.setSpacing(10)

        self.tab_bar=QTabBar(); self.tab_bar.setExpanding(False); self.tab_bar.setTabsClosable(True)
        self.tab_bar.currentChanged.connect(self._on_tab_changed)
        self.tab_bar.tabCloseRequested.connect(self._on_tab_close); tbl.addWidget(self.tab_bar)

        btn_new=QToolButton(); btn_new.setText("+"); btn_new.setObjectName("addTabBtn")
        btn_new.setToolTip("Open or create a database"); btn_new.clicked.connect(self._open_or_create_db)
        tbl.addWidget(btn_new); tbl.addSpacing(10)

        self.search_input=QLineEdit(); self.search_input.setPlaceholderText("🔍  Search files…  (Ctrl+F)")
        self.search_input.setObjectName("searchBox"); self.search_input.setMinimumWidth(200)
        self.search_input.setClearButtonEnabled(True); tbl.addWidget(self.search_input,1)

        self.ext_combo=QComboBox(); self.ext_combo.setMinimumWidth(130)
        self.ext_combo.addItem("All Extensions"); tbl.addWidget(self.ext_combo)

        self.sort_combo=QComboBox(); self.sort_combo.addItems(["Name ↕","Size ↕","Date ↕"])
        self.sort_combo.setMinimumWidth(90); tbl.addWidget(self.sort_combo)

        self.view_combo=QComboBox()
        self.view_combo.addItems(["⊞ Grid","📂 By Type","🗂 By Folder"])
        self.view_combo.setMinimumWidth(115); self.view_combo.setToolTip("Auto-Organizer: Switch view")
        self.view_combo.currentIndexChanged.connect(self._on_view_mode); tbl.addWidget(self.view_combo)

        self.theme_combo=QComboBox()
        self.theme_combo.addItems([f"🎨 {n}" for n in ThemeManager.names()])
        self.theme_combo.setMinimumWidth(130); self.theme_combo.setToolTip("Theme")
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed); tbl.addWidget(self.theme_combo)

        btn_scan=QPushButton("📁 Scan"); btn_scan.setObjectName("accentBtn")
        btn_scan.clicked.connect(self._start_scan_dialog); tbl.addWidget(btn_scan)
        btn_export=QPushButton("💾 Export"); btn_export.setObjectName("secondaryBtn")
        btn_export.clicked.connect(self._export_csv); tbl.addWidget(btn_export)
        main_lay.addWidget(tb)

        self.progress=QProgressBar(); self.progress.setFixedHeight(3)
        self.progress.setTextVisible(False); self.progress.setRange(0,100)
        self.progress.setValue(0); self.progress.setVisible(False); main_lay.addWidget(self.progress)

        splitter=QSplitter(Qt.Horizontal); splitter.setHandleWidth(1)
        self.sidebar=SidebarWidget(); self.sidebar.category_selected.connect(self._on_category)
        splitter.addWidget(self.sidebar)

        center=QWidget(); ccl=QVBoxLayout(center); ccl.setContentsMargins(0,0,0,0); ccl.setSpacing(0)
        self._center_stack=QStackedWidget()

        # page 0: grid
        grid_page=QWidget(); gpl=QVBoxLayout(grid_page); gpl.setContentsMargins(0,0,0,0); gpl.setSpacing(0)
        self.file_model=FileListModel(); self.file_delegate=FileCardDelegate()
        self.file_delegate.set_theme(self._tm.t)
        self.grid_view=QListView(); self.grid_view.setViewMode(QListView.IconMode)
        self.grid_view.setResizeMode(QListView.Adjust); self.grid_view.setSpacing(4)
        self.grid_view.setUniformItemSizes(True); self.grid_view.setMovement(QListView.Static)
        self.grid_view.setWrapping(True); self.grid_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.grid_view.setModel(self.file_model); self.grid_view.setItemDelegate(self.file_delegate)
        self.grid_view.setMouseTracking(True); self.grid_view.viewport().installEventFilter(self)
        self.grid_view.clicked.connect(self._on_file_clicked)
        self.grid_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.grid_view.customContextMenuRequested.connect(self._on_context_menu)
        gpl.addWidget(self.grid_view,1)

        footer=QWidget(); footer.setObjectName("footer"); footer.setFixedHeight(34)
        fl=QHBoxLayout(footer); fl.setContentsMargins(14,0,14,0)
        self.lbl_footer=QLabel("Ready"); self.lbl_footer.setStyleSheet("color:#64748b; font-size:11px")
        fl.addWidget(self.lbl_footer); fl.addStretch()
        self.btn_load_more=QPushButton("Load more ↓"); self.btn_load_more.setObjectName("secondaryBtn")
        self.btn_load_more.setVisible(False); self.btn_load_more.clicked.connect(self._load_more)
        fl.addWidget(self.btn_load_more); gpl.addWidget(footer)
        self._center_stack.addWidget(grid_page)

        # page 1: organizer tree
        self.organizer=OrganizerTree(); self.organizer.file_selected.connect(self._on_tree_file)
        self._center_stack.addWidget(self.organizer)
        ccl.addWidget(self._center_stack); splitter.addWidget(center)

        self.preview=PreviewPanel(); self.preview.open_location.connect(lambda p: open_file_location(p))
        splitter.addWidget(self.preview); splitter.setSizes([230,740,370])
        main_lay.addWidget(splitter,1)

        self.status=QStatusBar(); self.setStatusBar(self.status)
        self.status.showMessage(f"Welcome to {APP_NAME} v{APP_VERSION}")

        self._search_timer=QTimer(); self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_search)
        self.search_input.textChanged.connect(lambda: self._search_timer.start(SEARCH_DEBOUNCE_MS))
        self.ext_combo.currentIndexChanged.connect(self._on_ext_changed)
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)

        QShortcut(QKeySequence("Ctrl+F"),self,self.search_input.setFocus)
        QShortcut(QKeySequence("Escape"),self,self._escape_pressed)
        QShortcut(QKeySequence("Ctrl+O"),self,self._open_or_create_db)
        QShortcut(QKeySequence("Ctrl+E"),self,self._export_csv)

    def eventFilter(self, obj, event):
        if obj==self.grid_view.viewport():
            if event.type()==QEvent.MouseMove:
                idx=self.grid_view.indexAt(event.pos())
                if idx!=self.file_delegate._hovered:
                    self.file_delegate.set_hovered(idx); self.grid_view.viewport().update()
            elif event.type()==QEvent.Leave:
                self.file_delegate.set_hovered(QModelIndex()); self.grid_view.viewport().update()
        return super().eventFilter(obj,event)

    def _on_theme_changed(self, idx):
        names=ThemeManager.names()
        if 0<=idx<len(names):
            self._tm.apply(names[idx]); self.file_delegate.set_theme(self._tm.t)
            self.grid_view.viewport().update(); self._save_state()

    def _on_view_mode(self, idx):
        modes=["grid","type","folder"]
        self._view_mode=modes[idx] if idx<len(modes) else "grid"
        if self._view_mode=="grid": self._center_stack.setCurrentIndex(0)
        elif self._view_mode=="type":
            self._center_stack.setCurrentIndex(1); self.organizer.populate_by_type(self._db())
        elif self._view_mode=="folder":
            self._center_stack.setCurrentIndex(1); self.organizer.populate_by_folder(self._db())

    def _on_tree_file(self, fd): self.preview.show_file(fd)

    def _open_or_create_db(self):
        path,_=QFileDialog.getOpenFileName(self,"Open or Create Database",str(DB_DIR),"SQLite Databases (*.db);;All Files (*)")
        if not path:
            path,_=QFileDialog.getSaveFileName(self,"Create New Database",str(DB_DIR/"my_assets.db"),"SQLite Databases (*.db)")
        if not path: return
        self._add_db(path)

    def _add_db(self, path):
        p=Path(path); db_id=p.stem
        if db_id in self._dbs:
            for i in range(self.tab_bar.count()):
                if self.tab_bar.tabData(i)==db_id: self.tab_bar.setCurrentIndex(i); return
        self._dbs[db_id]=AssetDatabase(p)
        idx=self.tab_bar.addTab(db_id); self.tab_bar.setTabData(idx,db_id)
        self.tab_bar.setCurrentIndex(idx); self._save_state()

    def _on_tab_changed(self, idx):
        if idx<0: self._active_db=None; self.preview.clear_preview(); self.file_model.set_files([]); return
        self._active_db=self.tab_bar.tabData(idx); self._refresh_all(); self._save_state()

    def _on_tab_close(self, idx):
        db_id=self.tab_bar.tabData(idx); self.tab_bar.removeTab(idx)
        if db_id in self._dbs: del self._dbs[db_id]
        if self._active_db==db_id:
            self._active_db=None
            if self.tab_bar.count()>0: self.tab_bar.setCurrentIndex(0)
        self._save_state()

    def _db(self):
        return self._dbs.get(self._active_db) if self._active_db else None

    def _start_scan_dialog(self):
        if not self._db():
            QMessageBox.information(self,"No Database","Open or create a database first (click the + tab)."); return
        d=QFileDialog.getExistingDirectory(self,"Select Directory to Scan")
        if not d: return
        if self._scan_worker and self._scan_worker.isRunning():
            QMessageBox.warning(self,"Busy","A scan is already running."); return
        self._scan_worker=ScanWorker(self._db().path,d)
        self._scan_worker.progress.connect(self._on_scan_progress)
        self._scan_worker.finished_ok.connect(self._on_scan_done)
        self.progress.setVisible(True); self.progress.setValue(0)
        self.status.showMessage(f"Scanning {d} …"); self._scan_worker.start()

    def _on_scan_progress(self, current, total, status):
        if total>0: self.progress.setValue(int(current/total*100))
        self.lbl_footer.setText(f"Scanning: {current:,} / {total:,}  ({status})")

    def _on_scan_done(self):
        self.progress.setVisible(False); self.status.showMessage("Scan complete ✓",5000)
        self._refresh_all(); self._scan_worker=None

    def _do_search(self):
        self._current_query=self.search_input.text().strip(); self._offset=0; self._load_files(True)

    def _on_category(self, cat): self._current_cat=cat; self._offset=0; self._load_files(True)

    def _on_ext_changed(self):
        txt=self.ext_combo.currentText(); self._current_ext=""
        if txt!="All Extensions" and " " in txt: self._current_ext=txt.split(" ")[0]
        self._offset=0; self._load_files(True)

    def _on_sort_changed(self):
        self._sort=["name","size","date"][self.sort_combo.currentIndex()]
        self._offset=0; self._load_files(True)

    def _load_files(self, reset=False):
        db=self._db()
        if not db: self.file_model.set_files([]); self.lbl_footer.setText("No database loaded"); return
        files,total=db.search(query=self._current_query,
            category=self._current_cat if self._current_cat!="All" else None,
            extension=self._current_ext or None,limit=PAGE_SIZE,offset=self._offset,sort=self._sort)
        self._total=total
        if reset: self.file_model.set_files(files); self.preview.clear_preview()
        else: self.file_model.append_files(files)
        self._offset+=len(files)
        self.lbl_footer.setText(f"{self._offset:,} / {total:,} files")
        self.btn_load_more.setVisible(self._offset<total)
        self._queue_thumbnails(files)

    def _load_more(self): self._load_files(False)

    def _refresh_all(self):
        db=self._db()
        if not db: return
        st=db.stats(); self.sidebar.update_stats(st)
        self.ext_combo.blockSignals(True); self.ext_combo.clear(); self.ext_combo.addItem("All Extensions")
        for e in st.get("by_extension",[]): self.ext_combo.addItem(f"{e['extension']}  ({e['count']})")
        self.ext_combo.blockSignals(False)
        self._offset=0; self._load_files(True)
        if self._view_mode=="type": self.organizer.populate_by_type(db)
        elif self._view_mode=="folder": self.organizer.populate_by_folder(db)

    def _start_thumb_worker(self):
        self._thumb_worker=ThumbWorker(); self._thumb_worker.ready.connect(self._on_thumb_ready)
        self._thumb_worker.start()

    def _queue_thumbnails(self, files):
        if not self._thumb_worker: return
        items=[(f["id"],f["path"],f.get("extension","").lower()) for f in files if f.get("extension","").lower() in IMAGE_EXTS]
        if items: self._thumb_worker.enqueue(items)

    def _on_thumb_ready(self, fid, qimg): self.file_model.set_thumbnail(fid,QPixmap.fromImage(qimg))

    def _on_file_clicked(self, index):
        fd=index.data(ROLE_FILEDATA)
        if fd: self.preview.show_file(fd)

    def _on_context_menu(self, pos):
        idx=self.grid_view.indexAt(pos); fd=idx.data(ROLE_FILEDATA) if idx.isValid() else None
        if not fd: return
        menu=QMenu(self); menu.setStyleSheet(build_ctx_qss(self._tm.t))
        a_open=menu.addAction("📂  Open File Location")
        a_copy=menu.addAction("📋  Copy Path"); a_name=menu.addAction("📝  Copy Name")
        action=menu.exec(self.grid_view.viewport().mapToGlobal(pos))
        if action==a_open: open_file_location(fd["path"])
        elif action==a_copy: QApplication.clipboard().setText(fd["path"])
        elif action==a_name: QApplication.clipboard().setText(fd["name"])

    def _export_csv(self):
        db=self._db()
        if not db: return
        path,_=QFileDialog.getSaveFileName(self,"Export CSV",
            str(Path.home()/f"asset_export_{datetime.now():%Y%m%d_%H%M}.csv"),"CSV Files (*.csv)")
        if not path: return
        files,_=db.search(query=self._current_query,
            category=self._current_cat if self._current_cat!="All" else None,
            extension=self._current_ext or None,limit=999_999,offset=0,sort=self._sort)
        try:
            with open(path,"w",newline="",encoding="utf-8") as f:
                w=csv.writer(f); w.writerow(["Name","Path","Extension","Category","Size","Modified","Created"])
                for fd in files: w.writerow([fd["name"],fd["path"],fd["extension"],fd["category"],fd["size"],fd.get("modified_date",""),fd.get("created_date","")])
            self.status.showMessage(f"Exported {len(files)} files → {path}",5000)
        except Exception as e: QMessageBox.warning(self,"Export Error",str(e))

    def _escape_pressed(self):
        if self.search_input.hasFocus(): self.search_input.clear(); self.grid_view.setFocus()

    def _save_state(self):
        cfg=load_config()
        cfg["databases"]={did:str(db.path) for did,db in self._dbs.items()}
        cfg["active"]=self._active_db or ""
        cfg["geometry"]={"x":self.x(),"y":self.y(),"w":self.width(),"h":self.height()}
        cfg["theme"]=self._tm.current_name
        save_config(cfg)

    def _restore_state(self):
        cfg=load_config(); geo=cfg.get("geometry")
        if geo: self.setGeometry(geo.get("x",100),geo.get("y",100),geo.get("w",1340),geo.get("h",820))
        theme=cfg.get("theme","Dark"); names=ThemeManager.names()
        if theme in names:
            idx=names.index(theme)
            self.theme_combo.blockSignals(True); self.theme_combo.setCurrentIndex(idx); self.theme_combo.blockSignals(False)
            self._tm.apply(theme); self.file_delegate.set_theme(self._tm.t)
        dbs=cfg.get("databases",{})
        for did,dpath in dbs.items():
            if Path(dpath).exists():
                self._dbs[did]=AssetDatabase(Path(dpath))
                idx=self.tab_bar.addTab(did); self.tab_bar.setTabData(idx,did)
        active=cfg.get("active","")
        if active:
            for i in range(self.tab_bar.count()):
                if self.tab_bar.tabData(i)==active: self.tab_bar.setCurrentIndex(i); break

    def closeEvent(self, event):
        self._save_state()
        if self._thumb_worker: self._thumb_worker.stop(); self._thumb_worker.quit(); self._thumb_worker.wait(2000)
        if self._scan_worker and self._scan_worker.isRunning(): self._scan_worker.stop(); self._scan_worker.quit(); self._scan_worker.wait(3000)
        self.preview.clear_preview(); super().closeEvent(event)


# ═══════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════

def main():
    try: QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    except: pass
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME); app.setApplicationVersion(APP_VERSION); app.setStyle("Fusion")
    tm = ThemeManager(app); tm.apply("Dark")
    win = MainWindow(tm); win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
