import math
from pathlib import Path
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QColor, QImage, QPixmap, QPainter, QPen
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

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
