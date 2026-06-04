from typing import Optional, Tuple
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QSequentialAnimationGroup, QPauseAnimation
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QGraphicsOpacityEffect
from PySide6.QtGui import QGuiApplication

from core.colors import nearest_color_name, ass_alpha_to_qt

class DoubleClickLabel(QLabel):
    doubleClicked = Signal()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)

class SwatchControl(QWidget):
    clicked = Signal()

    def __init__(self, title: str):
        super().__init__()
        self._title = title
        self._rgba: Optional[Tuple[int, int, int, int]] = None
        self._original_text: Optional[str] = None
        self._opacity_effect: Optional[QGraphicsOpacityEffect] = None
        self._anim_group: Optional[QSequentialAnimationGroup] = None

        self.title_lbl = QLabel(title)
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_lbl.setStyleSheet("color: white; font-weight: 800; font-size: 14px;")

        self.swatch_btn = QPushButton("")
        self.swatch_btn.setFixedHeight(52)
        self.swatch_btn.clicked.connect(self.clicked.emit)

        self.name_lbl = DoubleClickLabel("")
        self.name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_lbl.setStyleSheet("color: white; font-weight: 600; font-size: 13px;")
        self.name_lbl.doubleClicked.connect(self._copy_to_clipboard)

        layout = QVBoxLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.swatch_btn)
        layout.addWidget(self.name_lbl)
        self.setLayout(layout)

    def set_rgba(self, rgba: Optional[Tuple[int, int, int, int]]):
        if self._anim_group and self._anim_group.state() == QSequentialAnimationGroup.State.Running:
            self._anim_group.stop()
        self._original_text = None
        if self._opacity_effect:
            self._opacity_effect.setOpacity(1.0)

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

    def _copy_to_clipboard(self):
        if not self._rgba:
            return

        r, g, b, _ = self._rgba
        hexv = f"#{r:02X}{g:02X}{b:02X}"

        clipboard = QGuiApplication.clipboard()
        clipboard.setText(hexv)

        self._show_copied_animation()

    def _show_copied_animation(self):
        if self._original_text is None:
            self._original_text = self.name_lbl.text()

        if self._anim_group and self._anim_group.state() == QSequentialAnimationGroup.State.Running:
            self._anim_group.stop()

        if not self._opacity_effect:
            self._opacity_effect = QGraphicsOpacityEffect(self.name_lbl)
            self.name_lbl.setGraphicsEffect(self._opacity_effect)

        self._opacity_effect.setOpacity(1.0)
        self.name_lbl.setText("Copied!")

        # Animation 1: Keep "Copied!" visible briefly
        pause = QPauseAnimation(500)

        # Animation 2: Fade out the "Copied!" text
        fade_out = QPropertyAnimation(self._opacity_effect, b"opacity")
        fade_out.setDuration(250)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)

        def on_fade_out_finished():
            if self._original_text is not None:
                self.name_lbl.setText(self._original_text)
                self._original_text = None

        fade_out.finished.connect(on_fade_out_finished)

        # Animation 3: Fade in the original text
        fade_in = QPropertyAnimation(self._opacity_effect, b"opacity")
        fade_in.setDuration(250)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)

        self._anim_group = QSequentialAnimationGroup(self)
        self._anim_group.addAnimation(pause)
        self._anim_group.addAnimation(fade_out)
        self._anim_group.addAnimation(fade_in)

        def on_group_finished():
            if self._opacity_effect:
                self._opacity_effect.setOpacity(1.0)

        self._anim_group.finished.connect(on_group_finished)
        self._anim_group.start()

