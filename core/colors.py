import json
import re
from pathlib import Path
from typing import List, Tuple
from core.utils import resource_path

# --- Easter Eggs & Creator Colors ---
CREATOR_COLORS = {
    "Matt Joy Slate": "#708090",
    "Nox Black": "#000001",
    "It Could Be Teal": "#17CDBE",
    "Hal Jam Blue": "#0072E5",
    "Fatbird Pink": "#FF9AEB",
    "diveBar Pink": "#F42C95",
    "diveBar Blue": "#01A7DC",
    "Pear Green": "#DBE273",
    "Junction Blue": "#023358",
    "Cloud Eleven Blue": "#005A9E",
    "Cloak Gray": "#B6B6B6",
    "Untanned Aghastronaut": "#FFF5E5",
    "Rank Amateur Feelgood Purpureus": "#9500b3",
    "The Most Evocative Shade of Deepest Indigo": "#120033",
    # --- Creator & Brand Colors ---
    "Spotify Green": "#1DB954",
    "Twitch Purple": "#9146FF",
    "Discord Blurple": "#5865F2",
    "TikTok Pink": "#FE2C55",
    "TikTok Cyan": "#25F4EE",
    "Patreon Coral": "#FF424D",
    "Twitter Blue": "#1DA1F2",
    "YouTube Red": "#FF0000",
    "Netflix Red": "#E50914",
    "T-Mobile Magenta": "#E20074",
    "UPS Pullman Brown": "#351C15",
    "Tiffany Blue": "#0ABAB5",
    "Post-it Canary Yellow": "#FDF200",
    "Ferrari Red": "#FF2800",
    "Wimbledon Purple": "#330066",
    "Wimbledon Green": "#006633",
    "Golden Gate Bridge Orange": "#C0362D",
    "Facebook Blue": "#1877F2",
    "Intel Blue": "#0071C5",
    "Disney Blue": "#003087",
    "Reese's Orange": "#FF8200",
    "Starbucks Green": "#00704A",
    "Cadbury Purple": "#47243C",
    "Pantone 448 C (Ugliest Color)": "#4A412A",
    "Barbie Pink": "#E0218A",
    "Hermès Orange": "#F37021",
    "John Deere Green": "#367C2B",
    "Coca-Cola Red": "#F40009",
    "Binghamton University Deep Green": "#005A43",
    # --- The Standard 140 CSS Colors ---
    "Alice Blue": "#F0F8FF",
    "Antique White": "#FAEBD7",
    "Aqua": "#00FFFF",
    "Aquamarine": "#7FFFD4",
    "Azure": "#F0FFFF",
    "Beige": "#F5F5DC",
    "Bisque": "#FFE4C4",
    "Black": "#000000",
    "Blanched Almond": "#FFEBCD",
    "Blue": "#0000FF",
    "Blue Violet": "#8A2BE2",
    "Brown": "#A52A2A",
    "Burly Wood": "#DEB887",
    "Cadet Blue": "#5F9EA0",
    "Chartreuse": "#7FFF00",
    "Chocolate": "#D2691E",
    "Coral": "#FF7F50",
    "Cornflower Blue": "#6495ED",
    "Cornsilk": "#FFF8DC",
    "Crimson": "#DC143C",
    "Cyan": "#00FFFF",
    "Dark Blue": "#00008B",
    "Dark Cyan": "#008B8B",
    "Dark Goldenrod": "#B8860B",
    "Dark Gray": "#A9A9A9",
    "Dark Green": "#006400",
    "Dark Khaki": "#BDB76B",
    "Dark Magenta": "#8B008B",
    "Dark Olive Green": "#556B2F",
    "Dark Orange": "#FF8C00",
    "Dark Orchid": "#9932CC",
    "Dark Red": "#8B0000",
    "Dark Salmon": "#E9967A",
    "Dark Sea Green": "#8FBC8F",
    "Dark Slate Blue": "#483D8B",
    "Dark Slate Gray": "#2F4F4F",
    "Dark Turquoise": "#00CED1",
    "Dark Violet": "#9400D3",
    "Deep Pink": "#FF1493",
    "Deep Sky Blue": "#00BFFF",
    "Dim Gray": "#696969",
    "Dodger Blue": "#1E90FF",
    "Firebrick": "#B22222",
    "Floral White": "#FFFAF0",
    "Forest Green": "#228B22",
    "Fuchsia": "#FF00FF",
    "Gainsboro": "#DCDCDC",
    "Ghost White": "#F8F8FF",
    "Gold": "#FFD700",
    "Goldenrod": "#DAA520",
    "Gray": "#808080",
    "Green": "#008000",
    "Green Yellow": "#ADFF2F",
    "Honeydew": "#F0FFF0",
    "Hot Pink": "#FF69B4",
    "Indian Red": "#CD5C5C",
    "Indigo": "#4B0082",
    "Ivory": "#FFFFF0",
    "Khaki": "#F0E68C",
    "Lavender": "#E6E6FA",
    "Lavender Blush": "#FFF0F5",
    "Lawn Green": "#7CFC00",
    "Lemon Chiffon": "#FFFACD",
    "Light Blue": "#ADD8E6",
    "Light Coral": "#F08080",
    "Light Cyan": "#E0FFFF",
    "Light Goldenrod Yellow": "#FAFAD2",
    "Light Gray": "#D3D3D3",
    "Light Green": "#90EE90",
    "Light Pink": "#FFB6C1",
    "Light Salmon": "#FFA07A",
    "Light Sea Green": "#20B2AA",
    "Light Sky Blue": "#87CEFA",
    "Light Slate Gray": "#778899",
    "Light Steel Blue": "#B0C4DE",
    "Light Yellow": "#FFFFE0",
    "Lime": "#00FF00",
    "Lime Green": "#32CD32",
    "Linen": "#FAF0E6",
    "Magenta": "#FF00FF",
    "Maroon": "#800000",
    "Medium Aquamarine": "#66CDAA",
    "Medium Blue": "#0000CD",
    "Medium Orchid": "#BA55D3",
    "Medium Purple": "#9370DB",
    "Medium Sea Green": "#3CB371",
    "Medium Slate Blue": "#7B68EE",
    "Medium Spring Green": "#00FA9A",
    "Medium Turquoise": "#48D1CC",
    "Medium Violet Red": "#C71585",
    "Midnight Blue": "#191970",
    "Mint Cream": "#F5FFFA",
    "Misty Rose": "#FFE4E1",
    "Moccasin": "#FFE4B5",
    "Navajo White": "#FFDEAD",
    "Navy": "#000080",
    "Old Lace": "#FDF5E6",
    "Olive": "#808000",
    "Olive Drab": "#6B8E23",
    "Orange": "#FFA500",
    "Orange Red": "#FF4500",
    "Orchid": "#DA70D6",
    "Pale Goldenrod": "#EEE8AA",
    "Pale Green": "#98FB98",
    "Pale Turquoise": "#AFEEEE",
    "Pale Violet Red": "#DB7093",
    "Papaya Whip": "#FFEFD5",
    "Peach Puff": "#FFDAB9",
    "Peru": "#CD853F",
    "Pink": "#FFC0CB",
    "Plum": "#DDA0DD",
    "Powder Blue": "#B0E0E6",
    "Purple": "#800080",
    "Rebecca Purple": "#663399",
    "Rosy Brown": "#BC8F8F",
    "Royal Blue": "#4169E1",
    "Saddle Brown": "#8B4513",
    "Salmon": "#FA8072",
    "Sandy Brown": "#F4A460",
    "Sea Green": "#2E8B57",
    "Sea Shell": "#FFF5EE",
    "Sienna": "#A0522D",
    "Silver": "#C0C0C0",
    "Sky Blue": "#87CEEB",
    "Slate Blue": "#6A5ACD",
    "Slate Gray": "#708090",
    "Snow": "#FFFAFA",
    "Spring Green": "#00FF7F",
    "Steel Blue": "#4682B4",
    "Tan": "#D2B48C",
    "Teal": "#008080",
    "Thistle": "#D8BFD8",
    "Tomato": "#FF6347",
    "Turquoise": "#40E0D0",
    "Violet": "#EE82EE",
    "Wheat": "#F5DEB3",
    "White": "#FFFFFF",
    "White Smoke": "#F5F5F5",
    "Yellow": "#FFFF00",
    "Yellow Green": "#9ACD32",
}

def _hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.strip().lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def load_color_names() -> List[Tuple[str, int, int, int]]:
    colors_rgb = []
    for name, hex_str in CREATOR_COLORS.items():
        colors_rgb.append((name, *_hex_to_rgb(hex_str)))

    try:
        json_path = resource_path("assets/colornames.json")
        if Path(json_path).exists():
            with open(json_path, "r", encoding="utf-8") as f:
                color_list = json.load(f)
                for c in color_list:
                    name = c.get("name")
                    hexv = c.get("hex")
                    if name and hexv:
                        colors_rgb.append((name, *_hex_to_rgb(hexv)))
    except Exception as e:
        print(f"Warning: Could not load colornames.json. Using fallback. ({e})")

    return colors_rgb

CSS_COLORS_RGB = load_color_names()

def nearest_color_name(r: int, g: int, b: int) -> str:
    best_name = "Unknown"
    best_d = 10**18
    for name, cr, cg, cb in CSS_COLORS_RGB:
        d = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2
        if d < best_d:
            best_d = d
            best_name = name
            if best_d == 0:
                break
    return best_name

def ass_alpha_to_qt(a_ass: int) -> int:
    a_ass = max(0, min(255, int(a_ass)))
    return 255 - a_ass

def parse_ass_color(s: str) -> Tuple[int, int, int, int]:
    t = s.strip().replace(" ", "")
    m = re.match(r"^&?H?([0-9A-Fa-f]{6,8})&?$", t)
    if not m:
        raise ValueError(f"Invalid ASS color: {s!r}")

    hexpart = m.group(1)
    if len(hexpart) == 6:
        bb, gg, rr, aa = (
            int(hexpart[0:2], 16),
            int(hexpart[2:4], 16),
            int(hexpart[4:6], 16),
            0,
        )
    else:
        aa, bb, gg, rr = (
            int(hexpart[0:2], 16),
            int(hexpart[2:4], 16),
            int(hexpart[4:6], 16),
            int(hexpart[6:8], 16),
        )
    return rr, gg, bb, aa

def format_ass_color(r: int, g: int, b: int, a: int = 0) -> str:
    r, g, b, a = (
        max(0, min(255, int(r))),
        max(0, min(255, int(g))),
        max(0, min(255, int(b))),
        max(0, min(255, int(a))),
    )
    return f"&H{a:02X}{b:02X}{g:02X}{r:02X}"

def strip_ass_tags(text: str) -> str:
    t = re.sub(r"\{[^}]*\}", "", text)
    t = t.replace("\\N", "\n").replace("\\n", "\n").replace("\\h", " ")
    return t.strip()
