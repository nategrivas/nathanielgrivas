"""List deploy/ files that differ from what is live on main, grouped by upload folder.
Skips binary media (img/, video, fonts). Run after build.py."""
import pathlib, subprocess, sys, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "deploy"
RAW = "https://raw.githubusercontent.com/nategrivas/nathanielgrivas/main/"
SKIP_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".mov", ".woff", ".woff2", ".ico"}

def live(rel):
    r = subprocess.run(["curl", "-fsSL", RAW + rel], capture_output=True)
    return r.stdout if r.returncode == 0 else None

groups = collections.defaultdict(list)
for f in sorted(OUT.rglob("*")):
    if not f.is_file():
        continue
    rel = f.relative_to(OUT).as_posix()
    if rel.startswith("img/") or f.suffix.lower() in SKIP_EXT or f.name.startswith("."):
        continue
    if rel == "links.html" and not (ROOT / "links" / "index.html").exists():
        continue
    if rel.startswith("assets/") and not (ROOT / "assets").exists() and rel != "assets/search.json":
        continue
    if live(rel) != f.read_bytes():
        groups[str(pathlib.PurePosixPath(rel).parent)].append(str(f))

if not groups:
    print("nothing changed"); sys.exit()
for folder, files in groups.items():
    url = "https://github.com/nategrivas/nathanielgrivas/upload/main" + ("" if folder == "." else "/" + folder)
    print(f"\n{url}  ({len(files)} files)")
    for x in files:
        print("  " + x)
