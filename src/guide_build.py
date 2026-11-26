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
        ("bars", "Cocktail bars", "cocktail bars"), ("dive", "Dive bars", "dive bars"), ("wine", "Wine bars", "wine bars"),
        ("beer", "Beer & breweries", "beer bars and breweries"), ("rooftop", "Rooftops & views", "rooftop bars"),
        ("sports", "Sports bars", "sports bars"), ("latenight", "Late night", "late-night spots")]),
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
