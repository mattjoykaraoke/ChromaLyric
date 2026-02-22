[![Download Latest Release](https://img.shields.io/badge/Download-Windows%20Installer-blue?style=for-the-badge&logo=windows)](https://github.com/mattjoykaraoke/ChromaLyric/releases/latest)
![Platform](https://img.shields.io/badge/platform-Windows-blue)
![Built with Python](https://img.shields.io/badge/Built%20with-Python-3776AB?logo=python&logoColor=white)
![Qt](https://img.shields.io/badge/Qt-PySide6-green)
![Installer](https://img.shields.io/badge/Installer-Inno%20Setup-purple)
![License](https://img.shields.io/badge/license-Proprietary-lightgrey)

🎤 ChromaLyric

ChromaLyric is a desktop tool for previewing and editing ASS (Advanced SubStation Alpha) subtitle style colors with a real-time karaoke visualization.

Built for karaoke creators and subtitle stylists who want fast, accurate color iteration without rendering video.
__________________________________________________________________________________________
✨ What It Does
ChromaLyric focuses on style-level editing inside .ass subtitle files:
• 🎨 Edit PrimaryColour, SecondaryColour, OutlineColour, and BackColour
• 🖥 Live, real-time preview of styles
• 🎶 Always-on karaoke highlight simulation
• 🔎 Adjustable preview zoom
• 🎚 Adjustable karaoke progress swipe
• 🧾 Load and save .ass files directly
• 🖱 Drag & drop support
__________________________________________________________________________________________
🎵 Karaoke Mode (Always Enabled)
ChromaLyric uses a simplified and predictable karaoke preview model:

• SecondaryColour	- Base lyric fill
• PrimaryColour	- Highlight swipe color
• OutlineColour	- Text outline
• BackColour - Preview background

This mirrors common karaoke rendering behavior and makes color iteration intuitive.
__________________________________________________________________________________________
🖥 Accurate Preview Rendering
The preview:
• Uses the exact BackColour with no artificial shading
• Renders outline thickness scaled properly
• Respects typeface, font, bold, italic, underline, strikeout
• Uses pixel-sized scaling relative to a calibrated base preview scale

Zoom control:
• 100% = calibrated baseline (optimized for 1080p-style ASS usage)
• Adjustable from 25% to 250%
__________________________________________________________________________________________
📂 Supported File Type
• .ass (Advanced SubStation Alpha)

ChromaLyric edits only the Styles section of the file.
Dialogue lines are preserved as-is.
__________________________________________________________________________________________
🚫 What It Does NOT Do
• Does not render video
• Does not burn subtitles
• Does not require FFmpeg
• Does not modify dialogue timing
• Does not alter non-style sections

It is strictly a style color editor and visualizer.
__________________________________________________________________________________________
🛠 How It Works Internally

1. Parses the [V4+ Styles] section.
2. Loads the style format definition.
3. Maps each style field dynamically.
4. Allows live modification of:
  • Colors
  • Font name (future release)
  • Font size (future release)
5. Rewrites only the style lines when saving.

No external tools are required.
__________________________________________________________________________________________
📦 Installation
Download the latest installer from the Releases page.

Run the installer and launch ChromaLyric from the Start Menu.
__________________________________________________________________________________________
🧱 Technology
ChromaLyric is built with:
• Python
• Qt / PySide6 (LGPL v3)
• PyInstaller (one-dir distribution)
• Inno Setup (Windows installer)
__________________________________________________________________________________________
📜 Licensing
ChromaLyric itself is proprietary software.
© 2026 Matthew Reifler. All rights reserved.

This application uses Qt / PySide6, licensed under the GNU Lesser General Public License v3 (LGPL-3.0).

Qt source code is available at:
https://code.qt.io/

See the /licenses folder and THIRD_PARTY_NOTICES.txt for details.
__________________________________________________________________________________________
🎯 Intended Audience
• Karaoke video creators who use .ass files as an intemediary to final video production
• Works great for people who use kbp2video in the karaoke creation process
__________________________________________________________________________________________
💡 Design Philosophy
ChromaLyric is intentionally focused and lightweight.

It exists to:
• Make color experimentation fast
• Provide visual confidence before rendering
• Remove friction from karaoke styling workflows
__________________________________________________________________________________________
📸 Screenshot

![ChromaLyric Screenshot](assets/screenshot.png)
