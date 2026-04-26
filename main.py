import sys
import argparse
import random
import json
from pathlib import Path

from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor, QIcon, QPalette, QImage
from PySide6.QtWidgets import QApplication

from core.utils import get_windows_accent_color, resource_path
from core.project import KaraokeProject
from core.ass_parser import style_set_color, style_get_color
from ui.main_window import MainWindow

APP_VERSION = "v1.14.0"
BASE_PREVIEW_SCALE = 0.45

def run_cli_mode(args):
    print(f"ChromaLyric {APP_VERSION} CLI Mode")
    print(f"Loading {args.file}...")
    project = KaraokeProject()
    try:
        project.load(args.file)
    except Exception as e:
        print(f"Error loading ASS file: {e}")
        return

    # Randomize
    if args.randomize:
        print("Applying random colors...")
        for st in project.doc.styles:
            style_set_color(st, "PrimaryColour", (random.randint(0,255), random.randint(0,255), random.randint(0,255), 0))
            style_set_color(st, "SecondaryColour", (random.randint(0,255), random.randint(0,255), random.randint(0,255), 0))
            style_set_color(st, "OutlineColour", (random.randint(0,255), random.randint(0,255), random.randint(0,255), 0))
            style_set_color(st, "BackColour", (random.randint(0,255), random.randint(0,255), random.randint(0,255), 100))

    # Apply Preset
    if args.apply_preset:
        print(f"Applying preset: {args.apply_preset}")
        settings = QSettings("MattJoy", "ChromaLyric")
        saved_data = str(settings.value("theme_presets", "[]"))
        try:
            presets = json.loads(saved_data)
            target = next((p for p in presets if p.get("name", "").lower() == args.apply_preset.lower()), None)
            if target:
                for st in project.doc.styles:
                    style_set_color(st, "PrimaryColour", target["primary"])
                    style_set_color(st, "SecondaryColour", target["secondary"])
                    style_set_color(st, "OutlineColour", target["outline"])
                    if "shadow_color" in target:
                        style_set_color(st, "BackColour", target["shadow_color"])
                    if "outline_thick" in target:
                        st.fields["Outline"] = str(target["outline_thick"])
                    if "shadow_dist" in target:
                        st.fields["Shadow"] = str(target["shadow_dist"])
                    if "shadow_angle" in target:
                        st.fields["ChromaAngle"] = str(target["shadow_angle"])
                    if "shadow_3d" in target:
                        st.fields["Chroma3D"] = "True" if target["shadow_3d"] else "False"
                    if "shadow_steps" in target:
                        st.fields["ChromaSteps"] = str(target["shadow_steps"])
            else:
                print(f"Preset '{args.apply_preset}' not found in library.")
        except Exception as e:
            print(f"Error parsing presets: {e}")

    # Extract Theme
    if args.extract_theme:
        print(f"Extracting theme from {args.extract_theme}...")
        img = QImage(args.extract_theme)
        if not img.isNull():
            img = img.scaled(10, 10)
            colors = []
            for x in range(10):
                for y in range(10):
                    c = img.pixelColor(x, y)
                    r, g, b = c.red(), c.green(), c.blue()
                    if not any((r-er)**2 + (g-eg)**2 + (b-eb)**2 < 4000 for er, eg, eb in colors):
                        colors.append((r, g, b))
            
            if len(colors) >= 2:
                for st in project.doc.styles:
                    style_set_color(st, "PrimaryColour", (*colors[0], 0))
                    style_set_color(st, "SecondaryColour", (*colors[1], 0))
                    if len(colors) >= 3:
                        style_set_color(st, "BackColour", (*colors[2], 0))
        else:
            print("Failed to load image for extraction.")

    # Granular Shadows
    if args.shadow_layers is not None or args.pseudo_3d is not None:
        print("Applying granular shadow settings...")
        for st in project.doc.styles:
            if args.shadow_layers is not None:
                st.fields["ChromaSteps"] = str(max(1, min(15, args.shadow_layers)))
            if args.pseudo_3d is not None:
                st.fields["Chroma3D"] = "True" if args.pseudo_3d else "False"

    if args.bake_3d_shadows:
        print("Baking 3D shadows is implicitly enabled when saving ASS file.")

    # Auto Safe Size
    if args.auto_safe_size:
        print("Running safe size optimization (requires GUI logic)...")
        app = QApplication.instance() or QApplication(sys.argv)
        win = MainWindow(app_version=APP_VERSION, base_preview_scale=BASE_PREVIEW_SCALE)
        win.project = project
        win.snap_to_safe_size()

    out_path = args.out
    if not out_path:
        out_path = str(Path(args.file).with_suffix("")) + "_edited.ass"
    
    project.save(out_path)
    print(f"Saved successfully to: {out_path}")

def main():
    parser = argparse.ArgumentParser(description="ChromaLyric Application")
    parser.add_argument("file", nargs="?", help="Optional ASS file to open")
    parser.add_argument("--cli", action="store_true", help="Run completely headless in CLI mode")
    parser.add_argument("--apply-preset", type=str, help="Name of theme preset to apply")
    parser.add_argument("--auto-safe-size", action="store_true", help="Auto shrink text to fit 1080p")
    parser.add_argument("--extract-theme", type=str, metavar="IMG_PATH", help="Apply colors from an image")
    parser.add_argument("--randomize", action="store_true", help="Randomize all style colors")
    parser.add_argument("--bake-3d-shadows", action="store_true", help="Enable shadow baking")
    parser.add_argument("--shadow-layers", type=int, help="Number of 3D shadow layers (1-15)")
    parser.add_argument("--pseudo-3d", type=lambda x: (str(x).lower() in ['true', '1', 'yes']), help="Enable Pseudo-3D effect (true/false)")
    parser.add_argument("--out", type=str, help="Output file path")

    args, unknown = parser.parse_known_args()

    app = QApplication(sys.argv)
    
    if args.cli:
        if not args.file:
            print("ERROR: Must provide an ASS file in --cli mode.")
            sys.exit(1)
        run_cli_mode(args)
        return

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

    if args.file and Path(args.file).exists() and args.file.lower().endswith(".ass"):
        win.load_ass(args.file)

    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
