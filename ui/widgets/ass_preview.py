import math
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from core.ass_parser import AssStyle, style_get_color, style_get_int
from core.colors import ass_alpha_to_qt

class AssPreviewWidget(QWidget):
    def __init__(self, base_preview_scale: float = 0.45):
        super().__init__()
        self.setMinimumHeight(200)
        self.setMaximumHeight(600)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding
        )

        self.sample_text = "Sample Text  AaBb  123  ♪"
        self.ass_style: Optional[AssStyle] = None
        self.preview_scale = base_preview_scale
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
