# Changelog

All notable changes to ChromaLyric will be documented in this file.

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
