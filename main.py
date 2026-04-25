import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPalette
from PySide6.QtWidgets import QApplication

from core.utils import get_windows_accent_color, resource_path
from ui.main_window import MainWindow

APP_VERSION = "v1.13.0"
BASE_PREVIEW_SCALE = 0.45

def main():
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
    win = MainWindow(app_version=APP_VERSION, base_preview_scale=BASE_PREVIEW_SCALE)

    if len(sys.argv) > 1:
        path = sys.argv[1]
        if Path(path).exists() and path.lower().endswith(".ass"):
            win.load_ass(path)

    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
