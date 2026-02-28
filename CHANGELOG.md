# Changelog

All notable changes to ChromaLyric will be documented in this file.

## [1.9.1] - 2026-02-28

### Added
- **Drag-and-Drop Image Loading**: Skip the file browser entirely. You can now drag `.jpg` or `.png` reference frames directly from your file explorer anywhere into the ChromaPicker window to instantly load them for extraction.

### Changed
- **Smart Error Handling**: Sending a color from the ChromaPicker without an active style no longer throws a dead-end warning. Instead, it gracefully prompts you with a custom menu that lets you instantly browse and load an `.ass` file right from the alert.

## [1.9.0] - 2026-02-27

### Added
- **ChromaPicker (Image Color Extractor)**: A brand-new floating utility to pull perfect color palettes directly from your reference frames (like anime episodes or music videos). Launch it right from the left sidebar!
- **Crosshair Pixel Dropper**: Load any `.jpg` or `.png` and click anywhere on the image to extract the exact RGBA pixel data. Large images automatically scale to fit your screen while retaining 1:1 pixel accuracy.
- **Extracted Palette History**: Every color you click is saved into a running swatch list on the right side of the picker, complete with its exact Hex code.
- **One-Click Quick Transfer**: Instantly route any extracted color to your current style. Use the `H`, `B`, `O`, `S`, or `BG` buttons to instantly push the color to your Highlight, Base, Outline, Shadow, or Preview Background.
- **Live UI Syncing**: Because the ChromaPicker floats over the main application, routing a color instantly updates the main preview window and your custom swatch memory without interrupting your workflow.

## [1.8.1] - 2026-02-27

### Added
- **Full Style Presets**: Theme Library now captures the complete visual identity of a style. In addition to colors, presets now save and restore Outline Thickness, Shadow Distance, and Shadow Transparency.

### Changed
- **Robust Color Parsing**: Implemented "Safe" color collection with hex-based fallbacks to prevent application crashes when interacting with malformed or incomplete .ass style definitions.

## [1.8.0] - 2026-02-24

### Added
- **Theme Library**: Save your perfect Highlight, Base, and Outline color combinations as custom presets. Dial in your style and hit "Save Current" to add it to your persistent library on the left sidebar.
- **Double-Click to Apply**: Instantly snap your current `.ass` style to any saved theme just by double-clicking it in your library.
- **Theme Management Context Menu**: Right-click any preset in your library to **Rename**, **Delete**, or instantly **Update** it with the colors currently active in your swatches.
- **Import & Export Themes**: Click the new gear icon (`⚙`) next to the save button to export your Theme Library as a `.json` file. Back up your favorite styles, move them between computers, or share your custom creator packs with the community!

### Changed
- **Persistent Color Picker Slots**: The 16 "Custom Color" squares at the bottom of the system `QColorDialog` will now remember your saved shades across sessions.
- **Native OS Memory**: Themes and custom colors are now saved natively to your operating system via `QSettings` (Windows Registry), ensuring your library is completely safe and persistent across future ChromaLyric `.exe` updates.

## [1.7.2] - 2026-02-23

### Added
- **Set Shadow to Black Button:** Most people use black shadows but KBS makes it a dark brown for some reason. Why waste time with more than one click to make it black?

## [1.7.1] - 2026-02-23

### Added
- **Global Drag-and-Drop:** You can now drag and drop `.ass` files anywhere inside the application window to instantly load them, removing the need to aim for the corner dropzone.
- **Color Names:** So many color names from the 140 CSS named colors + easter eggs to find.

## [1.7.0] - 2026-02-23

### Added
- **Smart Lyrics Preview:** The preview text now automatically detects and updates to the first lyric of the currently selected style. If the style is unused, it gracefully falls back to the song's opening line.
- **Animated Karaoke Playback:** Added a Play/Stop button to the \k swipe slider, allowing for a smooth real-time preview of the karaoke wipe effect.
- **Clickable Links:** The About box now supports fully clickable HTML links to route directly to YouTube.

### Changed
- **UI Theme:** Implemented the native Qt "Fusion" theme to ensure consistent, clean styling and proper arrow stacking across all operating systems.
- **Shadow Controls:** Swapped the raw ASS alpha math for a highly intuitive "Transparency" slider and spinbox combo that perfectly sync with each other.

### Fixed
- **Layout Alignment:** Removed double-margins on the shadow layout panel to prevent jarring window resizing and ensure perfect alignment with the top boxes.
