import os, sys, glob, sqlite3, pathlib, configparser
from urllib.parse import urlparse

def find_firefox_places() -> str:
    home = pathlib.Path.home()
    if sys.platform.startswith("win"):
        base = home / "AppData" / "Roaming" / "Mozilla" / "Firefox"
    elif sys.platform == "darwin":
        base = home / "Library" / "Application Support" / "Firefox"
    else:
        base = home / ".mozilla" / "firefox"

    ini = base / "profiles.ini"
    if ini.exists():
        cfg = configparser.ConfigParser()
        cfg.read(ini, encoding="utf-8")
        chosen, rel = None, True
        for s in cfg.sections():
            if cfg.has_option(s, "Default") and cfg.get(s, "Default") == "1":
                chosen = cfg.get(s, "Path"); rel = cfg.getboolean(s, "IsRelative", fallback=True); break
        if not chosen:
            for s in cfg.sections():
                if cfg.has_option(s, "Path"):
                    chosen = cfg.get(s, "Path"); rel = cfg.getboolean(s, "IsRelative", fallback=True); break
        if chosen:
            prof = (base / chosen) if rel else pathlib.Path(chosen)
            p = prof / "places.sqlite"
            if p.exists():
                return str(p)

    # fallback: glob
    for c in glob.glob(str(base / "Profiles" / "*.default*/places.sqlite")) + glob.glob(str(base / "*.default*/places.sqlite")):
        if os.path.exists(c):
            return c
    raise FileNotFoundError("places.sqlite not found. Start Firefox once, then try again.")

def open_readonly(db_path: str):
    return sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)

def is_tureng(url: str) -> bool:
    try:
        return "tureng.com" in urlparse(url).netloc.lower()
    except Exception:
        return False

def get_tagged_tureng(tag_like: str = "anki"):
    """Return [{'url','bookmark_title','tag'}, ...] for bookmarks with tag LIKE %tag_like% and domain tureng.com."""
    db_path = find_firefox_places()
    with open_readonly(db_path) as con:
        q = """
        SELECT p.url, COALESCE(b.title,'') AS bookmark_title, t.title AS tag
        FROM moz_bookmarks b
        JOIN moz_bookmarks t ON b.parent = t.id
        JOIN moz_places p ON b.fk = p.id
        WHERE LOWER(t.title) LIKE '%' || LOWER(?) || '%';
        """
        rows = con.execute(q, (tag_like,)).fetchall()
    tagged = [{"url": r[0], "bookmark_title": r[1], "tag": r[2]} for r in rows if r[0]]
    return [r for r in tagged if is_tureng(r["url"])]