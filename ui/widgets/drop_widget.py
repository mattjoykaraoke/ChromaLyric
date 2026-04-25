from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog

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
