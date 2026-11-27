"""Pockets: the sub-neighborhoods inside each Local LA area, drawn from street geometry.

polys.txt holds one pocket per line: id|name|encoded polygon (Google polyline, 5 decimals).
meta.json holds the words: {id: {"d": description, "b": boundaries in words}}, in display order.
Boundaries are our own research. No prices are published here.
"""
import json
import os

HERE = os.path.join(os.path.dirname(__file__), "pockets")
AREA = {
    "sm": "santa-monica", "brw": "brentwood", "pal": "pacific-palisades", "bh": "beverly-hills", "bhpo": "bhpo",
    "bel": "bel-air", "hh": "hollywood-hills", "hp": "hancock-park", "ven": "venice", "mdr": "marina-del-rey",
    "pv": "playa-vista", "pdr": "playa-del-rey", "mal": "malibu", "mv": "mar-vista", "palms": "palms",
    "cc": "culver-city", "wch": "westchester", "wla": "west-la", "ww": "westwood", "cen": "century-city",
    "chv": "cheviot-hills", "pr": "pico-robertson", "weho": "west-hollywood", "bg": "beverly-grove",
    "fx": "fairfax", "mm": "miracle-mile", "hw": "hollywood", "lf": "los-feliz", "sl": "silver-lake",
    "ep": "echo-park", "eh": "east-hollywood", "sc": "studio-city", "so": "sherman-oaks", "enc": "encino",
    "tz": "tarzana", "wh": "woodland-hills", "vv": "valley-village", "noho": "north-hollywood", "vn": "van-nuys",
    "res": "reseda",
}


def load():
    meta_path = os.path.join(HERE, "meta.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    order = {k: i for i, k in enumerate(meta)}
    out = {}
    path = os.path.join(HERE, "polys.txt")
    if not os.path.exists(path):
        return out
    for line in open(path):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        pid, name, enc = line.split("|", 2)
        m = meta.get(pid, {})
        if m.get("skip"):
            continue
        area = m.get("area") or AREA.get(pid.split("-")[0])
        if not area:
            continue
        out.setdefault(area, []).append(dict(i=pid, n=m.get("name", name), e=enc, d=m.get("d", ""), b=m.get("b", ""), a=area,
                                             o=order.get(pid, 9999)))
    for area in out:
        out[area].sort(key=lambda p: (p["o"], p["n"]))
    return out
