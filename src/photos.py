# Verified free Unsplash photos (images.unsplash.com, Unsplash License), checked by eye for each neighborhood.
# First photo is the cover. Each entry: (photo id, alt text)
PHOTOS = {
    "venice": [
        ("1552410101-651780c9e7d1", "The Venice sign over Windward Avenue at sunset"),
        ("1541233353-4f6e16ba14b2", "White footbridge over the Venice Canals"),
        ("1725312198242-5fab9901c754", "Palm trees along the Venice boardwalk"),
        ("1548816432-9befc5837f58", "Venice Canals at sunset"),
        ("1573397286878-0ff40aa140cd", "Skateboarder under the Venice sign"),
        ("1709226750087-6860fd6cca35", "Homes along the Venice Canals"),
        ("1518824547657-2bb07e2978ba", "Lifeguard tower on Venice Beach"),
        ("1599565508269-8603edf976b8", "Boats on a Venice canal"),
    ],
    "santa-monica": [
        ("1505887579242-c7bc04062e98", "Santa Monica Pier and the Pacific Park Ferris wheel"),
        ("1498196645145-687fd3bfe912", "Santa Monica Pier at dusk"),
        ("1565096940315-d3831bee0fb1", "Route 66 End of the Trail sign in Santa Monica"),
        ("1553201826-f338050bb02c", "The Santa Monica Pier entrance sign"),
        ("1523898770179-576b66f2c767", "Santa Monica beach on a summer day"),
        ("1661037177531-646f11829db6", "Santa Monica along the coast"),
    ],
    "malibu": [
        ("1783039212129-93d7b94aeda2", "Malibu Pier at sunset"),
        ("1596293108908-e1b87a55ee8f", "Beach homes on the Malibu coast"),
        ("1613945798133-e6b30c41a214", "Malibu cliffs and surf"),
        ("1499898595565-f424ed1d075c", "Malibu coastline and mountains"),
        ("1615571022219-eb45cf7faa9d", "Beach house over the sand in Malibu"),
        ("1635120392561-99eb64627cc5", "Malibu beach at golden hour"),
    ],
    "beverly-hills": [
        ("1626060446672-5128ec04f992", "The Beverly Hills sign in Beverly Gardens Park"),
        ("1600617548803-360421b4d39e", "Two Rodeo Drive in Beverly Hills"),
        ("1681181878800-8abf6328344e", "The Beverly Hills Hotel on Sunset Boulevard"),
        ("1600617547577-a486ad1c123d", "Rodeo Drive storefronts"),
        ("1591622594455-0f53d9d5a418", "Palm-lined street in Beverly Hills"),
    ],
    "hollywood-hills": [
        ("1594663805807-29a7cc1847c0", "The Hollywood sign at sunset"),
        ("1589053739346-ed32227546a4", "The Hollywood sign on Mount Lee"),
        ("1700228711940-c40eda77c79e", "The Hollywood Hills under a blue sky"),
        ("1563568996556-9a858f648704", "Lake Hollywood Reservoir below the Hollywood sign"),
    ],
    "silver-lake": [
        ("1742397391825-fc342c6b2bc1", "Silver Lake Reservoir with the hills behind"),
        ("1573241817627-51baa196a50d", "Welcome to Silverlake Sunset Junction sign"),
        ("/img/edgecliffe.jpg", "1436 Edgecliffe Dr in Silver Lake, Nathaniel's lease listing"),
    ],
    "los-feliz": [
        ("1572975165658-8fba2f1b0b37", "Griffith Observatory above Los Feliz"),
        ("1566864717473-2f0daf8979e5", "Griffith Observatory and the city view"),
        ("1622041173895-cb3665044a52", "Griffith Observatory at dusk"),
        ("1770174078818-b26791048fa5", "Griffith Observatory domes"),
        ("1546624356-62f238e38e2a", "Griffith Observatory entrance at night"),
    ],
    "fairfax": [
        ("1771294225103-6320f1b36231", "The Grove sign on Fairfax"),
        ("/img/fuller.jpg", "616 N Fuller Ave in the Fairfax District, sold by Nathaniel Grivas"),
    ],
    "echo-park": [
        ("1581876842641-2a25722f9fd9", "Echo Park Lake fountain with the downtown skyline"),
    ],
    "marina-del-rey": [
        ("1763826144409-ff14ea6d9e32", "Marina del Rey harbor walkway at sunset"),
        ("1612883011498-a3fd1aab1906", "Sailboats docked in Marina del Rey"),
        ("1696602294629-40d80060fda6", "Sailboat in the Marina del Rey harbor"),
        ("1763826351256-e15978b27207", "Marina del Rey docks at dusk"),
    ],
    "westwood": [
        ("1728970645747-7eb62c8f3ee6", "Royce Hall at UCLA in Westwood"),
        ("1661064695236-3719e1cd618f", "Powell Library at UCLA"),
        ("1729536233990-5dd65ab81e42", "UCLA campus lawn and Royce Hall"),
    ],
    "pacific-palisades": [
        ("1694392787176-2ee339f13644", "Pacific Palisades view over Santa Monica Bay"),
        ("1633908904924-da7254e56e1f", "The Getty Villa garden in Pacific Palisades"),
        ("1677382424723-9774eba31eca", "Pacific Palisades hillside above the ocean"),
    ],
    "brentwood": [
        ("1689096773595-e3aabac7c85d", "The Getty Center gardens above Brentwood"),
        ("1582346992845-c963d5b0ba0d", "The Getty Center plaza and stairs"),
        ("1571614295598-bc37756059c2", "Getty Center pavilion in Brentwood"),
        ("1689096725913-e519fab619c6", "The Getty Center Central Garden"),
    ],
    "miracle-mile": [
        ("1561902636-0e918139734e", "Urban Light at LACMA on the Miracle Mile"),
        ("1771294224838-463af3e2ab60", "The Urban Light lampposts at LACMA"),
        ("1737079282221-414735867109", "Urban Light at night on Wilshire Boulevard"),
        ("1672856491397-643f742c8111", "The Academy Museum dome on Wilshire and Fairfax"),
    ],
    "hollywood": [
        ("1613051744581-d87fbe8c9671", "Hollywood Boulevard with a classic car"),
        ("1621534893855-d0497f173d3f", "Hollywood Boulevard street scene"),
        ("1621534893852-355409fccaee", "The plaza at Hollywood and Highland"),
        ("1697025251689-bc5ba42f1f2e", "Palm trees and billboards on Hollywood Boulevard"),
    ],
    "century-city": [
        ("1616397733544-839114f977a7", "Century City towers above Avenue of the Stars"),
        ("1693716959993-7e5709ad429b", "Century City high-rises at sunset"),
        ("1693720117760-7c41b919f3db", "Century City from above"),
    ],
    "palms": [
        ("1733607946569-6348e7c9a53c", "The Helms Bakery sign on Venice Boulevard"),
        ("1733608242458-695cfd86e486", "Helms Bakery neon sign"),
        ("1733607946566-ae4b35bf5d61", "The Helms Bakery building"),
    ],
    "sherman-oaks": [
        ("1588279294107-98f6f0e43b19", "Casa Vega on Ventura Boulevard in Sherman Oaks"),
        ("1724280984019-81fe8e9d6794", "Sherman Oaks and the Valley from the hills"),
    ],
    "playa-del-rey": [
        ("1744888839687-87e82a4f8ed1", "Dockweiler Beach dunes in Playa del Rey"),
        ("1740478517901-589bf9ac4bf9", "The Playa del Rey jetty at sunset"),
        ("1761010785765-7c9ccb8a44b7", "Vista del Mar above Dockweiler Beach"),
    ],
    "pico-robertson": [
        ("/img/glenville.jpg", "1127 Glenville Dr in Pico-Robertson, a lease Nathaniel closed"),
    ],
    "reseda": [
        ("/img/lanark.jpg", "18748 Lanark St in Reseda, sold by Nathaniel Grivas"),
    ],
    "van-nuys": [
        ("/img/hartland.jpg", "14757 Hartland St in Van Nuys, bought by Nathaniel Grivas's client"),
    ],
    "encino": [
        ("/img/zelzah.jpg", "5142 Zelzah Ave #26 in Encino, Nathaniel's listing"),
    ],
}


def url(pid, w=1200, h=None, q=72):
    if pid.startswith("/"):
        return pid
    crop = f"&h={h}&fit=crop" if h else ""
    return f"https://images.unsplash.com/photo-{pid}?w={w}{crop}&q={q}&auto=format"


def srcset(pid, h_ratio=None, widths=(480, 800, 1200, 1800)):
    if pid.startswith("/"):
        return ""
    out = []
    for w in widths:
        h = int(w * h_ratio) if h_ratio else None
        out.append(f"{url(pid, w, h)} {w}w")
    return ", ".join(out)


def cover(slug):
    p = PHOTOS.get(slug)
    return p[0] if p else None
