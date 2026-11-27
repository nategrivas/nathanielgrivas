"""The LA Guide: neighborhood guides and citywide best-of pages, built from src/guide/*.json."""
import json, pathlib
from urllib.parse import quote_plus

GDIR = pathlib.Path(__file__).parent / "guide"

GROUPS = [
    ("eat", "Eat", [
        ("coffee", "Coffee", "coffee shops"), ("breakfast", "Breakfast", "breakfast"), ("brunch", "Brunch", "brunch"),
        ("lunch", "Lunch", "lunch"), ("dinner", "Dinner", "dinner"), ("date", "Date night", "date night restaurants"),
        ("pizza", "Pizza", "pizza"), ("tacos", "Tacos & Mexican", "tacos and Mexican food"), ("seafood", "Seafood", "seafood"),
        ("sushi", "Sushi & Japanese", "sushi and Japanese food"), ("bakery", "Bakeries & dessert", "bakeries and dessert"),
        ("healthy", "Healthy & plant-based", "healthy and plant-based food"), ("cheap", "Cheap eats", "cheap eats")]),
    ("drink", "Drink", [
        ("bars", "Cocktail bars & lounges", "cocktail bars and lounges"), ("wine", "Wine bars", "wine bars"),
        ("rooftop", "Rooftops & views", "rooftop bars"), ("latenight", "Late night", "late-night spots")]),
    ("do", "Do", [
        ("music", "Live music", "live music"), ("comedy", "Comedy & theater", "comedy and theater"), ("film", "Movies", "movie theaters"),
        ("museum", "Museums", "museums"), ("art", "Art & galleries", "art and galleries"), ("landmark", "Landmarks & sights", "landmarks"),
        ("park", "Parks", "parks"), ("hike", "Hikes & nature", "hikes"), ("beach", "Beaches", "beaches"),
        ("shop", "Shopping", "shopping"), ("market", "Markets", "markets and farmers markets"), ("fitness", "Fitness & outdoor sports", "fitness and outdoor sports"),
        ("golf", "Golf", "golf"), ("kids", "Kids & family", "family outings"), ("dogs", "Dog-friendly", "dog-friendly spots"),
        ("spa", "Spas & wellness", "spas and wellness")]),
]
CATS = {k: (label, plural, g) for g, _, items in GROUPS for k, label, plural in items}
ORDERED = [k for _, _, items in GROUPS for k, _, _ in items]


def load():
    out = {}
    for f in sorted(GDIR.glob("*.json")):
        d = json.loads(f.read_text())
        for p in d["places"]:
            p["c"] = [c for c in p["c"] if c in CATS] or ["landmark"]
        out[d["slug"]] = d
    return out


def maps_url(p, hood_name):
    q = p["n"] + " " + (p.get("a") or "") + " " + hood_name + " Los Angeles CA"
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(q)


# Neighborhood pages group places into a few broad sections, so every section shown has at least 3 picks.
SECTIONS = [
    ("morning", "Coffee & breakfast", "eat", {"coffee", "breakfast", "brunch", "bakery"}),
    ("casual", "Lunch & casual", "eat", {"lunch", "cheap", "healthy", "pizza", "tacos"}),
    ("dinner", "Dinner", "eat", {"dinner", "date", "seafood", "sushi"}),
    ("night", "Nightlife", "drink", {"bars", "wine", "rooftop", "latenight"}),
    ("culture", "Culture & shows", "do", {"museum", "art", "landmark", "music", "comedy", "film"}),
    ("outdoors", "Parks & outdoors", "do", {"park", "hike", "beach", "golf", "fitness", "dogs"}),
    ("shop", "Shops, markets & spas", "do", {"shop", "market", "spa", "kids"}),
]
SEC = {k: (label, g) for k, label, g, _ in SECTIONS}
SEC_ORDER = [k for k, *_ in SECTIONS]
SEC_OF = {c: k for k, _, _, cs in SECTIONS for c in cs}
MERGE_TO = {"morning": "casual", "casual": "dinner", "dinner": "casual", "night": "dinner",
            "culture": "outdoors", "outdoors": "culture", "shop": "culture"}
COMBOS = {
    frozenset({"morning", "casual"}): "Breakfast & lunch",
    frozenset({"casual", "dinner"}): "Restaurants",
    frozenset({"morning", "dinner"}): "Restaurants & cafes",
    frozenset({"morning", "casual", "dinner"}): "Restaurants & cafes",
    frozenset({"dinner", "night"}): "Dinner & drinks",
    frozenset({"culture", "outdoors"}): "Things to do",
    frozenset({"culture", "shop"}): "Things to do",
    frozenset({"outdoors", "shop"}): "Things to do",
    frozenset({"culture", "outdoors", "shop"}): "Things to do",
}


def sec_of(p):
    return SEC_OF.get(p["c"][0], "culture")


def combo_label(keys):
    keys = frozenset(keys)
    if len(keys) == 1:
        return SEC[next(iter(keys))][0]
    if keys in COMBOS:
        return COMBOS[keys]
    if keys <= {"culture", "outdoors", "shop"}:
        return "Things to do"
    if "night" in keys and keys & {"culture", "outdoors", "shop"}:
        return "Places to go"
    if "night" in keys:
        return "Eat & drink"
    return "Restaurants & cafes"


def combo_group(keys):
    gs = {SEC[k][1] for k in keys}
    if gs == {"eat"}:
        return "Eat"
    if gs == {"drink"}:
        return "Drink"
    if gs == {"do"}:
        return "Do"
    if gs <= {"eat", "drink"}:
        return "Eat & drink"
    return "Go"
