from __future__ import annotations

import json
import os
import re
import shutil
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import QSettings, Qt, QThread, QTimer, QUrl, Signal
from PySide6.QtGui import (
    QAction,
    QColor,
    QDesktopServices,
    QFont,
    QFontMetrics,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QDialog,
    QFileDialog,
    QFontComboBox,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

APP_VERSION = "v1.12.0"
# Redefine what "100%" means for preview sizing.
BASE_PREVIEW_SCALE = 0.45


def resource_path(relative: str) -> str:
    """Return an absolute path to a resource, working for dev and PyInstaller builds."""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return str(Path(base) / relative)
    return str(Path(__file__).resolve().parent / relative)


# -----------------------------
# Color naming (dynamic JSON loader)
# -----------------------------


def _hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.strip().lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def load_color_names() -> List[Tuple[str, int, int, int]]:
    """Loads the massive color list from JSON, while prioritizing creator colors."""
    colors_rgb = []

    creator_colors = {
        # --- Easter Eggs & Creator Colors ---
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

    for name, hex_str in creator_colors.items():
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


# -----------------------------
# ASS parsing / writing
# -----------------------------


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


@dataclass
class AssStyle:
    name: str
    fields: Dict[str, str]


@dataclass
class AssDoc:
    lines: List[str]
    format_cols: List[str]
    styles: List[AssStyle]
    style_line_indices: List[int]
    all_dialogues: List[str]
    dialogues_by_style: Dict[str, List[str]]
    bg_color: Optional[str]
    parsed_dialogues: List[Dict]

    @staticmethod
    def load(path: str) -> "AssDoc":
        text = Path(path).read_text(encoding="utf-8-sig", errors="replace")
        raw_lines = text.splitlines()

        lines = []
        bg_color = None
        for l in raw_lines:
            if l.startswith("Dialogue:"):
                parts = l.split(":", 1)[1].split(",", 9)
                if len(parts) == 10 and parts[8].strip().startswith("ChromaShadow"):
                    continue
            elif l.startswith("; kbputils_background_1.0 color:"):
                bg_color = l.split("color:", 1)[1].strip()
            lines.append(l)

        section_name = (
            "V4+ Styles"
            if any(l.strip() == "[V4+ Styles]" for l in lines)
            else "V4 Styles"
        )

        in_styles = False
        style_section_indices: List[int] = []
        for i, l in enumerate(lines):
            s = l.strip()
            if s.startswith("[") and s.endswith("]"):
                in_styles = s == f"[{section_name}]"
                continue
            if in_styles:
                style_section_indices.append(i)

        format_cols: List[str] = []
        for i in style_section_indices:
            if lines[i].strip().lower().startswith("format:"):
                fmt = lines[i].split(":", 1)[1]
                format_cols = [c.strip() for c in fmt.split(",") if c.strip()]
                break

        styles: List[AssStyle] = []
        style_line_indices: List[int] = []
        for i in style_section_indices:
            if not lines[i].strip().lower().startswith("style:"):
                continue
            payload = lines[i].split(":", 1)[1].lstrip()
            parts = [p.strip() for p in payload.split(",")]

            if len(parts) < len(format_cols):
                parts += [""] * (len(format_cols) - len(parts))
            elif len(parts) > len(format_cols):
                head = parts[: len(format_cols) - 1]
                tail = ",".join(parts[len(format_cols) - 1 :])
                parts = head + [tail]

            fields = dict(zip(format_cols, parts))
            name = fields.get("Name", f"Style@{i}")
            styles.append(AssStyle(name=name, fields=fields))
            style_line_indices.append(i)

        all_dialogues, by_style, parsed_dialogues = AssDoc._extract_dialogues(lines)

        return AssDoc(
            lines=lines,
            format_cols=format_cols,
            styles=styles,
            style_line_indices=style_line_indices,
            all_dialogues=all_dialogues,
            dialogues_by_style=by_style,
            bg_color=bg_color,
            parsed_dialogues=parsed_dialogues,
        )

    @staticmethod
    def _extract_dialogues(
        lines: List[str],
    ) -> Tuple[List[str], Dict[str, List[str]], List[Dict]]:
        in_events = False
        event_format: Optional[List[str]] = None
        all_dialogues = []
        by_style = {}
        parsed_dialogues = []

        def parse_time(t_str: str) -> int:
            try:
                h, m, s = t_str.split(":")
                s, cs = s.split(".")
                return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(cs) * 10
            except:
                return 0

        for l in lines:
            s = l.strip()
            if s.startswith("[") and s.endswith("]"):
                in_events = s == "[Events]"
                event_format = None
                continue
            if not in_events:
                continue

            if s.lower().startswith("format:"):
                fmt = s.split(":", 1)[1]
                event_format = [c.strip() for c in fmt.split(",") if c.strip()]
                continue

            if s.lower().startswith("dialogue:"):
                payload = s.split(":", 1)[1].lstrip()
                parts = [p.strip() for p in payload.split(",")]

                if event_format and len(parts) >= len(event_format):
                    if len(parts) > len(event_format):
                        head = parts[: len(event_format) - 1]
                        tail = ",".join(parts[len(event_format) - 1 :])
                        parts = head + [tail]

                    data = dict(zip(event_format, parts))
                    txt = data.get("Text") or data.get("text")
                    style = data.get("Style") or data.get("style", "")
                    start_t = data.get("Start", "0:00:00.00")
                    end_t = data.get("End", "0:00:00.00")

                    if txt:
                        clean_txt = strip_ass_tags(txt)
                        all_dialogues.append(clean_txt)
                        if style:
                            if style not in by_style:
                                by_style[style] = []
                            by_style[style].append(clean_txt)

                        clean_lines = clean_txt.split("\n")
                        parsed_dialogues.append(
                            {
                                "start": parse_time(start_t),
                                "end": parse_time(end_t),
                                "style": style,
                                "lines": clean_lines,
                            }
                        )

        return all_dialogues, by_style, parsed_dialogues

    def save_as(self, out_path: str, bg_color_hex: Optional[str] = None) -> None:
        import math

        new_style_lines = []
        for st in self.styles:
            clean_fields = {
                k: v for k, v in st.fields.items() if not k.startswith("Chroma")
            }
            row = [clean_fields.get(col, "") for col in self.format_cols]
            new_style_lines.append("Style: " + ",".join(row))

        if self.style_line_indices:
            start = self.style_line_indices[0]
            end = self.style_line_indices[-1]
            self.lines[start : end + 1] = new_style_lines

        final_lines = []

        for line in self.lines:
            if line.startswith("; kbputils_background_1.0 color:"):
                continue

            if line.startswith("Dialogue:"):
                prefix, payload = line.split(":", 1)
                parts = payload.split(",", 9)

                if len(parts) == 10:
                    layer, start, end, stylename, name, ml, mr, mv, effect, text = parts
                    stylename = stylename.strip()

                    target_style = next(
                        (s for s in self.styles if s.name == stylename), None
                    )

                    if target_style:
                        angle = float(target_style.fields.get("ChromaAngle", 45))
                        is_3d = target_style.fields.get("Chroma3D", "False") == "True"
                        steps = int(target_style.fields.get("ChromaSteps", 10))
                        shadow_dist = float(target_style.fields.get("Shadow", 0))

                        if shadow_dist > 0:
                            angle_rad = math.radians(angle)
                            base_layer = int(layer)

                            clean_text = re.sub(r"\\[xy]?shad[0-9.-]+", "", text)

                            if is_3d:
                                for i in range(steps, 0, -1):
                                    frac = i / steps
                                    dx = shadow_dist * frac * math.cos(angle_rad)
                                    dy = shadow_dist * frac * math.sin(angle_rad)
                                    override = f"{{\\xshad{dx:.2f}\\yshad{dy:.2f}}}"
                                    shadow_effect = (
                                        f"ChromaShadow;{effect}"
                                        if effect
                                        else "ChromaShadow"
                                    )
                                    layer_payload = f"{base_layer},{start},{end},{stylename},{name},{ml},{mr},{mv},{shadow_effect},{override}{clean_text}"
                                    final_lines.append(f"{prefix}:{layer_payload}")

                                override = f"{{\\xshad0\\yshad0}}"
                                top_payload = f"{base_layer + 1},{start},{end},{stylename},{name},{ml},{mr},{mv},{effect},{override}{clean_text}"
                                final_lines.append(f"{prefix}:{top_payload}")
                                continue
                            else:
                                dx = shadow_dist * math.cos(angle_rad)
                                dy = shadow_dist * math.sin(angle_rad)
                                override = f"{{\\xshad{dx:.2f}\\yshad{dy:.2f}}}"
                                single_payload = f"{base_layer},{start},{end},{stylename},{name},{ml},{mr},{mv},{effect},{override}{clean_text}"
                                final_lines.append(f"{prefix}:{single_payload}")
                                continue

            final_lines.append(line)

        if bg_color_hex:
            final_lines.append(f"; kbputils_background_1.0 color: {bg_color_hex}")

        Path(out_path).write_text(
            "\n".join(final_lines) + "\n", encoding="utf-8", newline="\n"
        )


def style_get_int(style: AssStyle, key: str, default: int = 0) -> int:
    v = style.fields.get(key)
    if v is None or v == "":
        return default
    try:
        return int(v)
    except ValueError:
        return default


def style_get_color(style: AssStyle, key: str) -> Optional[Tuple[int, int, int, int]]:
    v = style.fields.get(key)
    if not v:
        return None
    try:
        return parse_ass_color(v)
    except ValueError:
        return None


def style_set_color(style: AssStyle, key: str, rgba: Tuple[int, int, int, int]) -> None:
    if key not in style.fields:
        raise KeyError(f"Style format does not include '{key}'.")
    r, g, b, a = rgba
    style.fields[key] = format_ass_color(r, g, b, a)


# -----------------------------
# GitHub Update Worker
# -----------------------------


class GitHubUpdateWorker(QThread):
    update_available = Signal(str, str, str)

    def run(self):
        try:
            url = "https://api.github.com/repos/mattjoykaraoke/ChromaLyric/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "ChromaLyric-App"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                latest_version = data.get("tag_name", "")
                release_notes = data.get("body", "")
                html_url = data.get("html_url", "")
                self.update_available.emit(latest_version, release_notes, html_url)
        except Exception:
            pass


# -----------------------------
# Preview widget
# -----------------------------


class AssPreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(200)
        self.setMaximumHeight(600)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding
        )

        self.sample_text = "Sample Text  AaBb  123  ♪"
        self.ass_style: Optional[AssStyle] = None
        self.preview_scale = BASE_PREVIEW_SCALE
        self.bg_color = QColor(30, 30, 30)

        self.karaoke_progress = 0.35
        self.shadow_angle = 45
        self.shadow_3d = False
        self.shadow_steps = 10

    def set_style(self, style: Optional[AssStyle]):
        self.ass_style = style
        self.update()

    def set_text(self, text: str):
        self.sample_text = text if text.strip() else " "
        self.update()

    def set_preview_scale(self, scale: float):
        self.preview_scale = max(0.10, min(6.0, float(scale)))
        self.update()

    def set_bg_color(self, c: QColor):
        self.bg_color = c
        self.update()

    def set_k_progress(self, progress01: float):
        self.karaoke_progress = max(0.0, min(1.0, float(progress01)))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing
        )
        p.fillRect(self.rect(), self.bg_color)

        if not self.ass_style:
            p.end()
            return

        st = self.ass_style
        prim = style_get_color(st, "PrimaryColour") or (255, 255, 255, 0)
        sec = style_get_color(st, "SecondaryColour") or (255, 255, 0, 0)
        outl = style_get_color(st, "OutlineColour") or (0, 0, 0, 0)
        back = style_get_color(st, "BackColour") or (0, 0, 0, 0)

        prim_q = QColor(prim[0], prim[1], prim[2], ass_alpha_to_qt(prim[3]))
        sec_q = QColor(sec[0], sec[1], sec[2], ass_alpha_to_qt(sec[3]))
        outl_q = QColor(outl[0], outl[1], outl[2], ass_alpha_to_qt(outl[3]))
        back_q = QColor(back[0], back[1], back[2], ass_alpha_to_qt(back[3]))

        fontname = st.fields.get("Fontname", "Arial")
        fontsize = style_get_int(st, "Fontsize", 48)
        bold = style_get_int(st, "Bold", 0) != 0
        italic = style_get_int(st, "Italic", 0) != 0

        s = self.preview_scale

        font = QFont(fontname)
        font.setPixelSize(max(1, int(fontsize * s)))
        font.setBold(bold)
        font.setItalic(italic)

        outline_w = float(style_get_int(st, "Outline", 0)) * s
        shadow = float(style_get_int(st, "Shadow", 0)) * s

        align = style_get_int(st, "Alignment", 2)
        vpos = (
            "bottom"
            if align in (1, 2, 3)
            else ("middle" if align in (4, 5, 6) else "top")
        )
        hpos = (
            "left"
            if align in (1, 4, 7)
            else ("center" if align in (2, 5, 8) else "right")
        )

        margin = int(24 * s)
        sub_rect = self.rect().adjusted(margin, margin, -margin, -margin)

        p.setFont(font)
        metrics = p.fontMetrics()
        lines = self.sample_text.splitlines() if self.sample_text else [" "]

        line_h = metrics.height()
        block_h = line_h * len(lines)

        if vpos == "bottom":
            y0 = sub_rect.bottom() - int(36 * s) - block_h
        elif vpos == "middle":
            y0 = sub_rect.center().y() - block_h // 2
        else:
            y0 = sub_rect.top() + int(36 * s)

        for li, text in enumerate(lines):
            text_rect = metrics.boundingRect(text)

            if hpos == "left":
                x = sub_rect.left() + int(36 * s)
            elif hpos == "center":
                x = sub_rect.center().x() - text_rect.width() / 2
            else:
                x = sub_rect.right() - text_rect.width() - int(36 * s)

            baseline_x = int(x)
            baseline_y = int(y0 + (li + 1) * line_h)

            path = QPainterPath()
            path.addText(baseline_x, baseline_y, font, text)

            if shadow > 0.0 and back_q.alpha() > 0:
                import math

                angle_rad = math.radians(self.shadow_angle)
                if self.shadow_3d:
                    steps = max(1, min(15, self.shadow_steps))
                    for i in range(steps, 0, -1):
                        frac = i / steps
                        dx = shadow * frac * math.cos(angle_rad)
                        dy = shadow * frac * math.sin(angle_rad)
                        p.fillPath(path.translated(dx, dy), back_q)
                else:
                    dx = shadow * math.cos(angle_rad)
                    dy = shadow * math.sin(angle_rad)
                    p.fillPath(path.translated(dx, dy), back_q)

            if outline_w > 0.0 and outl_q.alpha() > 0:
                pen = QPen(
                    outl_q,
                    outline_w * 2.0,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin,
                )
                p.strokePath(path, pen)

            p.fillPath(path, sec_q)

            if prim_q.alpha() > 0:
                bounds = path.boundingRect()
                clip_w = bounds.width() * self.karaoke_progress
                clip = bounds.adjusted(0, 0, -(bounds.width() - clip_w), 0)
                p.save()
                p.setClipRect(clip)
                p.fillPath(path, prim_q)
                p.restore()

        p.end()


# -----------------------------
# Swatch control widget
# -----------------------------


class SwatchControl(QWidget):
    clicked = Signal()

    def __init__(self, title: str):
        super().__init__()
        self._title = title
        self._rgba: Optional[Tuple[int, int, int, int]] = None

        self.title_lbl = QLabel(title)
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_lbl.setStyleSheet("color: white; font-weight: 800; font-size: 14px;")

        self.swatch_btn = QPushButton("")
        self.swatch_btn.setFixedHeight(52)
        self.swatch_btn.clicked.connect(self.clicked.emit)

        self.name_lbl = QLabel("")
        self.name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_lbl.setStyleSheet("color: white; font-weight: 600; font-size: 13px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.swatch_btn)
        layout.addWidget(self.name_lbl)
        self.setLayout(layout)

    def set_rgba(self, rgba: Optional[Tuple[int, int, int, int]]):
        self._rgba = rgba
        if rgba is None:
            self.swatch_btn.setStyleSheet("padding: 8px; border: 1px solid #444;")
            self.name_lbl.setText("(missing)")
            return

        r, g, b, a = rgba
        qt_a = ass_alpha_to_qt(a)
        self.swatch_btn.setStyleSheet(
            f"background-color: rgba({r},{g},{b},{qt_a}); border: 1px solid #444;"
        )
        hexv = f"#{r:02X}{g:02X}{b:02X}"
        nm = nearest_color_name(r, g, b)
        self.name_lbl.setText(f"{nm}  {hexv}")


# -----------------------------
# Drag & drop
# -----------------------------


def is_supported_file(path: str) -> bool:
    return Path(path).suffix.lower() == ".ass"


class DropWidget(QWidget):
    fileDropped = Signal(str)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        self.label = QLabel("Drag & drop an .ass file anywhere\n—or click Open…")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 16px; padding: 18px; color: white;")

        self.open_btn = QPushButton("Open…")
        self.open_btn.clicked.connect(self.open_file_dialog)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.open_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open ASS file", "", "ASS (*.ass);;All files (*.*)"
        )
        if path:
            self.fileDropped.emit(path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if any(
                u.isLocalFile() and is_supported_file(u.toLocalFile())
                for u in event.mimeData().urls()
            ):
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event):
        for u in event.mimeData().urls():
            if u.isLocalFile() and is_supported_file(u.toLocalFile()):
                self.fileDropped.emit(u.toLocalFile())
                event.acceptProposedAction()
                return
        event.ignore()


class ImageDropper(QLabel):
    colorPicked = Signal(QColor)

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("border: 2px dashed #444; background-color: #121212;")
        self.setText("Click 'Load Image' to begin")
        self.source_image = None
        self.scaled_image = None

    def load_image(self, path: str):
        self.source_image = QImage(path)
        self.update_image()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.source_image:
            self.update_image()

    def update_image(self):
        if self.source_image is None or self.source_image.isNull():
            return
        self.scaled_image = self.source_image.scaled(
            self.width(),
            self.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(QPixmap.fromImage(self.scaled_image))

    def mousePressEvent(self, event):
        if not self.scaled_image:
            return
        x_offset = (self.width() - self.scaled_image.width()) // 2
        y_offset = (self.height() - self.scaled_image.height()) // 2
        px = int(event.position().x()) - x_offset
        py = int(event.position().y()) - y_offset

        if 0 <= px < self.scaled_image.width() and 0 <= py < self.scaled_image.height():
            color = self.scaled_image.pixelColor(px, py)
            self.colorPicked.emit(color)


class PickedColorWidget(QWidget):
    transferColor = Signal(str, QColor)

    def __init__(self, color: QColor):
        super().__init__()
        self.color = color
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)

        self.swatch = QLabel()
        self.swatch.setFixedSize(24, 24)
        self.swatch.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid #444; border-radius: 3px;"
        )

        self.hex_lbl = QLabel(color.name().upper())
        self.hex_lbl.setStyleSheet(
            "font-family: monospace; font-weight: bold; font-size: 13px;"
        )
        self.hex_lbl.setFixedWidth(65)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)
        targets = [
            ("H", "PrimaryColour", "Highlight"),
            ("B", "SecondaryColour", "Base"),
            ("O", "OutlineColour", "Outline"),
            ("S", "BackColour", "Shadow"),
            ("BG", "Background", "Preview BG"),
        ]

        for text, key, tooltip in targets:
            btn = QPushButton(text)
            btn.setFixedSize(26, 26)
            btn.setToolTip(f"Send to {tooltip}")
            btn.setStyleSheet("font-weight: bold; font-size: 11px;")
            btn.clicked.connect(
                lambda checked=False, k=key, c=color: self.transferColor.emit(k, c)
            )
            btn_layout.addWidget(btn)

        layout.addWidget(self.swatch)
        layout.addWidget(self.hex_lbl)
        layout.addLayout(btn_layout)
        layout.addStretch()
        self.setLayout(layout)


import math

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QPen


class AnglePicker(QWidget):
    angleChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)
        self.angle = 45

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(2, 2, -2, -2)
        p.setPen(QPen(QColor("#444"), 2))
        p.drawEllipse(rect)

        center = rect.center()
        rad = math.radians(self.angle)
        end_x = center.x() + (rect.width() / 2) * math.cos(rad)
        end_y = center.y() + (rect.height() / 2) * math.sin(rad)

        p.setPen(QPen(QColor("#17CDBE"), 2))
        p.drawLine(center, QPointF(end_x, end_y))

        p.setBrush(QColor("#17CDBE"))
        p.drawEllipse(QPointF(end_x, end_y), 4, 4)

    def mousePressEvent(self, event):
        self.update_angle(event.position())

    def mouseMoveEvent(self, event):
        self.update_angle(event.position())

    def update_angle(self, pos):
        center = self.rect().center()
        dx = pos.x() - center.x()
        dy = pos.y() - center.y()

        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        if angle_deg < 0:
            angle_deg += 360

        for snap in [0, 45, 90, 135, 180, 225, 270, 315, 360]:
            if abs(angle_deg - snap) < 15:
                angle_deg = snap
                break

        self.angle = int(angle_deg % 360)
        self.angleChanged.emit(self.angle)
        self.update()


# -----------------------------
# ChromaPicker
# -----------------------------


class ChromaPickerWindow(QDialog):
    colorTransferred = Signal(str, QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ChromaPicker - Image Color Extractor")
        self.resize(850, 550)
        self.setStyleSheet(
            "QDialog { background-color: #1E1E1E; color: white; } QLabel { color: white; }"
        )
        self.setAcceptDrops(True)

        self.dropper = ImageDropper()
        self.dropper.colorPicked.connect(self.add_color_to_list)
        self.dropper.setText("Click 'Load Image' or Drag & Drop here to begin")

        self.load_btn = QPushButton("📂 Load Image (JPG/PNG)")
        self.load_btn.setFixedHeight(35)
        self.load_btn.clicked.connect(self.open_image)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.dropper, stretch=1)
        left_layout.addWidget(self.load_btn)

        self.color_list = QListWidget()
        self.color_list.setFixedWidth(280)
        self.color_list.setStyleSheet(
            "QListWidget { background-color: #121212; border: 1px solid #444; }"
        )

        self.clear_btn = QPushButton("🗑 Clear Palette")
        self.clear_btn.clicked.connect(self.color_list.clear)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("<b>Extracted Palette</b>"))
        right_layout.addWidget(self.color_list)
        right_layout.addWidget(self.clear_btn)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addLayout(right_layout, stretch=1)
        self.setLayout(main_layout)

    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if path:
            self.dropper.load_image(path)

    def add_color_to_list(self, color: QColor):
        item = QListWidgetItem(self.color_list)
        widget = PickedColorWidget(color)
        widget.transferColor.connect(self.colorTransferred.emit)
        item.setSizeHint(widget.sizeHint())
        self.color_list.insertItem(0, item)
        self.color_list.setItemWidget(item, widget)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    ext = Path(url.toLocalFile()).suffix.lower()
                    if ext in [".png", ".jpg", ".jpeg"]:
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                ext = Path(path).suffix.lower()
                if ext in [".png", ".jpg", ".jpeg"]:
                    self.dropper.load_image(path)
                    event.acceptProposedAction()
                    return
        event.ignore()


# -----------------------------
# Main window
# -----------------------------


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChromaLyric")
        self.resize(1220, 780)
        self.setAcceptDrops(True)

        self.doc: Optional[AssDoc] = None
        self.current_path: Optional[str] = None
        self.style_line_idx: Dict[str, int] = {}

        self.picker = None
        self.CURRENT_VERSION = APP_VERSION
        self.settings = QSettings("MattJoy", "ChromaLyric")

        self.check_for_updates()

        # Left Column
        self.drop = DropWidget()
        self.drop.fileDropped.connect(self.load_ass)

        self.styles_list = QListWidget()
        self.styles_list.currentRowChanged.connect(self.on_style_selected)
        self.styles_list.setStyleSheet("font-size: 14px;")

        self.about_btn = QPushButton("About")
        self.about_btn.clicked.connect(self.show_about)

        left = QVBoxLayout()
        left.addWidget(self.drop)

        self.styles_group = QGroupBox("Styles")
        styles_layout = QVBoxLayout()
        styles_layout.addWidget(self.styles_list)
        self.styles_group.setLayout(styles_layout)

        left.addWidget(self.styles_group)

        self.preset_group = QGroupBox("Theme Library")
        preset_layout = QVBoxLayout()

        self.preset_list = QListWidget()
        self.preset_list.setStyleSheet("font-size: 14px;")
        self.preset_list.itemDoubleClicked.connect(self.apply_preset)

        self.preset_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.preset_list.customContextMenuRequested.connect(
            self.show_preset_context_menu
        )

        self.save_preset_btn = QPushButton("💾 Save Current")
        self.save_preset_btn.clicked.connect(self.save_new_preset)

        self.lib_options_btn = QPushButton("⚙")
        self.lib_options_btn.setFixedWidth(36)

        self.lib_menu = QMenu(self)
        self.lib_menu.addAction("Export Library...").triggered.connect(
            self.export_presets
        )
        self.lib_menu.addAction("Import Library...").triggered.connect(
            self.import_presets
        )
        self.lib_options_btn.setMenu(self.lib_menu)

        lib_btn_row = QHBoxLayout()
        lib_btn_row.addWidget(self.save_preset_btn)
        lib_btn_row.addWidget(self.lib_options_btn)

        preset_layout.addWidget(self.preset_list)
        preset_layout.addLayout(lib_btn_row)
        self.preset_group.setLayout(preset_layout)

        left.addWidget(self.preset_group)

        self.chroma_picker_btn = QPushButton("👁 ChromaPicker")
        self.chroma_picker_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 8px;
                font-weight: bold;
                background-color: #2D2D30;
                border: 1px solid #555;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #3E3E42; }
        """)
        self.chroma_picker_btn.clicked.connect(self.open_chroma_picker)
        left.addWidget(self.chroma_picker_btn)

        self.presets = []
        self.load_presets()
        self.load_custom_colors()

        left.addStretch(1)
        left.addWidget(self.about_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        left_wrap = QWidget()
        left_wrap.setLayout(left)

        # Right Column
        self.info = QLabel("Open an .ass file to begin.")
        self.info.setWordWrap(True)

        self.preview = AssPreviewWidget()

        self.preview_text = QLineEdit()
        self.preview_text.setPlaceholderText(
            r"Preview text… (you can use \N for new lines)"
        )
        self.preview_text.textChanged.connect(self.on_preview_text_changed)

        self.use_first_line_btn = QPushButton("Use First Line of Lyrics")
        self.use_first_line_btn.clicked.connect(self.use_first_song_line)
        self.use_first_line_btn.setEnabled(False)

        self.next_line_btn = QPushButton("Next Line")
        self.next_line_btn.clicked.connect(self.next_song_line)
        self.next_line_btn.setEnabled(False)

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(25)
        self.zoom_slider.setMaximum(250)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)

        self.zoom_lbl = QLabel("Zoom: 100%")
        self.zoom_lbl.setMinimumWidth(90)

        self.reset_zoom_btn = QPushButton("Reset Zoom")
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)

        self.bg_hex = QLineEdit("#1E1E1E")
        self.bg_hex.setMaximumWidth(100)
        self.bg_hex.editingFinished.connect(self.on_bg_hex_changed)

        self.bg_pick_btn = QPushButton("Pick BG…")
        self.bg_pick_btn.clicked.connect(self.pick_bg)

        self.k_slider = QSlider(Qt.Orientation.Horizontal)
        self.k_slider.setMinimum(0)
        self.k_slider.setMaximum(100)
        self.k_slider.setValue(35)
        self.k_slider.valueChanged.connect(self.on_k_changed)

        self.k_lbl = QLabel("K: 35%")
        self.k_lbl.setMinimumWidth(70)

        self.k_play_btn = QPushButton("▶ Play")
        self.k_play_btn.clicked.connect(self.toggle_k_play)

        self.k_timer = QTimer(self)
        self.k_timer.setInterval(20)
        self.k_timer.timeout.connect(self.on_k_timer_tick)

        ctrl_row1 = QHBoxLayout()
        ctrl_row1.addWidget(QLabel("Text:"))
        ctrl_row1.addWidget(self.preview_text, 1)
        ctrl_row1.addWidget(self.use_first_line_btn)
        ctrl_row1.addWidget(self.next_line_btn)

        ctrl_row2 = QHBoxLayout()
        ctrl_row2.addWidget(self.zoom_lbl)
        ctrl_row2.addWidget(self.zoom_slider, 1)
        ctrl_row2.addWidget(self.reset_zoom_btn)
        ctrl_row2.addSpacing(10)
        ctrl_row2.addWidget(QLabel("BG:"))
        ctrl_row2.addWidget(self.bg_hex)
        ctrl_row2.addWidget(self.bg_pick_btn)

        ctrl_row3 = QHBoxLayout()
        ctrl_row3.addWidget(QLabel(r"\k swipe:"))
        ctrl_row3.addWidget(self.k_play_btn)
        ctrl_row3.addWidget(self.k_lbl)
        ctrl_row3.addWidget(self.k_slider, 1)

        preview_box = QGroupBox("Preview")
        pv_layout = QVBoxLayout()
        pv_layout.addLayout(ctrl_row1)
        pv_layout.addLayout(ctrl_row2)
        pv_layout.addLayout(ctrl_row3)
        pv_layout.addWidget(self.preview)
        preview_box.setLayout(pv_layout)

        # Style Colors
        self.sw_highlight = SwatchControl("Highlight (PrimaryColour)")
        self.sw_base = SwatchControl("Base (SecondaryColour)")
        self.sw_outline = SwatchControl("Outline (OutlineColour)")

        self.sw_highlight.clicked.connect(lambda: self.pick_color("PrimaryColour"))
        self.sw_base.clicked.connect(lambda: self.pick_color("SecondaryColour"))
        self.sw_outline.clicked.connect(lambda: self.pick_color("OutlineColour"))

        self.sw_highlight.swatch_btn.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.sw_base.swatch_btn.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.sw_highlight.swatch_btn.customContextMenuRequested.connect(
            self.show_swap_menu
        )
        self.sw_base.swatch_btn.customContextMenuRequested.connect(self.show_swap_menu)

        self.outline_spin = QSpinBox()
        self.outline_spin.setRange(0, 20)
        self.outline_spin.setSingleStep(1)
        self.outline_spin.setFixedWidth(60)
        self.outline_spin.valueChanged.connect(self.on_outline_changed)

        colors_box = QGroupBox("Style Colors")
        colors_layout = QHBoxLayout()
        colors_layout.addWidget(self.sw_highlight)
        colors_layout.addWidget(self.sw_base)

        outline_row = QHBoxLayout()
        outline_row.setContentsMargins(0, 0, 0, 0)
        outline_row.setSpacing(8)
        outline_row.addWidget(self.sw_outline)
        outline_row.addWidget(
            self.outline_spin, alignment=Qt.AlignmentFlag.AlignVCenter
        )
        outline_container = QWidget()
        outline_container.setLayout(outline_row)

        colors_layout.addWidget(outline_container)
        colors_box.setLayout(colors_layout)

        # ---- NEW: Typography Controls ----
        self.typography_group = QGroupBox("Typography")
        self.typography_group.setCheckable(True)
        self.typography_group.setChecked(False)
        self.typography_group.toggled.connect(self.on_typography_group_toggled)

        self.typography_body = QWidget()
        typo_body_layout = QVBoxLayout()
        typo_body_layout.setContentsMargins(0, 0, 0, 0)
        typo_body_layout.setSpacing(6)

        # Typeface Row
        tf_row = QHBoxLayout()
        tf_row.addWidget(QLabel("Typeface:"))
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.on_font_name_changed)
        tf_row.addWidget(self.font_combo, 1)

        self.sync_typefaces_cb = QCheckBox("Sync All Styles")
        self.sync_typefaces_cb.setChecked(False)
        self.sync_typefaces_cb.toggled.connect(self.on_sync_typefaces_toggled)
        tf_row.addWidget(self.sync_typefaces_cb)

        # Size Row
        sz_row = QHBoxLayout()
        sz_row.addWidget(QLabel("Size (pt):"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(1, 400)
        self.font_size_spin.valueChanged.connect(self.on_font_size_changed)
        sz_row.addWidget(self.font_size_spin)

        self.sync_sizes_cb = QCheckBox("Sync All Styles")
        self.sync_sizes_cb.setChecked(True)
        sz_row.addWidget(self.sync_sizes_cb)
        sz_row.addStretch(1)

        # Format & Safety Row
        fmt_row = QHBoxLayout()
        self.bold_cb = QCheckBox("Bold")
        self.bold_cb.toggled.connect(self.on_font_format_changed)
        self.italic_cb = QCheckBox("Italic")
        self.italic_cb.toggled.connect(self.on_font_format_changed)

        self.snap_safe_btn = QPushButton("🛡️ Snap to 100%")
        self.snap_safe_btn.setToolTip(
            "Shrink font size until all stacked overlapping lyrics fit perfectly inside a 1080p boundary."
        )
        self.snap_safe_btn.clicked.connect(self.snap_to_safe_size)

        fmt_row.addWidget(self.bold_cb)
        fmt_row.addWidget(self.italic_cb)
        fmt_row.addStretch(1)
        fmt_row.addWidget(self.snap_safe_btn)

        typo_body_layout.addLayout(tf_row)
        typo_body_layout.addLayout(sz_row)
        typo_body_layout.addLayout(fmt_row)

        self.typography_body.setLayout(typo_body_layout)
        self.typography_body.setVisible(False)

        typo_group_layout = QVBoxLayout()
        typo_group_layout.setContentsMargins(8, 8, 8, 8)
        typo_group_layout.addWidget(self.typography_body)
        self.typography_group.setLayout(typo_group_layout)

        # Shadow Controls
        self.shadow_group = QGroupBox("Shadow")
        self.shadow_group.setCheckable(True)
        self.shadow_group.setChecked(False)
        self.shadow_group.toggled.connect(self.on_shadow_group_toggled)

        self.shadow_distance = QSpinBox()
        self.shadow_distance.setRange(0, 20)
        self.shadow_distance.setSingleStep(1)
        self.shadow_distance.setFixedWidth(60)
        self.shadow_distance.valueChanged.connect(self.on_shadow_distance_changed)

        self.shadow_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.shadow_opacity_slider.setRange(0, 100)

        self.shadow_opacity_spin = QSpinBox()
        self.shadow_opacity_spin.setRange(0, 100)
        self.shadow_opacity_spin.setSuffix("%")
        self.shadow_opacity_spin.setFixedWidth(60)

        self.shadow_opacity_slider.valueChanged.connect(
            self.shadow_opacity_spin.setValue
        )
        self.shadow_opacity_spin.valueChanged.connect(
            self.shadow_opacity_slider.setValue
        )
        self.shadow_opacity_spin.valueChanged.connect(self.on_shadow_opacity_changed)

        self.sw_shadow = SwatchControl("Shadow (BackColour)")
        self.sw_shadow.clicked.connect(lambda: self.pick_color("BackColour"))

        self.shadow_body = QWidget()
        shadow_body_layout = QVBoxLayout()
        shadow_body_layout.setContentsMargins(0, 0, 0, 0)
        shadow_body_layout.setSpacing(6)

        self.shadow_angle_picker = AnglePicker()
        self.shadow_angle_picker.angleChanged.connect(self.on_shadow_angle_changed)

        self.shadow_3d_cb = QCheckBox("Pseudo-3D Extrusion")
        self.shadow_3d_cb.toggled.connect(self.on_shadow_3d_toggled)

        self.shadow_steps = QSpinBox()
        self.shadow_steps.setRange(1, 15)
        self.shadow_steps.setValue(10)
        self.shadow_steps.setSuffix(" layers")
        self.shadow_steps.setFixedWidth(80)
        self.shadow_steps.setEnabled(False)
        self.shadow_steps.valueChanged.connect(self.on_shadow_steps_changed)

        row1 = QHBoxLayout()
        row1.addWidget(self.shadow_angle_picker)

        dist_3d_col = QVBoxLayout()
        dist_row = QHBoxLayout()
        dist_row.addWidget(QLabel("Distance/Depth:"))
        dist_row.addWidget(self.shadow_distance)
        dist_row.addStretch(1)

        step_row = QHBoxLayout()
        step_row.addWidget(self.shadow_3d_cb)
        step_row.addWidget(self.shadow_steps)
        step_row.addStretch(1)

        dist_3d_col.addLayout(dist_row)
        dist_3d_col.addLayout(step_row)

        row1.addLayout(dist_3d_col)
        row1.addStretch(1)
        shadow_body_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Transparency"))
        row2.addWidget(self.shadow_opacity_slider)
        row2.addWidget(self.shadow_opacity_spin)
        shadow_body_layout.addLayout(row2)

        self.quick_black_btn = QPushButton("⬛ Set Black")
        self.quick_black_btn.setToolTip("Instantly set shadow color to pure black")
        self.quick_black_btn.setMaximumWidth(90)
        self.quick_black_btn.clicked.connect(self.set_shadow_to_black)

        shadow_row3 = QHBoxLayout()
        shadow_row3.addWidget(self.sw_shadow)
        shadow_row3.addWidget(
            self.quick_black_btn, alignment=Qt.AlignmentFlag.AlignVCenter
        )
        shadow_body_layout.addLayout(shadow_row3)

        self.shadow_body.setLayout(shadow_body_layout)
        self.shadow_body.setVisible(False)

        self.shadow_distance.setEnabled(False)
        self.shadow_opacity_slider.setEnabled(False)
        self.shadow_opacity_spin.setEnabled(False)
        self.sw_shadow.setEnabled(False)
        self.quick_black_btn.setEnabled(False)

        shadow_group_layout = QVBoxLayout()
        shadow_group_layout.setContentsMargins(8, 8, 8, 8)
        shadow_group_layout.addWidget(self.shadow_body)
        self.shadow_group.setLayout(shadow_group_layout)

        # Save Controls
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_file)
        self.save_btn.setEnabled(False)

        self.save_as_btn = QPushButton("Save As…")
        self.save_as_btn.clicked.connect(self.save_as)
        self.save_as_btn.setEnabled(False)

        save_layout = QHBoxLayout()
        save_layout.addStretch(1)
        save_layout.addWidget(self.save_btn)
        save_layout.addWidget(self.save_as_btn)

        right = QVBoxLayout()
        right.addWidget(self.info)
        right.addWidget(preview_box, stretch=4)
        right.addWidget(colors_box, stretch=0)
        right.addWidget(self.typography_group, stretch=0)
        right.addWidget(self.shadow_group, stretch=0)
        right.addStretch(1)
        right.addLayout(save_layout)

        right_wrap = QWidget()
        right_wrap.setLayout(right)

        root = QWidget()
        root_layout = QHBoxLayout()
        root_layout.addWidget(left_wrap, 2)
        root_layout.addWidget(right_wrap, 5)
        root.setLayout(root_layout)
        self.setCentralWidget(root)

        self.setStyleSheet("""
            QLabel { color: white; }
            QGroupBox { color: white; }
        """)

        self.preview.set_bg_color(QColor(0x1E, 0x1E, 0x1E))
        self.preview.set_k_progress(self.k_slider.value() / 100.0)
        self.on_zoom_changed(self.zoom_slider.value())

        # Disabled state for Typography components until file load
        self.font_size_spin.setEnabled(False)
        self.font_combo.setEnabled(False)
        self.bold_cb.setEnabled(False)
        self.italic_cb.setEnabled(False)
        self.snap_safe_btn.setEnabled(False)

    # ---- Format Helper for Background Hex ----
    def format_bg_hex(self, c: QColor) -> str:
        if c.alpha() == 255:
            return c.name(QColor.NameFormat.HexRgb).upper()
        return c.name(QColor.NameFormat.HexArgb).upper()

    # ---- Update Checker Logic ----

    def check_for_updates(self):
        self.update_worker = GitHubUpdateWorker()
        self.update_worker.update_available.connect(self.prompt_update)
        self.update_worker.start()

    def prompt_update(self, latest_version: str, release_notes: str, url: str):
        if latest_version and latest_version > self.CURRENT_VERSION:
            reply = QMessageBox.question(
                self,
                "Update Available",
                f"A new version of ChromaLyric ({latest_version}) is available!\n\n"
                f"You are currently running {self.CURRENT_VERSION}.\n\n"
                "Would you like to open the download page?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl(url))

    # ---- Typography Editing ----

    def _calculate_timeline_bounds(
        self, size: int, fontname: str, bold: bool, italic: bool
    ) -> Tuple[int, int]:
        """
        Uses a sweep-line algorithm to measure overlapping text boxes across the entire timeline
        exactly simulating libass vertically stacking overlapping subtitles.
        """
        current_st = self.current_style()
        if not current_st:
            return 0, 0

        sync_sz = self.sync_sizes_cb.isChecked()
        sync_tf = self.sync_typefaces_cb.isChecked()

        # 1. Pre-build font metrics for every style based on hypothetically applied settings
        style_metrics = {}
        style_alignments = {}
        for st in self.doc.styles:
            sz = (
                size
                if (st.name == current_st.name or sync_sz)
                else style_get_int(st, "Fontsize", 48)
            )
            fname = (
                fontname
                if (st.name == current_st.name or sync_tf)
                else st.fields.get("Fontname", "Arial")
            )
            is_b = (
                bold
                if st.name == current_st.name
                else (style_get_int(st, "Bold", 0) != 0)
            )
            is_i = (
                italic
                if st.name == current_st.name
                else (style_get_int(st, "Italic", 0) != 0)
            )

            font = QFont(fname)
            font.setPixelSize(max(1, sz))
            font.setBold(is_b)
            font.setItalic(is_i)
            style_metrics[st.name] = QFontMetrics(font)
            style_alignments[st.name] = style_get_int(st, "Alignment", 2)

        # 2. Pre-calculate the block dimensions for every event to save time during sweep
        diag_dims = []
        for d in self.doc.parsed_dialogues:
            metrics = style_metrics.get(d["style"])
            if not metrics:
                diag_dims.append({"w": 0, "h": 0})
                continue
            ev_w = max((metrics.horizontalAdvance(l) for l in d["lines"]), default=0)
            ev_h = metrics.height() * len(d["lines"])
            diag_dims.append({"w": ev_w, "h": ev_h})

        # 3. Sweep Line Algorithm to find overlapping events
        events = []
        for i, diag in enumerate(self.doc.parsed_dialogues):
            events.append((diag["start"], "start", i))
            events.append((diag["end"], "end", i))

        # Sort by time. If times match, process 'end' before 'start' to prevent false overlap
        events.sort(key=lambda x: (x[0], x[1] == "start"))

        active_diags = set()
        global_max_w, global_max_h = 0, 0

        for time, ev_type, idx in events:
            if ev_type == "start":
                active_diags.add(idx)
            else:
                active_diags.discard(idx)

            # After an event is added or removed, re-evaluate stack boundaries
            align_groups = {}
            for active_idx in active_diags:
                d = self.doc.parsed_dialogues[active_idx]
                align = style_alignments.get(d["style"], 2)
                align_groups.setdefault(align, []).append(active_idx)

            for align, group in align_groups.items():
                # Filter out duplicates to prevent artificial stacking of identical text layers
                unique_texts = {}
                for active_idx in group:
                    d = self.doc.parsed_dialogues[active_idx]
                    text_key = "\n".join(d["lines"])
                    if text_key not in unique_texts:
                        unique_texts[text_key] = diag_dims[active_idx]

                gw, gh = 0, 0
                for dims in unique_texts.values():
                    gw = max(gw, dims["w"])  # Stack is as wide as its widest line
                    gh += dims["h"]  # Stack height is cumulative (libass stacking)

                global_max_w = max(global_max_w, gw)
                global_max_h = max(global_max_h, gh)

        return global_max_w, global_max_h

    def on_typography_group_toggled(self, checked: bool):
        self.typography_body.setVisible(checked)

    def check_font_boundaries(self):
        """Measures the global timeline to ensure stacked lyrics don't exceed 1920x1080"""
        if not self.doc or not self.doc.parsed_dialogues:
            return

        ui_fontname = self.font_combo.currentText()
        ui_fontsize = self.font_size_spin.value()
        ui_bold = self.bold_cb.isChecked()
        ui_italic = self.italic_cb.isChecked()

        global_max_w, global_max_h = self._calculate_timeline_bounds(
            ui_fontsize, ui_fontname, ui_bold, ui_italic
        )

        if global_max_w > 1920 or global_max_h > 1080:
            self.font_size_spin.setStyleSheet(
                "QSpinBox { background-color: #8B0000; color: white; }"
            )
            self.font_size_spin.setToolTip(
                f"Timeline stack exceeds 100% boundary! (Peak Overlap: {global_max_w}x{global_max_h} | Max: 1920x1080)"
            )
        else:
            self.font_size_spin.setStyleSheet("")
            self.font_size_spin.setToolTip("Font Size (pt)")

    def on_font_name_changed(self, font: QFont):
        st = self.current_style()
        if not st:
            return

        fontname = self.font_combo.currentText()
        if self.sync_typefaces_cb.isChecked():
            for s in self.doc.styles:
                s.fields["Fontname"] = fontname
        else:
            st.fields["Fontname"] = fontname

        self.check_font_boundaries()
        self.preview.update()

    def on_sync_typefaces_toggled(self, checked: bool):
        if checked:
            current_font_text = self.font_combo.currentText()
            reply = QMessageBox.question(
                self,
                "Synchronize Typefaces",
                f"Synchronize all typefaces to {current_font_text}?\nThis will overwrite the font choices for all other styles in the project.",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Ok:
                for s in self.doc.styles:
                    s.fields["Fontname"] = current_font_text
                self.check_font_boundaries()
                self.preview.update()
            else:
                self.sync_typefaces_cb.blockSignals(True)
                self.sync_typefaces_cb.setChecked(False)
                self.sync_typefaces_cb.blockSignals(False)

    def on_font_size_changed(self, size: int):
        st = self.current_style()
        if not st:
            return

        if self.sync_sizes_cb.isChecked():
            for s in self.doc.styles:
                s.fields["Fontsize"] = str(size)
        else:
            st.fields["Fontsize"] = str(size)

        self.check_font_boundaries()
        self.preview.update()

    def on_font_format_changed(self, checked: bool):
        st = self.current_style()
        if not st:
            return

        # Standard ASS boolean
        b_val = "-1" if self.bold_cb.isChecked() else "0"
        i_val = "-1" if self.italic_cb.isChecked() else "0"

        st.fields["Bold"] = b_val
        st.fields["Italic"] = i_val

        self.check_font_boundaries()
        self.preview.update()

    def snap_to_safe_size(self):
        """Automatically shrinks the font until ALL overlapping lyrics fit perfectly inside a 1080p boundary."""
        if not self.doc or not self.doc.parsed_dialogues:
            return

        ui_fontname = self.font_combo.currentText()
        ui_bold = self.bold_cb.isChecked()
        ui_italic = self.italic_cb.isChecked()
        size = self.font_size_spin.value()

        # Keep silently testing smaller sizes across the entire song until it fits
        while size > 1:
            global_max_w, global_max_h = self._calculate_timeline_bounds(
                size, ui_fontname, ui_bold, ui_italic
            )

            if global_max_w <= 1920 and global_max_h <= 1080:
                break
            size -= 1

        # Automatically updates the UI and syncs styles!
        self.font_size_spin.setValue(size)

    # ---- Outline / Shadow editing ----

    def on_outline_changed(self, value: int):
        st = self.current_style()
        if not st:
            return
        st.fields["Outline"] = str(value)
        self.preview.update()

    def on_shadow_group_toggled(self, checked: bool):
        self.shadow_body.setVisible(checked)
        self.shadow_distance.setEnabled(checked)
        self.shadow_opacity_slider.setEnabled(checked)
        self.shadow_opacity_spin.setEnabled(checked)
        self.sw_shadow.setEnabled(checked)
        self.quick_black_btn.setEnabled(checked)

    def on_shadow_distance_changed(self, value: int):
        st = self.current_style()
        if not st:
            return
        st.fields["Shadow"] = str(value)
        self.preview.update()

    def on_shadow_angle_changed(self, angle: int):
        self.preview.shadow_angle = angle
        st = self.current_style()
        if st:
            st.fields["ChromaAngle"] = str(angle)
        self.preview.update()

    def on_shadow_3d_toggled(self, checked: bool):
        self.preview.shadow_3d = checked
        self.shadow_steps.setEnabled(checked)
        st = self.current_style()
        if st:
            st.fields["Chroma3D"] = "True" if checked else "False"
        self.preview.update()

    def on_shadow_steps_changed(self, steps: int):
        self.preview.shadow_steps = steps
        st = self.current_style()
        if st:
            st.fields["ChromaSteps"] = str(steps)
        self.preview.update()

    def on_shadow_opacity_changed(self, pct: int):
        st = self.current_style()
        if not st:
            return
        pct = max(0, min(100, int(pct)))
        alpha = int(round(pct * 255 / 100))

        col = style_get_color(st, "BackColour") or (0, 0, 0, alpha)
        r, g, b, _ = col
        style_set_color(st, "BackColour", (r, g, b, alpha))
        self.sw_shadow.set_rgba((r, g, b, alpha))
        self.preview.update()

    # ---- File loading ----

    def load_ass(self, path: str):
        try:
            self.doc = AssDoc.load(path)
            self.current_path = path

            if self.doc.bg_color:
                c = QColor(self.doc.bg_color)
                if c.isValid():
                    self.preview.set_bg_color(c)
                    self.bg_hex.setText(self.format_bg_hex(c))

            self.styles_list.clear()
            for st in self.doc.styles:
                self.styles_list.addItem(QListWidgetItem(st.name))

            self.info.setText(f"Loaded:\n{path}\n\nSelect a style to edit its colors.")
            self.style_line_idx = {}

            self.save_btn.setEnabled(True)
            self.save_as_btn.setEnabled(True)
            self.font_size_spin.setEnabled(True)
            self.font_combo.setEnabled(True)
            self.bold_cb.setEnabled(True)
            self.italic_cb.setEnabled(True)
            self.snap_safe_btn.setEnabled(True)

            has_lyrics = bool(self.doc.all_dialogues)
            self.use_first_line_btn.setEnabled(has_lyrics)
            self.next_line_btn.setEnabled(has_lyrics)

            if self.doc.styles:
                self.styles_list.setCurrentRow(0)

            if has_lyrics:
                self.use_first_song_line()
            else:
                self.preview_text.setText("Sample Text  AaBb  123  ♪")

        except Exception as e:
            QMessageBox.critical(self, "Load error", str(e))

    def current_style(self) -> Optional[AssStyle]:
        if not self.doc:
            return None
        idx = self.styles_list.currentRow()
        if idx < 0 or idx >= len(self.doc.styles):
            return None
        return self.doc.styles[idx]

    def on_style_selected(self, row: int):
        st = self.current_style()
        self.preview.set_style(st)
        self.show_current_song_line()

        if not st:
            self.sw_highlight.set_rgba(None)
            self.sw_base.set_rgba(None)
            self.sw_outline.set_rgba(None)
            self.sw_shadow.set_rgba(None)

            self.outline_spin.blockSignals(True)
            self.outline_spin.setValue(0)
            self.outline_spin.blockSignals(False)

            self.shadow_distance.blockSignals(True)
            self.shadow_distance.setValue(0)
            self.shadow_distance.blockSignals(False)

            self.shadow_opacity_spin.blockSignals(True)
            self.shadow_opacity_spin.setValue(0)
            self.shadow_opacity_spin.blockSignals(False)

            self.shadow_opacity_slider.blockSignals(True)
            self.shadow_opacity_slider.setValue(0)
            self.shadow_opacity_slider.blockSignals(False)

            self.font_size_spin.blockSignals(True)
            self.font_size_spin.setValue(0)
            self.font_size_spin.blockSignals(False)

            self.bold_cb.blockSignals(True)
            self.bold_cb.setChecked(False)
            self.bold_cb.blockSignals(False)

            self.italic_cb.blockSignals(True)
            self.italic_cb.setChecked(False)
            self.italic_cb.blockSignals(False)

            self.font_size_spin.setStyleSheet("")
            self.font_size_spin.setToolTip("")
            return

        self.sw_highlight.set_rgba(style_get_color(st, "PrimaryColour"))
        self.sw_base.set_rgba(style_get_color(st, "SecondaryColour"))
        self.sw_outline.set_rgba(style_get_color(st, "OutlineColour"))

        self.outline_spin.blockSignals(True)
        self.outline_spin.setValue(style_get_int(st, "Outline", 0))
        self.outline_spin.blockSignals(False)

        self.shadow_distance.blockSignals(True)
        self.shadow_distance.setValue(style_get_int(st, "Shadow", 0))
        self.shadow_distance.blockSignals(False)

        shadow_rgba = style_get_color(st, "BackColour")
        self.sw_shadow.set_rgba(shadow_rgba)
        if shadow_rgba:
            a = shadow_rgba[3]
            pct = int(round(a * 100 / 255))
            self.shadow_opacity_spin.blockSignals(True)
            self.shadow_opacity_spin.setValue(pct)
            self.shadow_opacity_spin.blockSignals(False)

            self.shadow_opacity_slider.blockSignals(True)
            self.shadow_opacity_slider.setValue(pct)
            self.shadow_opacity_slider.blockSignals(False)
        else:
            self.shadow_opacity_spin.blockSignals(True)
            self.shadow_opacity_spin.setValue(0)
            self.shadow_opacity_spin.blockSignals(False)

            self.shadow_opacity_slider.blockSignals(True)
            self.shadow_opacity_slider.setValue(0)
            self.shadow_opacity_slider.blockSignals(False)

        angle = int(st.fields.get("ChromaAngle", 45))
        self.shadow_angle_picker.angle = angle
        self.shadow_angle_picker.update()
        self.preview.shadow_angle = angle

        is_3d = st.fields.get("Chroma3D", "False") == "True"
        self.shadow_3d_cb.blockSignals(True)
        self.shadow_3d_cb.setChecked(is_3d)
        self.shadow_3d_cb.blockSignals(False)
        self.preview.shadow_3d = is_3d
        self.shadow_steps.setEnabled(is_3d)

        steps = int(st.fields.get("ChromaSteps", 10))
        self.shadow_steps.blockSignals(True)
        self.shadow_steps.setValue(steps)
        self.shadow_steps.blockSignals(False)
        self.preview.shadow_steps = steps

        # Load Typography into UI
        fontname = st.fields.get("Fontname", "Arial")
        fontsize = style_get_int(st, "Fontsize", 48)
        is_bold = style_get_int(st, "Bold", 0) != 0
        is_italic = style_get_int(st, "Italic", 0) != 0

        self.font_combo.blockSignals(True)
        self.font_combo.setCurrentFont(QFont(fontname))
        self.font_combo.blockSignals(False)

        self.font_size_spin.blockSignals(True)
        self.font_size_spin.setValue(fontsize)
        self.font_size_spin.blockSignals(False)

        self.bold_cb.blockSignals(True)
        self.bold_cb.setChecked(is_bold)
        self.bold_cb.blockSignals(False)

        self.italic_cb.blockSignals(True)
        self.italic_cb.setChecked(is_italic)
        self.italic_cb.blockSignals(False)

        self.check_font_boundaries()

    def open_chroma_picker(self):
        if not self.picker:
            self.picker = ChromaPickerWindow(self)
            self.picker.colorTransferred.connect(self.receive_chromapicker_color)

        self.picker.show()
        self.picker.raise_()
        self.picker.activateWindow()

    def receive_chromapicker_color(self, target: str, color: QColor):
        if target == "Background":
            self.preview.set_bg_color(color)
            self.bg_hex.setText(self.format_bg_hex(color))
            return

        st = self.current_style()
        if not st:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("No Style Loaded")
            msg_box.setText("Please load an .ass file first!")
            msg_box.setIcon(QMessageBox.Icon.Warning)

            load_btn = msg_box.addButton(
                "Load an .ass file", QMessageBox.ButtonRole.ActionRole
            )
            cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            msg_box.exec()

            if msg_box.clickedButton() == load_btn:
                self.drop.open_file_dialog()
            return

        current = style_get_color(st, target) or (255, 255, 255, 0)
        alpha = current[3]
        style_set_color(st, target, (color.red(), color.green(), color.blue(), alpha))
        self.save_custom_colors()
        self.on_style_selected(self.styles_list.currentRow())
        self.preview.update()

    # ---- Editing ----

    def pick_color(self, key: str):
        st = self.current_style()
        if not st:
            return

        current = style_get_color(st, key) or (255, 255, 255, 0)
        r, g, b, a = current

        chosen = QColorDialog.getColor(QColor(r, g, b), self, f"Pick {key}")
        if not chosen.isValid():
            return

        self.save_custom_colors()
        style_set_color(st, key, (chosen.red(), chosen.green(), chosen.blue(), a))
        self.on_style_selected(self.styles_list.currentRow())
        self.preview.update()

    def set_shadow_to_black(self):
        st = self.current_style()
        if not st:
            return
        current = style_get_color(st, "BackColour") or (0, 0, 0, 0)
        _, _, _, a = current
        style_set_color(st, "BackColour", (0, 0, 0, a))
        self.on_style_selected(self.styles_list.currentRow())
        self.preview.update()

    def swap_highlight_base(self):
        st = self.current_style()
        if not st:
            return
        prim = style_get_color(st, "PrimaryColour") or (255, 255, 255, 0)
        sec = style_get_color(st, "SecondaryColour") or (255, 255, 0, 0)
        style_set_color(st, "PrimaryColour", sec)
        style_set_color(st, "SecondaryColour", prim)
        self.on_style_selected(self.styles_list.currentRow())
        self.preview.update()

    def show_swap_menu(self, pos):
        menu = QMenu(self)
        swap_action = menu.addAction("🔄 Swap Highlight && Base")
        from PySide6.QtGui import QCursor

        action = menu.exec(QCursor.pos())
        if action == swap_action:
            self.swap_highlight_base()

    def save_file(self):
        if not self.doc or not self.current_path:
            return
        self._do_save(self.current_path)

    def save_as(self):
        if not self.doc or not self.current_path:
            return
        default_out = str(Path(self.current_path).with_suffix("")) + "_edited.ass"
        out_path, _ = QFileDialog.getSaveFileName(
            self, "Save ASS As", default_out, "ASS (*.ass)"
        )
        if out_path:
            self._do_save(out_path)

    def _do_save(self, out_path: str):
        try:
            bg_hex_for_file = self.preview.bg_color.name(
                QColor.NameFormat.HexArgb
            ).upper()
            self.doc.save_as(out_path, bg_color_hex=bg_hex_for_file)
            QMessageBox.information(
                self, "Saved", f"Saved successfully to:\n{out_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Save error", str(e))

    def show_about(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("About ChromaLyric")
        dlg.setModal(True)

        logo = QLabel()
        pix = QPixmap(resource_path("assets/ChromaLyricLogo.png"))
        if not pix.isNull():
            pix = pix.scaled(
                520,
                220,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo.setPixmap(pix)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_lbl = QLabel(
            "Vibe Coded in 2026 by Matt Joy.<br>"
            + '<a href="https://www.youtube.com/@MattJoyKaraoke" style="color: #708090;">youtube.com/@MattJoyKaraoke</a><br>'
            + '<a href="https://github.com/mattjoykaraoke" style="color: #708090;">github.com/mattjoykaraoke</a><br><br>'
            + f"Version {APP_VERSION}.<br>"
            + "Built with Qt / PySide6 (LGPL v3).<br>"
            + "Includes community color names curated by meodai.<br>"
            + "See licenses folder for details."
        )
        text_lbl.setOpenExternalLinks(True)
        text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_lbl.setStyleSheet("font-size: 14px; color: white;")

        ok = QPushButton("OK")
        ok.clicked.connect(dlg.accept)

        lay = QVBoxLayout()
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)
        lay.addWidget(logo)
        lay.addWidget(text_lbl)
        lay.addWidget(ok, alignment=Qt.AlignmentFlag.AlignCenter)

        dlg.setLayout(lay)
        dlg.setStyleSheet(
            "QDialog { background-color: #1E1E1E; } QPushButton { padding: 6px 14px; }"
        )
        dlg.exec()

    # ---- Preview controls ----

    def reset_zoom(self):
        self.zoom_slider.setValue(100)

    def on_zoom_changed(self, v: int):
        self.zoom_lbl.setText(f"Zoom: {v}%")
        effective_scale = BASE_PREVIEW_SCALE * (v / 100.0)
        self.preview.set_preview_scale(effective_scale)

    def on_preview_text_changed(self, text: str):
        self.preview.set_text(text.replace("\\N", "\n"))

        # Don't trigger the global timeline check just because the UI preview text was typed in,
        # since the UI box is just a playground and the overlap engine checks the real ASS data.

    def show_current_song_line(self):
        if not self.doc:
            return
        st = self.current_style()
        text_to_use = None

        if st and st.name in self.doc.dialogues_by_style:
            style_lines = self.doc.dialogues_by_style[st.name]
            if style_lines:
                idx = self.style_line_idx.get(st.name, 0)
                text_to_use = style_lines[idx]

        if not text_to_use and self.doc.all_dialogues:
            text_to_use = self.doc.all_dialogues[0]

        if text_to_use:
            self.preview_text.setText(text_to_use[:200])

    def use_first_song_line(self):
        st = self.current_style()
        if st:
            self.style_line_idx[st.name] = 0
        self.show_current_song_line()

    def next_song_line(self):
        st = self.current_style()
        if st and st.name in self.doc.dialogues_by_style:
            style_lines = self.doc.dialogues_by_style[st.name]
            if style_lines:
                current_idx = self.style_line_idx.get(st.name, 0)
                self.style_line_idx[st.name] = (current_idx + 1) % len(style_lines)
        self.show_current_song_line()

    def pick_bg(self):
        initial = self.preview.bg_color
        chosen = QColorDialog.getColor(initial, self, "Pick preview background")
        if not chosen.isValid():
            return
        self.preview.set_bg_color(chosen)
        self.bg_hex.setText(self.format_bg_hex(chosen))

    def on_bg_hex_changed(self):
        t = self.bg_hex.text().strip()
        if not t.startswith("#"):
            t = "#" + t
        c = QColor(t)
        if not c.isValid():
            QMessageBox.warning(
                self, "Invalid hex", "That hex color couldn't be parsed."
            )
            return
        self.preview.set_bg_color(c)
        self.bg_hex.setText(self.format_bg_hex(c))

    def on_k_changed(self, v: int):
        self.k_lbl.setText(f"K: {v}%")
        self.preview.set_k_progress(v / 100.0)

    def toggle_k_play(self):
        if self.k_timer.isActive():
            self.k_timer.stop()
            self.k_play_btn.setText("▶ Play")
        else:
            if self.k_slider.value() >= 100:
                self.k_slider.setValue(0)
            self.k_timer.start()
            self.k_play_btn.setText("⏸ Stop")

    def on_k_timer_tick(self):
        val = self.k_slider.value()
        if val >= 100:
            self.k_timer.stop()
            self.k_play_btn.setText("▶ Play")
        else:
            self.k_slider.setValue(val + 1)

    # ==========================================
    # ---- THEME LIBRARY LOGIC ----
    # ==========================================

    def get_current_style_colors(self):
        st = self.current_style()
        if not st:
            return None
        return {
            "primary": style_get_color(st, "PrimaryColour") or (255, 255, 255, 0),
            "secondary": style_get_color(st, "SecondaryColour") or (255, 255, 0, 0),
            "outline": style_get_color(st, "OutlineColour") or (0, 0, 0, 0),
            "shadow_color": style_get_color(st, "BackColour") or (0, 0, 0, 0),
            "outline_thick": style_get_int(st, "Outline", 0),
            "shadow_dist": style_get_int(st, "Shadow", 0),
            "shadow_angle": self.shadow_angle_picker.angle,
            "shadow_3d": self.shadow_3d_cb.isChecked(),
            "shadow_steps": self.shadow_steps.value(),
        }

    def load_presets(self):
        self.preset_list.clear()
        saved_data = str(self.settings.value("theme_presets", "[]"))
        try:
            self.presets = json.loads(saved_data)
        except json.JSONDecodeError:
            self.presets = []

        for p in self.presets:
            self.preset_list.addItem(QListWidgetItem(p["name"]))

    def save_presets_to_storage(self):
        self.settings.setValue("theme_presets", json.dumps(self.presets))

    def save_new_preset(self):
        colors = self.get_current_style_colors()
        if not colors:
            QMessageBox.warning(
                self, "No Style", "Please select a style first to save its colors."
            )
            return

        name, ok = QInputDialog.getText(
            self, "Save Preset", "Enter a name for this Theme:"
        )
        if ok and name.strip():
            new_preset = {"name": name.strip(), **colors}
            self.presets.append(new_preset)
            self.preset_list.addItem(QListWidgetItem(name.strip()))
            self.save_presets_to_storage()

    def apply_preset(self, item: QListWidgetItem):
        st = self.current_style()
        if not st:
            return

        row = self.preset_list.row(item)
        preset = self.presets[row]

        style_set_color(st, "PrimaryColour", preset["primary"])
        style_set_color(st, "SecondaryColour", preset["secondary"])
        style_set_color(st, "OutlineColour", preset["outline"])

        if "shadow_color" in preset:
            style_set_color(st, "BackColour", preset["shadow_color"])

        if "outline_thick" in preset:
            st.fields["Outline"] = str(preset["outline_thick"])
        if "shadow_dist" in preset:
            st.fields["Shadow"] = str(preset["shadow_dist"])

        if "shadow_angle" in preset:
            self.shadow_angle_picker.angle = preset["shadow_angle"]
            self.shadow_angle_picker.update()
            self.preview.shadow_angle = preset["shadow_angle"]

        if "shadow_3d" in preset:
            self.shadow_3d_cb.setChecked(preset["shadow_3d"])

        if "shadow_steps" in preset:
            self.shadow_steps.setValue(preset["shadow_steps"])

        self.on_style_selected(self.styles_list.currentRow())
        self.preview.update()

    def show_preset_context_menu(self, pos):
        item = self.preset_list.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        rename_action = menu.addAction("Rename Preset")
        update_action = menu.addAction("Update with Current Colors")
        delete_action = menu.addAction("Delete Preset")

        action = menu.exec(self.preset_list.mapToGlobal(pos))
        row = self.preset_list.row(item)

        if action == rename_action:
            new_name, ok = QInputDialog.getText(
                self, "Rename Preset", "New name:", text=item.text()
            )
            if ok and new_name.strip():
                self.presets[row]["name"] = new_name.strip()
                item.setText(new_name.strip())
                self.save_presets_to_storage()

        elif action == update_action:
            colors = self.get_current_style_colors()
            if colors:
                self.presets[row].update(colors)
                self.save_presets_to_storage()
                QMessageBox.information(
                    self,
                    "Updated",
                    f"'{item.text()}' updated with your current swatches.",
                )

        elif action == delete_action:
            self.presets.pop(row)
            self.preset_list.takeItem(row)
            self.save_presets_to_storage()

    def export_presets(self):
        if not self.presets:
            QMessageBox.information(
                self, "Empty Library", "There are no presets to export."
            )
            return

        out_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Theme Library",
            "ChromaLyric_Themes.json",
            "JSON Files (*.json)",
        )
        if out_path:
            try:
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(self.presets, f, indent=4)
                QMessageBox.information(
                    self, "Success", "Theme Library exported successfully!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Export Error", f"Failed to export themes:\n{str(e)}"
                )

    def import_presets(self):
        in_path, _ = QFileDialog.getOpenFileName(
            self, "Import Theme Library", "", "JSON Files (*.json)"
        )
        if in_path:
            try:
                with open(in_path, "r", encoding="utf-8") as f:
                    imported_data = json.load(f)

                if isinstance(imported_data, list) and all(
                    "name" in item for item in imported_data
                ):
                    self.presets.extend(imported_data)
                    self.save_presets_to_storage()
                    self.load_presets()
                    QMessageBox.information(
                        self, "Success", f"Imported {len(imported_data)} themes!"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Invalid File",
                        "This file does not contain valid ChromaLyric themes.",
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Import Error", f"Failed to import themes:\n{str(e)}"
                )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if any(
                u.isLocalFile() and is_supported_file(u.toLocalFile())
                for u in event.mimeData().urls()
            ):
                event.acceptProposedAction()
                return
            event.ignore()

    def load_custom_colors(self):
        saved_colors = list(self.settings.value("custom_colors", []))
        for i, hex_val in enumerate(saved_colors):
            if i < QColorDialog.customCount():
                QColorDialog.setCustomColor(i, QColor(hex_val))

    def save_custom_colors(self):
        custom_colors = []
        for i in range(QColorDialog.customCount()):
            color = QColorDialog.customColor(i)
            custom_colors.append(color.name())
        self.settings.setValue("custom_colors", custom_colors)

    def dropEvent(self, event):
        for u in event.mimeData().urls():
            if u.isLocalFile() and is_supported_file(u.toLocalFile()):
                self.load_ass(u.toLocalFile())
                event.acceptProposedAction()
                return
        event.ignore()


import winreg


def get_windows_accent_color():
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\DWM")
        value, _ = winreg.QueryValueEx(key, "ColorizationColor")
        r = (value >> 16) & 0xFF
        g = (value >> 8) & 0xFF
        b = value & 0xFF
        return QColor(r, g, b)
    except Exception:
        return QColor(42, 130, 218)


def main():
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QIcon, QPalette

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    accent_color = get_windows_accent_color()

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(18, 18, 18))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Link, accent_color)
    dark_palette.setColor(QPalette.ColorRole.Highlight, accent_color)
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

    app.setPalette(dark_palette)

    app.setApplicationName("ChromaLyric")
    app.setWindowIcon(QIcon(resource_path("assets/ChromaLyric.ico")))
    win = MainWindow()

    if len(sys.argv) > 1:
        path = sys.argv[1]
        if Path(path).exists() and path.lower().endswith(".ass"):
            win.load_ass(path)

    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
