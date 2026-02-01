
# EAM — Editing Asset Manager v1.0

**EAM (Editing Asset Manager)** is a lightweight, modern PySide6 desktop application for cataloging, browsing, and previewing creative/editing assets — images, videos, audio, fonts, documents, project files, and more.

Built for editors, motion designers, and creators who want fast access to large asset libraries without bloated DAM software.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![PySide6](https://img.shields.io/badge/PySide6-Qt6-green)
![License](https://img.shields.io/badge/License-MIT-orange)

---

## ✨ Features

| Feature | Description |
|------|------------|
| **Multi-Database Tabs** | Open and switch between multiple asset catalogs |
| **Background Scanning** | Scan large folders without freezing the UI |
| **Auto-Organizer** | Grid view, Tree by File Type, or Tree by Folder |
| **Live Preview Panel** | Images, video, audio, animated GIFs, fonts, text |
| **Animated GIF Support** | Full looping animation via `QMovie` |
| **7 Themes** | Dark, Light, Midnight, Extra Dark, Purple, Glass Dark, Glass Light |
| **Smart Search** | Real-time search with filters and sorting |
| **Lazy Thumbnails** | Disk-cached thumbnails for low memory usage |
| **Pagination** | 120 items per page with “Load More” |
| **Export to CSV** | Export filtered results instantly |
| **Session Persistence** | Remembers open databases, window state, theme |

---

## 🚀 Quick Start

### Install Dependencies

```bash
pip install PySide6 Pillow
````

### Run EAM

```bash
python asset_catalog_desktop.py
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut   | Action                     |
| ---------- | -------------------------- |
| `Ctrl + F` | Focus search               |
| `Ctrl + O` | Open or create database    |
| `Ctrl + E` | Export current view to CSV |
| `Esc`      | Clear search / unfocus     |

---

## 🧭 Typical Workflow

1. **Open or Create a Database** — `Ctrl + O`
2. **Scan a Directory** — Choose a folder containing assets
3. **Browse Assets** — Use grid or tree organizer
4. **Preview Files** — Click any item to preview instantly
5. **Filter & Search** — By name, category, extension, or sort order
6. **Export** — Save current results as CSV

---

## 🛠 CLI Scanner (Optional)

For headless environments or batch jobs, EAM includes a CLI scanner:

```bash
python scan_assets.py
```

This generates `.db` files fully compatible with the desktop app.

---

## 🖼 Supported Previews

### Images

PNG, JPG, JPEG, WEBP, BMP, TIFF, ICO, SVG

### Animated GIF

* Full animation playback (looping)

### Video

MP4, MOV, AVI, MKV, WEBM, FLV, WMV

### Audio

MP3, WAV, FLAC, AAC, OGG, M4A
(play / pause / seek)

### Fonts

TTF, OTF (live rendered previews)

### Text & Code

TXT, CSV, JSON, MD, PY, JS, HTML, CSS, XML, YAML, and more

> Some file types (project files, archives, 3D models) are cataloged but not previewed.

---

## 🧱 Platform Notes

| Platform    | Notes                                |
| ----------- | ------------------------------------ |
| **Windows** | Works out of the box                 |
| **macOS**   | Works out of the box                 |
| **Linux**   | Media playback may require GStreamer |

```bash
sudo apt install gstreamer1.0-plugins-good \
                 gstreamer1.0-plugins-bad \
                 gstreamer1.0-plugins-ugly
```

If media playback isn’t available, EAM still functions fully as a catalog browser.

---

## 📂 Data Storage

All application data is stored in:

```
~/.eam/
├── config.json      # Window state, theme, open databases
├── databases/       # Default .db catalog location
└── thumbnails/      # Cached image thumbnails
```

---

## 📦 Requirements

* Python **3.9+**
* PySide6 **≥ 6.5**
* Pillow **≥ 9.0** *(recommended for thumbnails)*

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## 💡 About

EAM is designed to be **fast**, **local-first**, and **editor-friendly** — no cloud, no subscriptions, no vendor lock-in.

If you work with large asset libraries, EAM keeps them organized and instantly accessible.


