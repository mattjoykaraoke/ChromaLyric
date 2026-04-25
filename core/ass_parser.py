import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.colors import parse_ass_color, format_ass_color, strip_ass_tags

@dataclass
class AssStyle:
    name: str
    fields: Dict[str, str]

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
                        pos_match = re.search(
                            r"\\pos\(([\d.-]+)\s*,\s*([\d.-]+)\)", txt
                        )
                        pos_data = (
                            (float(pos_match.group(1)), float(pos_match.group(2)))
                            if pos_match
                            else None
                        )

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
                                "pos": pos_data,
                                "raw_text_clean": clean_txt,
                            }
                        )

        return all_dialogues, by_style, parsed_dialogues

    def save_as(self, out_path: str, bg_color_hex: Optional[str] = None) -> None:
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
