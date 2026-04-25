import sys
import winreg
from pathlib import Path
from PySide6.QtGui import QColor

def resource_path(relative: str) -> str:
    """Return an absolute path to a resource, working for dev and PyInstaller builds."""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return str(Path(base) / relative)
    return str(Path(__file__).resolve().parent.parent / relative)

def get_windows_accent_color() -> QColor:
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
