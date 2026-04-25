from typing import Optional, Tuple
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from core.colors import nearest_color_name, ass_alpha_to_qt

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
