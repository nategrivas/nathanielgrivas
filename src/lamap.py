"""Hand-drawn vector map of Los Angeles for the site. No tiles, no API keys.

Shapes are simplified from known coordinates: good for orientation, not for surveying.
"""
import math

LNG0, LNG1 = -118.84, -118.22
LAT0, LAT1 = 33.925, 34.235
W = 1000.0
HH = round(W * (LAT1 - LAT0) / ((LNG1 - LNG0) * math.cos(math.radians(34.08))), 1)


def proj(lat, lng):
    x = (lng - LNG0) / (LNG1 - LNG0) * W
    y = (LAT1 - lat) / (LAT1 - LAT0) * HH
    return round(x, 1), round(y, 1)


def smooth(points, close=False, t=0.5):
    """Catmull-Rom through the points, written as cubic Beziers, so hand-placed coastlines read as drawn."""
    P = [proj(lat, lng) for lng, lat in points]
    if close:
        P = P + P[:2]
        ext = [P[-3]] + P
    else:
        ext = [P[0]] + P + [P[-1]]
    d = f"M{ext[1][0]},{ext[1][1]}"
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]},{p2[1]}"
    return d + (" Z" if close else "")


def path(points, close=False):
    pts = [proj(lat, lng) for lng, lat in points]
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    return d + (" Z" if close else "")


COAST = [(-119.02, 34.052), (-118.96, 34.046), (-118.90, 34.040), (-118.84, 34.030), (-118.82, 34.017), (-118.806, 34.001), (-118.79, 34.012), (-118.76, 34.022),
         (-118.72, 34.030), (-118.69, 34.034), (-118.677, 34.036), (-118.65, 34.037), (-118.62, 34.037),
         (-118.583, 34.039), (-118.56, 34.040), (-118.535, 34.034), (-118.52, 34.024), (-118.498, 34.009),
         (-118.486, 33.995), (-118.469, 33.977), (-118.458, 33.963), (-118.447, 33.950), (-118.437, 33.930),
         (-118.433, 33.925)]
OCEAN = COAST + [(-118.84, 33.925)]
MOUNTAINS = ([(-119.02, 34.14), (-118.84, 34.135), (-118.75, 34.135), (-118.68, 34.14), (-118.63, 34.152), (-118.60, 34.155),
              (-118.56, 34.155), (-118.52, 34.150), (-118.48, 34.146), (-118.45, 34.144), (-118.42, 34.139),
              (-118.39, 34.134), (-118.36, 34.130), (-118.33, 34.128), (-118.30, 34.143), (-118.28, 34.148),
              (-118.262, 34.130), (-118.28, 34.113), (-118.30, 34.108), (-118.33, 34.104), (-118.36, 34.099),
              (-118.39, 34.091), (-118.42, 34.085), (-118.45, 34.079), (-118.48, 34.071), (-118.50, 34.061),
              (-118.52, 34.046)] + [p for p in reversed(COAST[:17])])
FWY = {
    "405": [(-118.392, 33.925), (-118.395, 33.96), (-118.405, 33.985), (-118.42, 34.005), (-118.433, 34.025),
            (-118.445, 34.05), (-118.452, 34.07), (-118.468, 34.09), (-118.478, 34.11), (-118.475, 34.13),
            (-118.468, 34.155), (-118.468, 34.19), (-118.47, 34.235)],
    "10": [(-118.493, 34.016), (-118.46, 34.022), (-118.433, 34.025), (-118.40, 34.031), (-118.37, 34.034),
           (-118.34, 34.037), (-118.31, 34.036), (-118.28, 34.03), (-118.25, 34.028), (-118.22, 34.03)],
    "101": [(-118.84, 34.150), (-118.75, 34.145), (-118.66, 34.155), (-118.61, 34.170), (-118.55, 34.166),
            (-118.50, 34.163), (-118.468, 34.157), (-118.43, 34.155), (-118.40, 34.152), (-118.38, 34.142),
            (-118.36, 34.135), (-118.345, 34.12), (-118.335, 34.10), (-118.31, 34.093), (-118.285, 34.083),
            (-118.265, 34.07), (-118.245, 34.06), (-118.22, 34.055)],
}
BLVD = {
    "Sunset Blvd": [(-118.556, 34.040), (-118.52, 34.047), (-118.49, 34.062), (-118.47, 34.072), (-118.445, 34.073),
                    (-118.42, 34.079), (-118.40, 34.081), (-118.385, 34.09), (-118.37, 34.096), (-118.33, 34.098),
                    (-118.30, 34.098), (-118.28, 34.092), (-118.265, 34.08), (-118.245, 34.062)],
    "Wilshire Blvd": [(-118.497, 34.018), (-118.47, 34.040), (-118.445, 34.058), (-118.42, 34.064), (-118.40, 34.066),
                      (-118.37, 34.064), (-118.34, 34.062), (-118.30, 34.0617), (-118.27, 34.057), (-118.25, 34.050)],
    "Ventura Blvd": [(-118.64, 34.171), (-118.58, 34.170), (-118.55, 34.168), (-118.50, 34.161), (-118.45, 34.152),
                     (-118.40, 34.146), (-118.37, 34.142)],
}
BLVD_LABEL = {"Sunset Blvd": (34.0835, -118.392, -16), "Wilshire Blvd": (34.0665, -118.425, -12), "Ventura Blvd": (34.1715, -118.585, -1)}
FWY_LABEL = {"405": (34.118, -118.476), "10": (34.036, -118.355), "101": (34.170, -118.585)}
PLACES = [("Pacific Ocean", 33.965, -118.66, "sea"), ("Santa Monica Mountains", 34.098, -118.64, "mtn"),
          ("San Fernando Valley", 34.215, -118.52, "area"), ("Downtown", 34.0522, -118.2437, "pin"),
          ("LAX", 33.9425, -118.4081, "pin")]


def base_symbol():
    """The shared base map, defined once per page and reused with <use href="#la">."""
    fw = "".join(f'<path d="{smooth(p)}" fill="none" stroke="#f4f1ec" stroke-opacity=".09" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>' for p in FWY.values())
    bl = "".join(f'<path d="{smooth(p)}" fill="none" stroke="#d9a882" stroke-opacity=".09" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"/>' for p in BLVD.values())
    return (f'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
            f'<pattern id="waves" width="14" height="14" patternUnits="userSpaceOnUse"><path d="M0 7 q3.5 -3 7 0 t7 0" fill="none" stroke="rgba(127,209,199,.07)" stroke-width="1"/></pattern><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="rgba(255,255,255,.035)" stroke-width=".6"/></pattern>'
            f'<symbol id="la" viewBox="0 0 {W:g} {HH:g}">'
            f'<rect x="-320" width="{W + 640:g}" height="{HH:g}" fill="#121110"/><rect x="-320" width="{W + 640:g}" height="{HH:g}" fill="url(#grid)"/>'
            f'<path d="{smooth(COAST)} L{proj(33.925, -119.02)[0]},{proj(33.925, -119.02)[1]} Z" fill="#0c1517"/><path d="{smooth(COAST)} L{proj(33.925, -119.02)[0]},{proj(33.925, -119.02)[1]} Z" fill="url(#waves)"/>'
            f'<path d="{smooth(MOUNTAINS, True)}" fill="#d9a882" fill-opacity=".06"/>'
            f'<path d="{smooth(COAST)}" fill="none" stroke="#7fd1c7" stroke-opacity=".5" stroke-width="1.3" stroke-linejoin="round"/>{bl}{fw}'
            f'</symbol></defs></svg>')


def labels(scale=1.0):
    out = []
    for name, lat, lng, kind in PLACES:
        x, y = proj(lat, lng)
        if kind == "pin":
            left = lng > -118.3
            tx = x - 6 * scale if left else x + 6 * scale
            out.append(f'<g class="pl pin"><circle cx="{x}" cy="{y}" r="{2.6*scale:.1f}"/><text x="{tx:.1f}" y="{y + 3.5*scale:.1f}" font-size="{10*scale:.1f}"{' text-anchor="end"' if left else ''}>{name}</text></g>')
        else:
            out.append(f'<text class="pl {kind}" x="{x}" y="{y}" font-size="{(15 if kind != "area" else 14)*scale:.1f}" text-anchor="middle">{name}</text>')
    for k, (lat, lng, rot) in BLVD_LABEL.items():
        x, y = proj(lat, lng)
        out.append(f'<text class="pl blvd" x="{x}" y="{y}" font-size="{8.5*scale:.1f}" text-anchor="middle" transform="rotate({rot} {x} {y})">{k}</text>')
    for k, (lat, lng) in FWY_LABEL.items():
        x, y = proj(lat, lng)
        out.append(f'<g class="shield"><rect x="{x - 11*scale:.1f}" y="{y - 7*scale:.1f}" width="{22*scale:.1f}" height="{14*scale:.1f}" rx="{4*scale:.1f}"/><text x="{x}" y="{y + 3.6*scale:.1f}" font-size="{9.5*scale:.1f}" text-anchor="middle">{k}</text></g>')
    return "".join(out)


def view_around(lat, lng, width=240.0, aspect=0.5, fx=0.5):
    cx, cy = proj(lat, lng)
    w = width
    h = width * aspect
    x = min(max(cx - w * fx, -w * 0.35), W - w * 0.65)
    y = min(max(cy - h / 2, 0), HH - h)
    return x, y, w, h
