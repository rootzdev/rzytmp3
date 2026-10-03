"""RZYTMP3 - YouTube'dan MP3 indirici (tek şarkı ya da oynatma listesi).

Kullanım:
  python rzytmp3.py                                  -> pencere
  python rzytmp3.py <link> [<link> ...] [seçenekler] -> komut satırı
  python rzytmp3.py --kur                            -> ffmpeg + Deno'yu bin\\ klasörüne indir

Seçenekler:
  -o, --klasor KLASOR   indirilecek klasör (varsayılan: Müzik\\YouTube)
  -k, --kalite KBPS     320 / 256 / 192 / 128 (varsayılan 320)
  --tekli               linkte liste olsa bile sadece o videoyu indir
  --tekrar              daha önce indirilenleri de yeniden indir

Developed by rootzdev
Copyright (c) 2026 rootzdev — GNU GPLv3 (LICENSE, NOTICE)
"""
import argparse
import importlib.util
import json
import os
import queue
import re
import shutil
import ssl
import sys
import threading
import urllib.request
import webbrowser
import zipfile

APP_ID = "rzytmp3"
APP_NAME = "RZYTMP3"
AUTHOR = "rootzdev"
VERSION = "1.3.0"
DISCORD = "discord.gg/C3zPSNrTY2"
COPYRIGHT = "Copyright © 2026 rootzdev"
LICENSE_NAME = "GPLv3"
QUALITIES = ["128", "192", "256", "320"]
ARCHIVE_FILE = ".rzytmp3_archive.txt"

TOOLS = {
    "ffmpeg": {"url": "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
               "files": ["ffmpeg.exe", "ffprobe.exe"]},
    "deno": {"url": "https://github.com/denoland/deno/releases/latest/download/deno-x86_64-pc-windows-msvc.zip",
             "files": ["deno.exe"]},
}

STRINGS = {
    "tr": {
        "subtitle": "YouTube → MP3  ·  tek şarkı ya da liste",
        "links": "Linkler",
        "placeholder": "Linkleri buraya yapıştır (her satıra bir tane)…",
        "paste": "Yapıştır",
        "clear": "Temizle",
        "options": "Kayıt yeri ve seçenekler",
        "browse": "Seç…",
        "open": "Aç",
        "quality": "Kalite",
        "playlist": "Tüm liste",
        "playlist_folder": "Listeye klasör aç",
        "skip_existing": "İndirilmişleri atla",
        "download": "İNDİR",
        "stop": "Durdur",
        "ready": "Hazır",
        "stopping": "Durduruluyor…",
        "finished": "Bitti",
        "log": "Kayıt",
        "get_missing": "Eksikleri indir",
        "need_link": "En az bir link yapıştır.",
        "folder_error": "Klasör oluşturulamadı:\n%s",
        "no_ytdlp": "yt-dlp kurulu değil.\n\npip install -U -r requirements.txt",
        "no_ffmpeg": "ffmpeg yok. Alttaki 'Eksikleri indir'e bas.",
        "install_question": "Şunlar indirilip program klasöründeki bin\\ içine konacak:\n\n%s\n\nDevam edilsin mi?",
        "quit_question": "İşlem sürüyor. Çıkılsın mı?",
        "language_busy": "İşlem sürerken dil değiştirilemez.",
        "missing": "Eksik: %s → alttaki 'Eksikleri indir'",
        "ytdlp_hint": "  (yt-dlp için: pip install -U -r requirements.txt)",
        "ready_log": "Hazır. Linkleri yapıştır, İNDİR'e bas.",
        "job_start": "%d link → %s",
        "starting": "Başlıyor: ",
        "cancelled": "Durduruldu.",
        "user_cancel": "Kullanıcı durdurdu",
        "exists": "Zaten var: ",
        "unavailable": "Kullanılamıyor, atlandı: ",
        "no_deno": "Deno yok: bazı şarkılar inmeyebilir ya da düşük kalitede inebilir (alttan 'Eksikleri indir').",
        "hidden_videos": "Listedeki bazı videolar YouTube'da kaldırılmış/gizli, atlanacak.",
        "summary": "%d indirildi · %d zaten vardı · %d kullanılamıyor · %d hata",
        "tool_downloading": "%s indiriliyor… %.0f MB",
        "tool_installed": "%s kuruldu → %s",
        "tool_not_in_zip": "zip içinde bulunamadı: ",
        "tool_failed": "%s indirilemedi: %s",
        "tool_present": "%s zaten var.",
        "cli_no_ytdlp": "yt-dlp kurulu değil:  pip install -U -r requirements.txt",
        "cli_no_ffmpeg": "ffmpeg yok:  python rzytmp3.py --kur",
        "cli_header": "%s %s | Klasör: %s | %s kbps",
        "cli_description": "%s - YouTube'dan MP3 indirici. Developed by %s.",
        "help_links": "video ya da oynatma listesi linkleri (boşsa pencere açılır)",
        "help_folder": "indirilecek klasör",
        "help_quality": "MP3 kalitesi (kbps)",
        "help_single": "linkte liste olsa bile sadece o videoyu indir",
        "help_redownload": "daha önce indirilenleri de yeniden indir",
        "help_install": "ffmpeg + Deno'yu bin\\ klasörüne indir",
        "about_title": "Hakkında",
        "about": "%s %s\n%s\n\nBu program özgür yazılımdır: GNU Genel Kamu Lisansı sürüm 3 (GPLv3) koşulları "
                 "altında dağıtabilir ve değiştirebilirsiniz. Değiştirilmiş sürümler de GPLv3 ile, kaynak "
                 "koduyla paylaşılmalı ve \"Developed by rootzdev\" atfı korunmalıdır (NOTICE).\n\n"
                 "Program HİÇBİR GARANTİ OLMADAN sunulur.\n\nLisans: LICENSE dosyası ya da "
                 "https://www.gnu.org/licenses/gpl-3.0\nDiscord: %s",
    },
    "en": {
        "subtitle": "YouTube → MP3  ·  single track or playlist",
        "links": "Links",
        "placeholder": "Paste links here (one per line)…",
        "paste": "Paste",
        "clear": "Clear",
        "options": "Save location & options",
        "browse": "Browse…",
        "open": "Open",
        "quality": "Quality",
        "playlist": "Whole playlist",
        "playlist_folder": "Playlist folder",
        "skip_existing": "Skip downloaded",
        "download": "DOWNLOAD",
        "stop": "Stop",
        "ready": "Ready",
        "stopping": "Stopping…",
        "finished": "Done",
        "log": "Log",
        "get_missing": "Get missing",
        "need_link": "Paste at least one link.",
        "folder_error": "Could not create the folder:\n%s",
        "no_ytdlp": "yt-dlp is not installed.\n\npip install -U -r requirements.txt",
        "no_ffmpeg": "ffmpeg is missing. Click 'Get missing' below.",
        "install_question": "The following will be downloaded into the bin\\ folder next to the app:\n\n%s\n\nContinue?",
        "quit_question": "A job is still running. Quit anyway?",
        "language_busy": "The language can't be changed while a job is running.",
        "missing": "Missing: %s → click 'Get missing' below",
        "ytdlp_hint": "  (for yt-dlp: pip install -U -r requirements.txt)",
        "ready_log": "Ready. Paste your links and press DOWNLOAD.",
        "job_start": "%d link(s) → %s",
        "starting": "Starting: ",
        "cancelled": "Stopped.",
        "user_cancel": "Stopped by user",
        "exists": "Already downloaded: ",
        "unavailable": "Unavailable, skipped: ",
        "no_deno": "Deno is missing: some tracks may fail or download in lower quality (use 'Get missing' below).",
        "hidden_videos": "Some videos in this playlist are removed or private and will be skipped.",
        "summary": "%d downloaded · %d already had · %d unavailable · %d errors",
        "tool_downloading": "Downloading %s… %.0f MB",
        "tool_installed": "%s installed → %s",
        "tool_not_in_zip": "not found in the zip: ",
        "tool_failed": "%s could not be downloaded: %s",
        "tool_present": "%s already present.",
        "cli_no_ytdlp": "yt-dlp is not installed:  pip install -U -r requirements.txt",
        "cli_no_ffmpeg": "ffmpeg is missing:  python rzytmp3.py --install",
        "cli_header": "%s %s | Folder: %s | %s kbps",
        "cli_description": "%s - YouTube to MP3 downloader. Developed by %s.",
        "help_links": "video or playlist links (opens the window if empty)",
        "help_folder": "download folder",
        "help_quality": "MP3 quality (kbps)",
        "help_single": "download only that video even if the link has a playlist",
        "help_redownload": "download again even if already downloaded",
        "help_install": "download ffmpeg + Deno into the bin\\ folder",
        "about_title": "About",
        "about": "%s %s\n%s\n\nThis program is free software: you can redistribute it and/or modify it under "
                 "the terms of the GNU General Public License version 3 (GPLv3). Modified versions must also "
                 "be shared under GPLv3 with their source code and must keep the \"Developed by rootzdev\" "
                 "attribution (NOTICE).\n\nThis program comes with ABSOLUTELY NO WARRANTY.\n\nLicense: the "
                 "LICENSE file or https://www.gnu.org/licenses/gpl-3.0\nDiscord: %s",
    },
}

language = "tr"


def t(key):
    return STRINGS[language].get(key) or STRINGS["en"][key]


def system_language():
    try:
        import ctypes
        return "tr" if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF == 0x1F else "en"
    except Exception:
        return "en"


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(name):
    base = getattr(sys, "_MEIPASS", app_dir())
    return os.path.join(base, name)


def bin_dir():
    return os.path.join(app_dir(), "bin")


def settings_path():
    root = os.environ.get("APPDATA") or os.path.expanduser("~")
    path = os.path.join(root, APP_ID)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, "settings.json")


def load_settings():
    try:
        with open(settings_path(), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_settings(settings):
    try:
        with open(settings_path(), "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def find_local(exe):
    for folder in (bin_dir(), app_dir()):
        path = os.path.join(folder, exe)
        if os.path.isfile(path):
            return path
    return None


def find_ffmpeg():
    path = find_local("ffmpeg.exe") or shutil.which("ffmpeg")
    return os.path.dirname(path) if path else None


def find_deno():
    default = os.path.join(os.path.expanduser("~"), ".deno", "bin", "deno.exe")
    return find_local("deno.exe") or shutil.which("deno") or (default if os.path.isfile(default) else None)


def has_ytdlp():
    return importlib.util.find_spec("yt_dlp") is not None


def missing_tools():
    missing = []
    if not has_ytdlp():
        missing.append("yt-dlp")
    if not find_ffmpeg():
        missing.append("ffmpeg")
    if not find_deno():
        missing.append("deno")
    return missing


def default_folder():
    return os.path.join(os.path.expanduser("~"), "Music", "YouTube")


def ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def download_tool(name, emit):
    tool = TOOLS[name]
    target = bin_dir()
    os.makedirs(target, exist_ok=True)
    temp = os.path.join(target, name + ".zip.part")
    request = urllib.request.Request(tool["url"], headers={"User-Agent": "%s/%s" % (APP_ID, VERSION)})
    try:
        with urllib.request.urlopen(request, timeout=60, context=ssl_context()) as response, open(temp, "wb") as f:
            total = int(response.headers.get("Content-Length") or 0)
            done = 0
            while True:
                chunk = response.read(1 << 16)
                if not chunk:
                    break
                f.write(chunk)
                done += len(chunk)
                emit("progress", {"title": t("tool_downloading") % (name, done / 1048576),
                                  "percent": done * 100.0 / total if total else None,
                                  "index": None, "count": None})
        wanted = {x.lower() for x in tool["files"]}
        found = set()
        with zipfile.ZipFile(temp) as archive:
            for member in archive.infolist():
                base = os.path.basename(member.filename).lower()
                if base in wanted:
                    with archive.open(member) as src, open(os.path.join(target, base), "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    found.add(base)
        if found != wanted:
            raise RuntimeError(t("tool_not_in_zip") + ", ".join(sorted(wanted - found)))
    finally:
        if os.path.exists(temp):
            os.remove(temp)
    emit("log", ("ok", t("tool_installed") % (name, target)))


ANSI_RE = re.compile(r"\x1b?\[[0-9;]*m")
UNAVAILABLE_MARKERS = ("Video unavailable", "Private video", "This video is not available",
                       "video has been removed", "not available in your country", "members-only")


def clean_message(msg):
    msg = ANSI_RE.sub("", msg).strip()
    for prefix in ("ERROR: ", "WARNING: "):
        if msg.startswith(prefix):
            return msg[len(prefix):]
    return msg


class YdlLogger:
    def __init__(self, downloader):
        self.dl = downloader

    def debug(self, msg):
        msg = clean_message(msg)
        if "has already been recorded in the archive" in msg:
            self.dl.stats["skipped"] += 1
            title = msg.split("]", 1)[-1].replace("has already been recorded in the archive", "").strip()
            self.dl.emit("log", ("muted", t("exists") + title))

    def info(self, msg):
        pass

    def warning(self, msg):
        msg = clean_message(msg)
        if "No supported JavaScript runtime" in msg:
            msg = t("no_deno")
        elif "unavailable videos are hidden" in msg:
            msg = t("hidden_videos")
        if msg in self.dl.seen_warnings:
            return
        self.dl.seen_warnings.add(msg)
        self.dl.emit("log", ("warn", msg))

    def error(self, msg):
        msg = clean_message(msg)
        if any(marker in msg for marker in UNAVAILABLE_MARKERS):
            self.dl.stats["unavailable"] += 1
            self.dl.emit("log", ("muted", t("unavailable") + msg.replace("[youtube] ", "")))
            return
        self.dl.stats["errors"] += 1
        self.dl.emit("log", ("error", msg))


class SilentLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


class Downloader:
    def __init__(self, folder, quality="320", playlist=True, playlist_folder=True, skip_existing=True, emit=None):
        self.folder = folder
        self.quality = quality
        self.playlist = playlist
        self.playlist_folder = playlist_folder
        self.skip_existing = skip_existing
        self.emit = emit or (lambda kind, data: None)
        self.cancelled = False
        self.stats = {"done": 0, "errors": 0, "skipped": 0, "unavailable": 0}
        self.seen_warnings = set()

    def _js_runtime(self, options):
        deno = find_deno()
        if deno:
            options["js_runtimes"] = {"deno": {"path": deno}}
        return options

    def _options(self, template):
        options = {
            "format": "bestaudio/best",
            "outtmpl": template,
            "noplaylist": not self.playlist,
            "ignoreerrors": True,
            "windowsfilenames": True,
            "writethumbnail": True,
            "quiet": True,
            "noprogress": True,
            "color": {"stdout": "never", "stderr": "never"},
            "logger": YdlLogger(self),
            "progress_hooks": [self._on_progress],
            "postprocessor_hooks": [self._on_postprocess],
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": self.quality},
                {"key": "FFmpegMetadata", "add_metadata": True},
                {"key": "FFmpegThumbnailsConvertor", "format": "jpg", "when": "before_dl"},
                {"key": "EmbedThumbnail"},
            ],
        }
        ffmpeg = find_ffmpeg()
        if ffmpeg:
            options["ffmpeg_location"] = ffmpeg
        if self.skip_existing:
            options["download_archive"] = os.path.join(self.folder, ARCHIVE_FILE)
        return self._js_runtime(options)

    def _is_playlist(self, url):
        from yt_dlp import YoutubeDL
        options = self._js_runtime({"quiet": True, "no_warnings": True, "noplaylist": not self.playlist,
                                    "logger": SilentLogger()})
        try:
            with YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False, process=False)
                if info and info.get("_type") in ("url", "url_transparent") and info.get("url"):
                    info = ydl.extract_info(info["url"], download=False, process=False)
        except Exception:
            return False
        return bool(info) and info.get("_type") == "playlist"

    def _template(self, url):
        if self.playlist and self.playlist_folder and self._is_playlist(url):
            return os.path.join(self.folder, "%(playlist_title)s", "%(playlist_index)03d - %(title)s.%(ext)s")
        return os.path.join(self.folder, "%(title)s.%(ext)s")

    def _on_progress(self, d):
        if self.cancelled:
            from yt_dlp.utils import DownloadCancelled
            raise DownloadCancelled(t("user_cancel"))
        info = d.get("info_dict") or {}
        data = {"title": info.get("title") or "?", "index": info.get("playlist_index"),
                "count": info.get("n_entries") or info.get("playlist_count"), "percent": None}
        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                data["percent"] = min(100.0, d.get("downloaded_bytes", 0) * 100.0 / total)
            self.emit("progress", data)
        elif status == "finished":
            data["percent"] = 100.0
            self.emit("progress", data)

    def _on_postprocess(self, d):
        if d.get("status") == "finished" and d.get("postprocessor") == "MoveFiles":
            self.stats["done"] += 1
            path = (d.get("info_dict") or {}).get("filepath") or ""
            self.emit("log", ("ok", os.path.basename(path)))

    def run(self, urls):
        from yt_dlp import YoutubeDL
        from yt_dlp.utils import DownloadCancelled
        os.makedirs(self.folder, exist_ok=True)
        for url in urls:
            if self.cancelled:
                break
            self.emit("log", ("info", t("starting") + url))
            try:
                with YoutubeDL(self._options(self._template(url))) as ydl:
                    ydl.download([url])
            except DownloadCancelled:
                self.emit("log", ("warn", t("cancelled")))
                break
            except Exception as e:
                self.stats["errors"] += 1
                self.emit("log", ("error", str(e)))
        return self.stats


def summary(stats):
    return t("summary") % (stats["done"], stats["skipped"], stats["unavailable"], stats["errors"])


def cli_emit(kind, data):
    if kind == "log":
        print("\r" + data[1] + " " * 10)
    elif kind == "progress":
        index = "[%s/%s] " % (data["index"], data["count"] or "?") if data["index"] else ""
        percent = "%%%3.0f" % data["percent"] if data["percent"] is not None else ""
        print("\r%s%s %s   " % (index, data["title"][:60], percent), end="", flush=True)


def cli_install():
    for name, finder in (("ffmpeg", find_ffmpeg), ("deno", find_deno)):
        if finder():
            print(t("tool_present") % name)
            continue
        try:
            download_tool(name, cli_emit)
        except Exception as e:
            print("\n" + t("tool_failed") % (name, e))
            return 1
    return 0


def cli(args):
    if not has_ytdlp():
        print(t("cli_no_ytdlp"))
        return 1
    if not find_ffmpeg():
        print(t("cli_no_ffmpeg"))
        return 1
    folder = os.path.abspath(args.folder or default_folder())
    dl = Downloader(folder, args.quality, playlist=not args.single, skip_existing=not args.redownload,
                    emit=cli_emit)
    print(t("cli_header") % (APP_NAME, VERSION, folder, args.quality))
    try:
        dl.run(args.links)
    except KeyboardInterrupt:
        print("\n" + t("cancelled"))
    print("\n" + summary(dl.stats))
    return 0 if dl.stats["errors"] == 0 else 2


COLORS = {
    "bg": "#0d0f13", "card": "#15181e", "input": "#0a0c10", "border": "#252a33",
    "text": "#e7e9ee", "muted": "#7d8596", "accent": "#e5383b", "accent_hover": "#c42528",
    "green": "#3ccf7a", "yellow": "#e8b339", "red": "#ff5d5d", "discord": "#5865f2",
}
FONT = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_BOLD = ("Segoe UI Semibold", 10)
FONT_TITLE = ("Segoe UI Black", 18)
FONT_LOG = ("Consolas", 9)
WIDTH, HEIGHT = 760, 680


def set_app_id():
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("%s.%s" % (AUTHOR, APP_ID))
    except Exception:
        pass


def dark_title_bar(root):
    try:
        import ctypes
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        value = ctypes.c_int(1)
        for attribute in (20, 19):
            if ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attribute, ctypes.byref(value),
                                                          ctypes.sizeof(value)) == 0:
                break
    except Exception:
        pass


def run_window(restore=None):
    global language
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, font as tkfont

    settings = load_settings()
    language = settings.get("language") or system_language()
    root = tk.Tk()
    root.withdraw()
    root.title(APP_NAME)
    root.configure(bg=COLORS["bg"])
    root.resizable(False, False)
    icon = resource_path("icon.ico")
    if os.path.isfile(icon):
        try:
            root.iconbitmap(default=icon)
        except tk.TclError:
            pass
    x = (root.winfo_screenwidth() - WIDTH) // 2
    y = max(0, (root.winfo_screenheight() - HEIGHT) // 2 - 30)
    root.geometry("%dx%d+%d+%d" % (WIDTH, HEIGHT, x, y))

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("RZ.Horizontal.TProgressbar", troughcolor=COLORS["input"], background=COLORS["accent"],
                    bordercolor=COLORS["border"], lightcolor=COLORS["accent"], darkcolor=COLORS["accent"],
                    thickness=8)

    events = queue.Queue()
    state = {"job": None, "busy": False, "restart": None}

    def button(parent, text, command, primary=False, width=None):
        bg, hover = (COLORS["accent"], COLORS["accent_hover"]) if primary else (COLORS["border"], "#323845")
        fg = "#ffffff" if primary else COLORS["text"]
        b = tk.Label(parent, text=text, bg=bg, fg=fg, font=FONT_BOLD if primary else FONT,
                     padx=16 if primary else 12, pady=7 if primary else 5, cursor="hand2", width=width)
        b.enabled = True

        def click(_):
            if b.enabled:
                command()

        def set_enabled(on):
            b.enabled = on
            b.configure(bg=bg if on else COLORS["card"], fg=fg if on else COLORS["muted"],
                        cursor="hand2" if on else "arrow")

        b.bind("<Button-1>", click)
        b.bind("<Enter>", lambda _: b.enabled and b.configure(bg=hover))
        b.bind("<Leave>", lambda _: b.configure(bg=bg if b.enabled else COLORS["card"]))
        b.set_enabled = set_enabled
        return b

    def card(parent, title=None):
        outer = tk.Frame(parent, bg=COLORS["card"], highlightthickness=1, highlightbackground=COLORS["border"])
        if title:
            tk.Label(outer, text=title.upper(), bg=COLORS["card"], fg=COLORS["muted"],
                     font=("Segoe UI Semibold", 8)).pack(anchor="w", padx=14, pady=(10, 0))
        inner = tk.Frame(outer, bg=COLORS["card"])
        inner.pack(fill="both", expand=True, padx=14, pady=(6, 12))
        return outer, inner

    def toggle(parent, text, var):
        frame = tk.Frame(parent, bg=COLORS["card"], cursor="hand2")
        dot = tk.Label(frame, bg=COLORS["card"], font=("Segoe UI", 11), cursor="hand2")
        label = tk.Label(frame, text=text, bg=COLORS["card"], font=FONT, cursor="hand2")
        dot.pack(side="left")
        label.pack(side="left", padx=(4, 0))

        def draw():
            on = var.get()
            dot.configure(text="●" if on else "○", fg=COLORS["accent"] if on else COLORS["muted"])
            label.configure(fg=COLORS["text"] if on else COLORS["muted"])

        for widget in (frame, dot, label):
            widget.bind("<Button-1>", lambda _: (var.set(not var.get()), draw()))
        draw()
        return frame

    def segmented(parent, values, var, on_change, bg):
        box = tk.Frame(parent, bg=COLORS["border"])
        labels = {}

        def draw():
            for value, label in labels.items():
                selected = var.get() == value
                label.configure(bg=COLORS["accent"] if selected else bg,
                                fg="#ffffff" if selected else COLORS["muted"])

        def pick(value):
            if var.get() != value and on_change(value) is not False:
                var.set(value)
            draw()

        for i, value in enumerate(values):
            label = tk.Label(box, text=value.upper(), font=FONT_SMALL, padx=10, pady=4, cursor="hand2")
            label.pack(side="left", padx=(0 if i == 0 else 1, 0))
            label.bind("<Button-1>", lambda _, v=value: pick(v))
            labels[value] = label
        draw()
        return box

    footer = tk.Frame(root, bg=COLORS["bg"])
    footer.pack(side="bottom", fill="x", padx=22, pady=(10, 12))

    header = tk.Frame(root, bg=COLORS["bg"])
    header.pack(fill="x", padx=22, pady=(16, 12))
    title_font = tkfont.Font(root=root, family=FONT_TITLE[0], size=FONT_TITLE[1])
    split = title_font.measure("RZ")
    logo = tk.Canvas(header, bg=COLORS["bg"], highlightthickness=0, bd=0,
                     width=title_font.measure(APP_NAME) + 2, height=title_font.metrics("linespace"))
    logo.create_text(0, 0, anchor="nw", text="RZ", fill=COLORS["accent"], font=title_font)
    logo.create_text(split, 0, anchor="nw", text=APP_NAME[2:], fill=COLORS["text"], font=title_font)
    logo.pack(side="left")
    tk.Label(header, text=t("subtitle"), bg=COLORS["bg"], fg=COLORS["muted"],
             font=FONT_SMALL).pack(side="left", padx=(14, 0), pady=(8, 0))

    def change_language(value):
        if state["busy"]:
            messagebox.showinfo(APP_NAME, t("language_busy"))
            return False
        settings["language"] = value
        save_settings(settings)
        state["restart"] = {"links": "" if links.empty else links.get("1.0", "end").strip(),
                            "folder": folder.get()}
        root.after(10, root.destroy)
        return True

    language_var = tk.StringVar(value=language)
    segmented(header, ["tr", "en"], language_var, change_language, COLORS["card"]).pack(side="right", pady=(6, 0))

    body = tk.Frame(root, bg=COLORS["bg"])
    body.pack(fill="both", expand=True, padx=22)

    links_card, links_inner = card(body, t("links"))
    links_card.pack(fill="x")
    placeholder = t("placeholder")
    links = tk.Text(links_inner, height=4, wrap="none", bg=COLORS["input"], fg=COLORS["muted"],
                    insertbackground=COLORS["text"], relief="flat", font=FONT, highlightthickness=1,
                    highlightbackground=COLORS["border"], highlightcolor=COLORS["accent"], padx=10, pady=8,
                    undo=True)
    links.pack(side="left", fill="x", expand=True)
    if restore and restore.get("links"):
        links.insert("1.0", restore["links"])
        links.configure(fg=COLORS["text"])
        links.empty = False
    else:
        links.insert("1.0", placeholder)
        links.empty = True

    def links_focus_in(_):
        if links.empty:
            links.delete("1.0", "end")
            links.configure(fg=COLORS["text"])
            links.empty = False

    def links_focus_out(_):
        if not links.get("1.0", "end").strip():
            links.delete("1.0", "end")
            links.insert("1.0", placeholder)
            links.configure(fg=COLORS["muted"])
            links.empty = True

    links.bind("<FocusIn>", links_focus_in)
    links.bind("<FocusOut>", links_focus_out)

    def paste():
        try:
            text = root.clipboard_get().strip()
        except tk.TclError:
            return
        links_focus_in(None)
        current = links.get("1.0", "end").strip()
        links.insert("end", ("\n" if current else "") + text)

    def clear():
        links.delete("1.0", "end")
        links.empty = False
        links_focus_out(None)

    side = tk.Frame(links_inner, bg=COLORS["card"])
    side.pack(side="left", fill="y", padx=(10, 0))
    button(side, t("paste"), paste, width=9).pack(fill="x")
    button(side, t("clear"), clear, width=9).pack(fill="x", pady=(6, 0))

    opts_card, opts_inner = card(body, t("options"))
    opts_card.pack(fill="x", pady=(12, 0))
    row = tk.Frame(opts_inner, bg=COLORS["card"])
    row.pack(fill="x")
    recent = settings.get("recent_folders") or [default_folder()]
    folder = tk.StringVar(value=(restore or {}).get("folder") or recent[0])
    entry_frame = tk.Frame(row, bg=COLORS["input"], highlightthickness=1, highlightbackground=COLORS["border"])
    entry_frame.pack(side="left", fill="x", expand=True)
    entry = tk.Entry(entry_frame, textvariable=folder, bg=COLORS["input"], fg=COLORS["text"],
                     insertbackground=COLORS["text"], relief="flat", bd=0, font=FONT)
    entry.pack(fill="x", padx=10, ipady=6)
    entry.bind("<FocusIn>", lambda _: entry_frame.configure(highlightbackground=COLORS["accent"]))
    entry.bind("<FocusOut>", lambda _: entry_frame.configure(highlightbackground=COLORS["border"]))

    def recent_menu():
        menu = tk.Menu(root, tearoff=0, bg=COLORS["card"], fg=COLORS["text"], activebackground=COLORS["accent"],
                       activeforeground="#ffffff", relief="flat", bd=0, font=FONT)
        for path in (settings.get("recent_folders") or recent):
            menu.add_command(label=path, command=lambda p=path: folder.set(p))
        menu.tk_popup(recent_btn.winfo_rootx(), recent_btn.winfo_rooty() + recent_btn.winfo_height())

    def browse():
        path = filedialog.askdirectory(initialdir=folder.get() or default_folder())
        if path:
            folder.set(os.path.normpath(path))

    def open_folder():
        path = folder.get().strip()
        if os.path.isdir(path):
            os.startfile(path)

    recent_btn = button(row, "▾", recent_menu)
    recent_btn.pack(side="left", padx=(6, 0))
    button(row, t("browse"), browse).pack(side="left", padx=(6, 0))
    button(row, t("open"), open_folder).pack(side="left", padx=(6, 0))

    options_row = tk.Frame(opts_inner, bg=COLORS["card"])
    options_row.pack(fill="x", pady=(12, 0))
    tk.Label(options_row, text=t("quality"), bg=COLORS["card"], fg=COLORS["muted"],
             font=FONT_SMALL).pack(side="left")
    quality = tk.StringVar(value=settings.get("quality", "320"))
    segmented(options_row, QUALITIES, quality, lambda v: True, COLORS["input"]).pack(side="left", padx=(8, 4))
    tk.Label(options_row, text="kbps", bg=COLORS["card"], fg=COLORS["muted"], font=FONT_SMALL).pack(side="left")

    playlist = tk.BooleanVar(value=settings.get("playlist", True))
    playlist_folder = tk.BooleanVar(value=settings.get("playlist_folder", True))
    skip_existing = tk.BooleanVar(value=settings.get("skip_existing", True))
    toggle(options_row, t("skip_existing"), skip_existing).pack(side="right")
    toggle(options_row, t("playlist_folder"), playlist_folder).pack(side="right", padx=14)
    toggle(options_row, t("playlist"), playlist).pack(side="right")

    run_card, run_inner = card(body)
    run_card.pack(fill="x", pady=(12, 0))
    run_row = tk.Frame(run_inner, bg=COLORS["card"])
    run_row.pack(fill="x")
    download_btn = button(run_row, t("download"), lambda: start(), primary=True, width=10)
    download_btn.pack(side="left")
    stop_btn = button(run_row, t("stop"), lambda: stop(), width=8)
    stop_btn.pack(side="left", padx=(8, 0))
    stop_btn.set_enabled(False)
    status_box = tk.Frame(run_row, bg=COLORS["card"])
    status_box.pack(side="left", fill="x", expand=True, padx=(16, 0))
    status = tk.StringVar(value=t("ready"))
    position = tk.StringVar()
    status_row = tk.Frame(status_box, bg=COLORS["card"])
    status_row.pack(fill="x")
    tk.Label(status_row, textvariable=status, bg=COLORS["card"], fg=COLORS["text"], font=FONT, anchor="w",
             width=1).pack(side="left", fill="x", expand=True)
    tk.Label(status_row, textvariable=position, bg=COLORS["card"], fg=COLORS["muted"],
             font=FONT_SMALL).pack(side="right")
    progress = ttk.Progressbar(status_box, style="RZ.Horizontal.TProgressbar", maximum=100)
    progress.pack(fill="x", pady=(6, 0))

    log_card, log_inner = card(body, t("log"))
    log_card.pack(fill="both", expand=True, pady=(12, 0))
    log = tk.Text(log_inner, bg=COLORS["input"], fg=COLORS["muted"], relief="flat", font=FONT_LOG,
                  state="disabled", highlightthickness=0, padx=10, pady=8, wrap="word", cursor="arrow")
    log.pack(fill="both", expand=True)
    for tag, color in (("info", COLORS["text"]), ("ok", COLORS["green"]), ("warn", COLORS["yellow"]),
                       ("error", COLORS["red"]), ("muted", COLORS["muted"])):
        log.tag_configure(tag, foreground=color)
    prefixes = {"ok": "✓ ", "warn": "! ", "error": "✗ ", "info": "› ", "muted": "  "}

    def write_log(tag, text):
        log.configure(state="normal")
        log.insert("end", prefixes.get(tag, "") + text + "\n", tag)
        log.see("end")
        log.configure(state="disabled")

    credit = tk.Frame(footer, bg=COLORS["bg"])
    credit.pack(side="left")
    tk.Label(credit, text="Developed by ", bg=COLORS["bg"], fg=COLORS["muted"], font=FONT_SMALL).pack(side="left")
    tk.Label(credit, text=AUTHOR, bg=COLORS["bg"], fg=COLORS["accent"],
             font=("Segoe UI Semibold", 9)).pack(side="left")

    discord = tk.Frame(footer, bg=COLORS["bg"], cursor="hand2")
    discord.pack(side="left", padx=(28, 0))
    discord_dot = tk.Label(discord, text="●", bg=COLORS["bg"], fg=COLORS["discord"], font=FONT_SMALL,
                           cursor="hand2")
    discord_text = tk.Label(discord, text=DISCORD, bg=COLORS["bg"], fg=COLORS["muted"], font=FONT_SMALL,
                            cursor="hand2")
    discord_dot.pack(side="left")
    discord_text.pack(side="left", padx=(4, 0))
    for widget in (discord, discord_dot, discord_text):
        widget.bind("<Button-1>", lambda _: webbrowser.open("https://" + DISCORD))
        widget.bind("<Enter>", lambda _: discord_text.configure(fg=COLORS["text"],
                                                                 font=FONT_SMALL + ("underline",)))
        widget.bind("<Leave>", lambda _: discord_text.configure(fg=COLORS["muted"], font=FONT_SMALL))

    about = tk.Label(footer, text="v%s · %s" % (VERSION, LICENSE_NAME), bg=COLORS["bg"], fg=COLORS["muted"],
                     font=FONT_SMALL, cursor="hand2")
    about.pack(side="right")
    about.bind("<Button-1>", lambda _: messagebox.showinfo(
        "%s — %s" % (APP_NAME, t("about_title")), t("about") % (APP_NAME, VERSION, COPYRIGHT, DISCORD)))
    about.bind("<Enter>", lambda _: about.configure(fg=COLORS["text"]))
    about.bind("<Leave>", lambda _: about.configure(fg=COLORS["muted"]))
    tools_bar = tk.Frame(footer, bg=COLORS["bg"])
    tools_bar.pack(side="right", padx=(0, 16))

    def draw_tools():
        for widget in tools_bar.winfo_children():
            widget.destroy()
        for name, ok in (("yt-dlp", has_ytdlp()), ("ffmpeg", bool(find_ffmpeg())), ("deno", bool(find_deno()))):
            tk.Label(tools_bar, text="● ", bg=COLORS["bg"], fg=COLORS["green"] if ok else COLORS["red"],
                     font=FONT_SMALL).pack(side="left")
            tk.Label(tools_bar, text=name + "   ", bg=COLORS["bg"], fg=COLORS["muted"],
                     font=FONT_SMALL).pack(side="left")
        installable = [x for x in missing_tools() if x in TOOLS]
        if installable:
            link = tk.Label(tools_bar, text=t("get_missing"), bg=COLORS["bg"], fg=COLORS["accent"],
                            font=("Segoe UI Semibold", 9, "underline"), cursor="hand2")
            link.bind("<Button-1>", lambda _: install(installable))
            link.pack(side="left")

    def set_busy(on):
        state["busy"] = on
        download_btn.set_enabled(not on)
        stop_btn.set_enabled(on and state["job"] is not None)

    def install(names):
        if state["busy"]:
            return
        items = "\n".join("• %s  (%s)" % (n, TOOLS[n]["url"]) for n in names)
        if not messagebox.askyesno(APP_NAME, t("install_question") % items):
            return
        set_busy(True)

        def worker():
            for n in names:
                try:
                    download_tool(n, lambda kind, data: events.put((kind, data)))
                except Exception as e:
                    events.put(("log", ("error", t("tool_failed") % (n, e))))
            events.put(("install_done", None))

        threading.Thread(target=worker, daemon=True).start()

    def start():
        if state["busy"]:
            return
        urls = [] if links.empty else [x.strip() for x in links.get("1.0", "end").splitlines() if x.strip()]
        if not urls:
            messagebox.showinfo(APP_NAME, t("need_link"))
            return
        target = os.path.normpath(folder.get().strip() or default_folder())
        try:
            os.makedirs(target, exist_ok=True)
        except OSError as e:
            messagebox.showerror(APP_NAME, t("folder_error") % e)
            return
        if not has_ytdlp():
            messagebox.showerror(APP_NAME, t("no_ytdlp"))
            return
        if not find_ffmpeg():
            messagebox.showerror(APP_NAME, t("no_ffmpeg"))
            return
        recent_list = [target] + [p for p in (settings.get("recent_folders") or [])
                                  if os.path.normcase(p) != os.path.normcase(target)]
        settings.update(recent_folders=recent_list[:8], quality=quality.get(), playlist=playlist.get(),
                        playlist_folder=playlist_folder.get(), skip_existing=skip_existing.get())
        save_settings(settings)

        job = Downloader(target, quality.get(), playlist.get(), playlist_folder.get(), skip_existing.get(),
                         emit=lambda kind, data: events.put((kind, data)))
        state["job"] = job
        set_busy(True)
        progress["value"] = 0
        position.set("")
        write_log("info", t("job_start") % (len(urls), target))

        def worker():
            try:
                job.run(urls)
            except Exception as e:
                events.put(("log", ("error", str(e))))
            events.put(("done", job.stats))

        threading.Thread(target=worker, daemon=True).start()

    def stop():
        if state["job"]:
            state["job"].cancelled = True
            status.set(t("stopping"))

    def poll():
        try:
            while True:
                kind, data = events.get_nowait()
                if kind == "log":
                    write_log(*data)
                elif kind == "progress":
                    status.set(data["title"])
                    progress["value"] = data["percent"] or 0
                    position.set("%s / %s" % (data["index"], data["count"] or "?") if data["index"] else "")
                elif kind == "done":
                    status.set(t("finished"))
                    position.set("")
                    write_log("info", summary(data))
                    state["job"] = None
                    set_busy(False)
                elif kind == "install_done":
                    status.set(t("ready"))
                    progress["value"] = 0
                    set_busy(False)
                    draw_tools()
        except queue.Empty:
            pass
        root.after(100, poll)

    def on_close():
        if state["busy"] and not messagebox.askyesno(APP_NAME, t("quit_question")):
            return
        stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    draw_tools()
    missing = missing_tools()
    if missing:
        write_log("warn", t("missing") % ", ".join(missing) + ("" if has_ytdlp() else t("ytdlp_hint")))
    else:
        write_log("muted", t("ready_log"))
    root.after(100, poll)
    root.update_idletasks()
    dark_title_bar(root)
    root.deiconify()
    root.mainloop()
    return state["restart"]


def gui():
    set_app_id()
    restore = None
    while True:
        restore = run_window(restore)
        if restore is None:
            break


def main():
    global language
    language = load_settings().get("language") or system_language()
    parser = argparse.ArgumentParser(prog=APP_ID, description=t("cli_description") % (APP_NAME, AUTHOR))
    parser.add_argument("links", nargs="*", help=t("help_links"))
    parser.add_argument("-o", "--klasor", "--folder", dest="folder", help=t("help_folder"))
    parser.add_argument("-k", "--kalite", "--quality", dest="quality", default="320", choices=QUALITIES,
                        help=t("help_quality"))
    parser.add_argument("--tekli", "--single", dest="single", action="store_true", help=t("help_single"))
    parser.add_argument("--tekrar", "--redownload", dest="redownload", action="store_true",
                        help=t("help_redownload"))
    parser.add_argument("--kur", "--install", dest="install", action="store_true", help=t("help_install"))
    parser.add_argument("--version", action="version",
                        version="%s %s — %s — %s" % (APP_NAME, VERSION, COPYRIGHT, LICENSE_NAME))
    args = parser.parse_args()
    if args.install:
        sys.exit(cli_install())
    if args.links:
        sys.exit(cli(args))
    gui()


if __name__ == "__main__":
    main()
