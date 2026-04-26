# Changelog

All notable changes to ChromaLyric will be documented in this file.

## [1.14.0] - 2026-04-25

### Added
- **Video Backgrounds:** Added a video background system to the application. It's not a renderer and it doesn't use `FFMPEG` so you can't save the final project with the video, but you can use it to preview your lyrics with the video in the editor for color matching purposes. You can disable the video and go back to color/hex backgrounds anytime.
- **Video Controls:** Added a video scrub and playback controls to the application.

## [1.13.1] - 2026-04-25

### Added
- **CLI Mode:** Added a command-line interface mode to the application.
- **Undo/Redo System:** Added an Undo/Redo system to the application.
- **Project Versioning:** Added a versioning system to the project.
- **Palette Extraction:** Added a palette extraction system to the application.

## [1.13.0] - 2026-04-25

### Added
- **Package Architecture Update:** Broke the monolithic file into relevant parts.

## [1.12.2] - 2026-04-11

### Fixed
- **Smart Collision Prevention:** Changing the collision calculation to use ASS mathmatical rules (all other methods failed) due to custom fonts that do not accurately report their Ascender and Descender values.

## [1.12.1] - 2026-04-11

### Added
- **Smart Collision Prevention:** The `.ass` files converted using `kbputils` have `\pos(x,y)` tags that confused the original logic for alerting you to a bounding box issue. The latest code avoids vertical collisions as well as vertical and horizontal bounding box breaks.

## [1.12.0] - 2026-04-11

### Added
- **New Typography Drawer:** Added a collapsible Typography drawer giving you direct control over Typeface, Font Size, Bold, and Italic formatting without ever opening a text editor. 
- **Size Sync:** Checkbox toggle (default ON) allows adjusting the font size for all styles at once or using the Snap tool to automatically shrink any render that would break the 1080p bounding box (simulated ffmpeg and libass collision logic with `.setPixelSize()` for the calculations and ignores complex extra lines for shadow simulation). The Snap tool does not increase size of the fonts to maximum, you would need to overshoot the maximum and click the tool to snap down to maximum, if that's your style.
- **Typeface Sync:** Checkbox toggle (default OFF) allows for changing the typeface of all styles to the same thing but you can still use different fonts for different styles if you want.
- **Theme Purity:** Font choices and sizes are saved directly to your `.ass` file, but they are strictly isolated from your Theme Presets. Applying a saved color preset from your library will only update your colors and shadows, ensuring your carefully balanced 1080p typography is never accidentally overwritten.

## [1.11.0] - 2026-04-10

### Added
- **Color Update:** Newest (as of 4/1/2026) meodai/color-names library update. Why not?
- **Update to BG Hex Formatting:** The Background UI now intelligently accepts transparency. It displays 6-digit hex codes (#RRGGBB) for solid colors but automatically expands to 8-digit hex codes (#AARRGGBB) if alpha/transparency is detected or manually entered. Not all video formats accept transparency but with `kbputils`, the rules should make sense.
- **kbputils Compatibility:** Added support for the upcoming `; kbputils_background_1.0 color: #AARRBBGG` tag. Anytime you save a `.ass` file the comment will be appended to the file and provide direct background alpha and hex to the program. 
- **Style-Aware Lookup:** The "Use First Line of Lyrics" button now specifically searches for the first line of text tied to the currently selected Style.
- **Next Line Functionality:** Added a "Next Line" button that allows you to cycle through every lyric line associated with your selected style.
- **Direct Save:** Added a "Save" button to the main interface for instant, destructive overwriting of the current `.ass` file for streamling work with `kbp2video` or `Matt Joy Karaoke Creation Suite` (not yet available to public).

## [1.10.5] - 2026-04-01

### Added
- **Update Notifications:** ChromaLyric now silently checks the GitHub repository on startup. If a newer release is detected, users will receive a gentle prompt featuring the new changelog and a direct link to download the latest installer.

## [1.10.4] - 2026-04-01

### Fixed
- **Strict ASS Formatting:** Removed an unintended trailing space after commas when saving modified style lines. ChromaLyric now outputs tightly packed, natively formatted `.ass` definitions (e.g., `Style: Name,Font,Size` instead of `Style: Name, Font, Size`), ensuring perfect 1:1 compatibility with standard Aegisub behavior and third-party subtitle parsers.

## [1.10.3] - 2026-03-30

### Added
- **Color Swapping**: Right click the palette on Highlight or Base to swap them.

## [1.10.2] - 2026-03-15

### Changed
- **Dynamic Resizing**: Vertical space and horizontal space are better managed.
- **Slider Color**: Registry is read for your accent color and applies it (fixed from default blue when I enforced dark mode)

## [1.10.1] - 2026-03-15

### Changed
- **Force Dark Mode**: ChromaLyric looks better in dark mode.

## [1.10.0] - 2026-03-10

### Added
- **Advanced KFX Engine (Pseudo-3D & Angled Shadows)**: ChromaLyric is now a mini-rendering engine! You can now easily generate complex karaoke text effects directly in the UI without needing to write complex ASS override tags by hand. 
- **Interactive Angle Dial**: A new custom radial dial lets you visually set the exact angle (0º-360º) for your drop shadows or 3D extrusions.
- **Pseudo-3D Extrusion Mode**: Check the new 3D box to instantly stack up to 15 mathematical layers of your text, creating a smooth, deep, retro-3D extrusion effect.
- **Non-Destructive Exporting**: When you save, ChromaLyric calculates and injects precise \xshad and \yshad tags into your `.ass` file. We automatically tag these generated background layers with ChromaShadow in the Effect column. If you ever reopen the file in ChromaLyric, it instantly strips the 3D layers out on load, leaving your original lyrics perfectly clean and editable.

### Changed
- **Theme Library Upgrade**: Your custom Theme Library presets now natively support and remember your custom 3D Extrusion, Step count, and Angle settings. Dial in your perfect 3D aesthetic, save it once, and apply it anywhere.
- **FFmpeg & libass Compatibility**: Upgraded the export logic to automatically clean existing, conflicting shadow tags (\shad) from your raw lyrics and elevate the z-index of the primary text. This ensures tools like kbp2video and ffmpeg composite your 3D shadows flawlessly without squashing layers during the video burn process.

## [1.9.2] - 2026-02-28

### Added
- **Massive Color Database**: Integrated the meodai/color-names library, expanding the naming engine to include over 31,000+ community-curated color names.
- **Brand Color Priority**: Established a dedicated "Creator & Brand Colors" section to ensure custom names and easter eggs always take precedence over the community database.
- **Strict Type Safety**: Implemented explicit string casting and type hinting for the Theme Library and Custom Color loaders to ensure 100% reliable data recovery from the Windows Registry.

### Changed
- **PySide6 (Qt6) Migration**: Refactored the entire codebase to be fully compliant with modern PySide6 standards. All UI and rendering logic now utilizes strict Qt6 enum namespaces for better performance and future-proofing.
- **Critical Rendering Collision**: Renamed the internal style variable to ass_style to resolve a conflict with the native QWidget.style() method, preventing potential application crashes during UI redrawing.
- **Linter Cleanup**: Resolved critical errors, including fixed antialiasing flags and proper context menu policies.
- **Redundant Imports**: Removed duplicate typing declarations to improve code readability and execution speed.

## [1.9.1] - 2026-02-28

### Added
- **Drag-and-Drop Image Loading**: Skip the file browser entirely. You can now drag `.jpg` or `.png` reference frames directly from your file explorer anywhere into the ChromaPicker window to instantly load them for extraction.

### Changed
- **Smart Error Handling**: Sending a color from the ChromaPicker without an active style no longer throws a dead-end warning. Instead, it gracefully prompts you with a custom menu that lets you instantly browse and load an `.ass` file right from the alert.
- **ChromaPicker Persistence**: You can now close and open ChromaPicker per session without losing the image and palette data.

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
- **Robust Color Parsing**: Implemented "Safe" color collection with hex-based fallbacks to prevent application crashes when interacting with malformed or incomplete `.ass` style definitions.

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
