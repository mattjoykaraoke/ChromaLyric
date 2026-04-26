import json
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QSettings, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QFont, QIcon, QPixmap, QCursor, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QDialog,
    QFileDialog,
    QFontComboBox,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from core.ass_parser import AssDoc, AssStyle, style_get_color, style_get_int, style_set_color
from core.colors import nearest_color_name
from core.utils import resource_path
from core.project import KaraokeProject
from ui.widgets.ass_preview import AssPreviewWidget
from ui.widgets.color_picker import ChromaPickerWindow
from ui.widgets.drop_widget import DropWidget, is_supported_file
from ui.widgets.swatch import SwatchControl
from workers.github import GitHubUpdateWorker

class MainWindow(QMainWindow):
    def __init__(self, app_version: str, base_preview_scale: float):
        super().__init__()
        self.setWindowTitle("ChromaLyric")
        self.resize(1220, 780)
        self.setAcceptDrops(True)

        self.project = KaraokeProject()
        self.style_line_idx: Dict[str, int] = {}

        self.picker = None
        self.CURRENT_VERSION = app_version
        self.settings = QSettings("MattJoy", "ChromaLyric")
        self.base_preview_scale = base_preview_scale

        self.check_for_updates()

        # Shortcuts
        self.undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, self)
        self.undo_shortcut.activated.connect(self.undo)
        self.redo_shortcut = QShortcut(QKeySequence.StandardKey.Redo, self)
        self.redo_shortcut.activated.connect(self.redo)

        # Left Column
        self.drop = DropWidget()
        self.drop.fileDropped.connect(self.load_ass)

        self.styles_list = QListWidget()
        self.styles_list.currentRowChanged.connect(self.on_style_selected)
        self.styles_list.setStyleSheet("font-size: 14px;")

        self.about_btn = QPushButton("About")
        self.about_btn.clicked.connect(self.show_about)

        left = QVBoxLayout()
        left.addWidget(self.drop)

        self.styles_group = QGroupBox("Styles")
        styles_layout = QVBoxLayout()
        styles_layout.addWidget(self.styles_list)
        self.styles_group.setLayout(styles_layout)

        left.addWidget(self.styles_group)

        self.preset_group = QGroupBox("Theme Library")
        preset_layout = QVBoxLayout()

        self.preset_list = QListWidget()
        self.preset_list.setStyleSheet("font-size: 14px;")
        self.preset_list.itemDoubleClicked.connect(self.apply_preset)

        self.preset_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.preset_list.customContextMenuRequested.connect(
            self.show_preset_context_menu
        )

        self.save_preset_btn = QPushButton("💾 Save Current")
        self.save_preset_btn.clicked.connect(self.save_new_preset)

        self.lib_options_btn = QPushButton("⚙")
        self.lib_options_btn.setFixedWidth(36)

        self.lib_menu = QMenu(self)
        self.lib_menu.addAction("Export Library...").triggered.connect(
            self.export_presets
        )
        self.lib_menu.addAction("Import Library...").triggered.connect(
            self.import_presets
        )
        self.lib_options_btn.setMenu(self.lib_menu)

        lib_btn_row = QHBoxLayout()
        lib_btn_row.addWidget(self.save_preset_btn)
        lib_btn_row.addWidget(self.lib_options_btn)

        preset_layout.addWidget(self.preset_list)
        preset_layout.addLayout(lib_btn_row)
        self.preset_group.setLayout(preset_layout)

        left.addWidget(self.preset_group)

        self.chroma_picker_btn = QPushButton("👁 ChromaPicker")
        self.chroma_picker_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 8px;
                font-weight: bold;
                background-color: #2D2D30;
                border: 1px solid #555;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #3E3E42; }
        """)
        self.chroma_picker_btn.clicked.connect(self.open_chroma_picker)
        left.addWidget(self.chroma_picker_btn)

        self.presets = []
        self.load_presets()
        self.load_custom_colors()

        left.addStretch(1)
        left.addWidget(self.about_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        left_wrap = QWidget()
        left_wrap.setLayout(left)

        # Right Column
        self.info = QLabel("Open an .ass file to begin.")
        self.info.setWordWrap(True)

        self.preview = AssPreviewWidget(base_preview_scale=self.base_preview_scale)

        self.preview_text = QLineEdit()
        self.preview_text.setPlaceholderText(
            r"Preview text… (you can use \N for new lines)"
        )
        self.preview_text.textChanged.connect(self.on_preview_text_changed)

        self.use_first_line_btn = QPushButton("Use First Line of Lyrics")
        self.use_first_line_btn.clicked.connect(self.use_first_song_line)
        self.use_first_line_btn.setEnabled(False)

        self.next_line_btn = QPushButton("Next Line")
        self.next_line_btn.clicked.connect(self.next_song_line)
        self.next_line_btn.setEnabled(False)

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(25)
        self.zoom_slider.setMaximum(250)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)

        self.zoom_lbl = QLabel("Zoom: 100%")
        self.zoom_lbl.setMinimumWidth(90)

        self.reset_zoom_btn = QPushButton("Reset Zoom")
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)

        self.bg_hex = QLineEdit("#1E1E1E")
        self.bg_hex.setMaximumWidth(100)
        self.bg_hex.editingFinished.connect(self.on_bg_hex_changed)

        self.bg_pick_btn = QPushButton("Pick BG…")
        self.bg_pick_btn.clicked.connect(self.pick_bg)

        self.k_slider = QSlider(Qt.Orientation.Horizontal)
        self.k_slider.setMinimum(0)
        self.k_slider.setMaximum(100)
        self.k_slider.setValue(35)
        self.k_slider.valueChanged.connect(self.on_k_changed)

        self.k_lbl = QLabel("K: 35%")
        self.k_lbl.setMinimumWidth(70)

        self.k_play_btn = QPushButton("▶ Play")
        self.k_play_btn.clicked.connect(self.toggle_k_play)

        self.k_timer = QTimer(self)
        self.k_timer.setInterval(20)
        self.k_timer.timeout.connect(self.on_k_timer_tick)

        ctrl_row1 = QHBoxLayout()
        ctrl_row1.addWidget(QLabel("Text:"))
        ctrl_row1.addWidget(self.preview_text, 1)
        ctrl_row1.addWidget(self.use_first_line_btn)
        ctrl_row1.addWidget(self.next_line_btn)

        ctrl_row2 = QHBoxLayout()
        ctrl_row2.addWidget(self.zoom_lbl)
        ctrl_row2.addWidget(self.zoom_slider, 1)
        ctrl_row2.addWidget(self.reset_zoom_btn)
        ctrl_row2.addSpacing(10)
        ctrl_row2.addWidget(QLabel("BG:"))
        ctrl_row2.addWidget(self.bg_hex)
        ctrl_row2.addWidget(self.bg_pick_btn)

        ctrl_row3 = QHBoxLayout()
        ctrl_row3.addWidget(QLabel(r"\k swipe:"))
        ctrl_row3.addWidget(self.k_play_btn)
        ctrl_row3.addWidget(self.k_lbl)
        ctrl_row3.addWidget(self.k_slider, 1)

        # Media Player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoSink(self.preview.video_sink)
        self.video_duration = 0

        self.load_vid_btn = QPushButton("Load Video…")
        self.load_vid_btn.clicked.connect(self.load_video)

        self.play_vid_btn = QPushButton("▶")
        self.play_vid_btn.setFixedWidth(30)
        self.play_vid_btn.setEnabled(False)
        self.play_vid_btn.clicked.connect(self.toggle_video_playback)

        self.vid_scrub = QSlider(Qt.Orientation.Horizontal)
        self.vid_scrub.setEnabled(False)
        self.vid_scrub.sliderMoved.connect(self.scrub_video)

        self.mute_vid_btn = QPushButton("🔊")
        self.mute_vid_btn.setFixedWidth(30)
        self.mute_vid_btn.setEnabled(False)
        self.mute_vid_btn.clicked.connect(self.toggle_video_mute)

        self.disable_vid_btn = QPushButton("✖")
        self.disable_vid_btn.setFixedWidth(30)
        self.disable_vid_btn.setToolTip("Remove Video Background")
        self.disable_vid_btn.setEnabled(False)
        self.disable_vid_btn.clicked.connect(self.disable_video)

        self.media_player.positionChanged.connect(self.on_video_position_changed)
        self.media_player.durationChanged.connect(self.on_video_duration_changed)

        ctrl_row_vid = QHBoxLayout()
        ctrl_row_vid.addWidget(QLabel("Video:"))
        ctrl_row_vid.addWidget(self.load_vid_btn)
        ctrl_row_vid.addWidget(self.play_vid_btn)
        ctrl_row_vid.addWidget(self.vid_scrub, 1)
        ctrl_row_vid.addWidget(self.mute_vid_btn)
        ctrl_row_vid.addWidget(self.disable_vid_btn)

        preview_box = QGroupBox("Preview")
        pv_layout = QVBoxLayout()
        pv_layout.addLayout(ctrl_row1)
        pv_layout.addLayout(ctrl_row2)
        pv_layout.addLayout(ctrl_row_vid)
        pv_layout.addLayout(ctrl_row3)
        pv_layout.addWidget(self.preview)
        preview_box.setLayout(pv_layout)

        # Style Colors
        self.sw_highlight = SwatchControl("Highlight (PrimaryColour)")
        self.sw_base = SwatchControl("Base (SecondaryColour)")
        self.sw_outline = SwatchControl("Outline (OutlineColour)")

        self.sw_highlight.clicked.connect(lambda: self.pick_color("PrimaryColour"))
        self.sw_base.clicked.connect(lambda: self.pick_color("SecondaryColour"))
        self.sw_outline.clicked.connect(lambda: self.pick_color("OutlineColour"))

        self.sw_highlight.swatch_btn.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.sw_base.swatch_btn.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.sw_highlight.swatch_btn.customContextMenuRequested.connect(
            self.show_swap_menu
        )
        self.sw_base.swatch_btn.customContextMenuRequested.connect(self.show_swap_menu)

        self.outline_spin = QSpinBox()
        self.outline_spin.setRange(0, 20)
        self.outline_spin.setSingleStep(1)
        self.outline_spin.setFixedWidth(60)
        self.outline_spin.editingFinished.connect(self.on_outline_changed)

        colors_box = QGroupBox("Style Colors")
        colors_layout = QHBoxLayout()
        colors_layout.addWidget(self.sw_highlight)
        colors_layout.addWidget(self.sw_base)

        outline_row = QHBoxLayout()
        outline_row.setContentsMargins(0, 0, 0, 0)
        outline_row.setSpacing(8)
        outline_row.addWidget(self.sw_outline)
        outline_row.addWidget(
            self.outline_spin, alignment=Qt.AlignmentFlag.AlignVCenter
        )
        outline_container = QWidget()
        outline_container.setLayout(outline_row)

        colors_layout.addWidget(outline_container)
        colors_box.setLayout(colors_layout)

        # ---- NEW: Typography Controls ----
        self.typography_group = QGroupBox("Typography")
        self.typography_group.setCheckable(True)
        self.typography_group.setChecked(False)
        self.typography_group.toggled.connect(self.on_typography_group_toggled)

        self.typography_body = QWidget()
        typo_body_layout = QVBoxLayout()
        typo_body_layout.setContentsMargins(0, 0, 0, 0)
        typo_body_layout.setSpacing(6)

        # Typeface Row
        tf_row = QHBoxLayout()
        tf_row.addWidget(QLabel("Typeface:"))
        self.font_combo = QFontComboBox()
        self.font_combo.activated.connect(self.on_font_name_changed)
        tf_row.addWidget(self.font_combo, 1)

        self.sync_typefaces_cb = QCheckBox("Sync All Styles")
        self.sync_typefaces_cb.setChecked(False)
        self.sync_typefaces_cb.toggled.connect(self.on_sync_typefaces_toggled)
        tf_row.addWidget(self.sync_typefaces_cb)

        # Size Row
        sz_row = QHBoxLayout()
        sz_row.addWidget(QLabel("Size (pt):"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(1, 400)
        self.font_size_spin.editingFinished.connect(self.on_font_size_changed)
        sz_row.addWidget(self.font_size_spin)

        self.sync_sizes_cb = QCheckBox("Sync All Styles")
        self.sync_sizes_cb.setChecked(True)
        sz_row.addWidget(self.sync_sizes_cb)
        sz_row.addStretch(1)

        # Format & Safety Row
        fmt_row = QHBoxLayout()
        self.bold_cb = QCheckBox("Bold")
        self.bold_cb.toggled.connect(self.on_font_format_changed)
        self.italic_cb = QCheckBox("Italic")
        self.italic_cb.toggled.connect(self.on_font_format_changed)

        self.snap_safe_btn = QPushButton("🛡️ Snap to 100%")
        self.snap_safe_btn.setToolTip(
            "Shrink font size until all stacked overlapping lyrics fit perfectly inside a 1080p boundary."
        )
        self.snap_safe_btn.clicked.connect(self.snap_to_safe_size)

        fmt_row.addWidget(self.bold_cb)
        fmt_row.addWidget(self.italic_cb)
        fmt_row.addStretch(1)
        fmt_row.addWidget(self.snap_safe_btn)

        typo_body_layout.addLayout(tf_row)
        typo_body_layout.addLayout(sz_row)
        typo_body_layout.addLayout(fmt_row)

        self.typography_body.setLayout(typo_body_layout)
        self.typography_body.setVisible(False)

        typo_group_layout = QVBoxLayout()
        typo_group_layout.setContentsMargins(8, 8, 8, 8)
        typo_group_layout.addWidget(self.typography_body)
        self.typography_group.setLayout(typo_group_layout)

        # Shadow Controls
        self.shadow_group = QGroupBox("Shadow")
        self.shadow_group.setCheckable(True)
        self.shadow_group.setChecked(False)
        self.shadow_group.toggled.connect(self.on_shadow_group_toggled)

        self.shadow_distance = QSpinBox()
        self.shadow_distance.setRange(0, 20)
        self.shadow_distance.setSingleStep(1)
        self.shadow_distance.setFixedWidth(60)
        self.shadow_distance.editingFinished.connect(self.on_shadow_distance_changed)

        self.shadow_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.shadow_opacity_slider.setRange(0, 100)

        self.shadow_opacity_spin = QSpinBox()
        self.shadow_opacity_spin.setRange(0, 100)
        self.shadow_opacity_spin.setSuffix("%")
        self.shadow_opacity_spin.setFixedWidth(60)

        self.shadow_opacity_slider.valueChanged.connect(
            self.shadow_opacity_spin.setValue
        )
        self.shadow_opacity_spin.valueChanged.connect(
            self.shadow_opacity_slider.setValue
        )
        # Only commit change on release
        self.shadow_opacity_slider.sliderReleased.connect(self.on_shadow_opacity_changed)
        self.shadow_opacity_spin.editingFinished.connect(self.on_shadow_opacity_changed)

        # Update preview while sliding
        self.shadow_opacity_slider.valueChanged.connect(self.preview_shadow_opacity)

        self.sw_shadow = SwatchControl("Shadow (BackColour)")
        self.sw_shadow.clicked.connect(lambda: self.pick_color("BackColour"))

        self.shadow_body = QWidget()
        shadow_body_layout = QVBoxLayout()
        shadow_body_layout.setContentsMargins(0, 0, 0, 0)
        shadow_body_layout.setSpacing(6)

        from ui.widgets.color_picker import AnglePicker
        self.shadow_angle_picker = AnglePicker()
        self.shadow_angle_picker.angleChanged.connect(self.on_shadow_angle_changed)

        self.shadow_3d_cb = QCheckBox("Pseudo-3D Extrusion")
        self.shadow_3d_cb.toggled.connect(self.on_shadow_3d_toggled)

        self.shadow_steps = QSpinBox()
        self.shadow_steps.setRange(1, 15)
        self.shadow_steps.setValue(10)
        self.shadow_steps.setSuffix(" layers")
        self.shadow_steps.setFixedWidth(80)
        self.shadow_steps.setEnabled(False)
        self.shadow_steps.editingFinished.connect(self.on_shadow_steps_changed)

        row1 = QHBoxLayout()
        row1.addWidget(self.shadow_angle_picker)

        dist_3d_col = QVBoxLayout()
        dist_row = QHBoxLayout()
        dist_row.addWidget(QLabel("Distance/Depth:"))
        dist_row.addWidget(self.shadow_distance)
        dist_row.addStretch(1)

        step_row = QHBoxLayout()
        step_row.addWidget(self.shadow_3d_cb)
        step_row.addWidget(self.shadow_steps)
        step_row.addStretch(1)

        dist_3d_col.addLayout(dist_row)
        dist_3d_col.addLayout(step_row)

        row1.addLayout(dist_3d_col)
        row1.addStretch(1)
        shadow_body_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Transparency"))
        row2.addWidget(self.shadow_opacity_slider)
        row2.addWidget(self.shadow_opacity_spin)
        shadow_body_layout.addLayout(row2)

        self.quick_black_btn = QPushButton("⬛ Set Black")
        self.quick_black_btn.setToolTip("Instantly set shadow color to pure black")
        self.quick_black_btn.setMaximumWidth(90)
        self.quick_black_btn.clicked.connect(self.set_shadow_to_black)

        shadow_row3 = QHBoxLayout()
        shadow_row3.addWidget(self.sw_shadow)
        shadow_row3.addWidget(
            self.quick_black_btn, alignment=Qt.AlignmentFlag.AlignVCenter
        )
        shadow_body_layout.addLayout(shadow_row3)

        self.shadow_body.setLayout(shadow_body_layout)
        self.shadow_body.setVisible(False)

        self.shadow_distance.setEnabled(False)
        self.shadow_opacity_slider.setEnabled(False)
        self.shadow_opacity_spin.setEnabled(False)
        self.sw_shadow.setEnabled(False)
        self.quick_black_btn.setEnabled(False)

        shadow_group_layout = QVBoxLayout()
        shadow_group_layout.setContentsMargins(8, 8, 8, 8)
        shadow_group_layout.addWidget(self.shadow_body)
        self.shadow_group.setLayout(shadow_group_layout)

        # Save Controls
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_file)
        self.save_btn.setEnabled(False)

        self.save_as_btn = QPushButton("Save As…")
        self.save_as_btn.clicked.connect(self.save_as)
        self.save_as_btn.setEnabled(False)

        save_layout = QHBoxLayout()
        save_layout.addStretch(1)
        save_layout.addWidget(self.save_btn)
        save_layout.addWidget(self.save_as_btn)

        right = QVBoxLayout()
        right.addWidget(self.info)
        right.addWidget(preview_box, stretch=4)
        right.addWidget(colors_box, stretch=0)
        right.addWidget(self.typography_group, stretch=0)
        right.addWidget(self.shadow_group, stretch=0)
        right.addStretch(1)
        right.addLayout(save_layout)

        right_wrap = QWidget()
        right_wrap.setLayout(right)

        root = QWidget()
        root_layout = QHBoxLayout()
        root_layout.addWidget(left_wrap, 2)
        root_layout.addWidget(right_wrap, 5)
        root.setLayout(root_layout)
        self.setCentralWidget(root)

        self.setStyleSheet("""
            QLabel { color: white; }
            QGroupBox { color: white; }
        """)

        self.preview.set_bg_color(QColor(0x1E, 0x1E, 0x1E))
        self.preview.set_k_progress(self.k_slider.value() / 100.0)
        self.on_zoom_changed(self.zoom_slider.value())

        # Disabled state for Typography components until file load
        self.font_size_spin.setEnabled(False)
        self.font_combo.setEnabled(False)
        self.bold_cb.setEnabled(False)
        self.italic_cb.setEnabled(False)
        self.snap_safe_btn.setEnabled(False)

    def undo(self):
        if self.project.undo():
            self._refresh_ui_after_state_change()

    def redo(self):
        if self.project.redo():
            self._refresh_ui_after_state_change()

    def _refresh_ui_after_state_change(self):
        # Full UI refresh to match new state
        if self.project.doc and self.project.doc.bg_color:
            c = QColor(self.project.doc.bg_color)
            if c.isValid():
                self.preview.set_bg_color(c)
                self.bg_hex.setText(self.format_bg_hex(c))
        
        # update current style selection panel
        idx = self.styles_list.currentRow()
        if idx >= 0:
            self.on_style_selected(idx)

    # ---- Format Helper for Background Hex ----
    def format_bg_hex(self, c: QColor) -> str:
        if c.alpha() == 255:
            return c.name(QColor.NameFormat.HexRgb).upper()
        return c.name(QColor.NameFormat.HexArgb).upper()

    # ---- Video Player Logic ----
    def load_video(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi *.mkv *.mov)")
        if path:
            self.media_player.setSource(QUrl.fromLocalFile(path))
            self.preview.set_video_enabled(True)
            self.play_vid_btn.setEnabled(True)
            self.vid_scrub.setEnabled(True)
            self.mute_vid_btn.setEnabled(True)
            self.disable_vid_btn.setEnabled(True)
            self.media_player.play()
            self.play_vid_btn.setText("⏸")

    def toggle_video_playback(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_vid_btn.setText("▶")
        else:
            self.media_player.play()
            self.play_vid_btn.setText("⏸")

    def toggle_video_mute(self):
        muted = not self.audio_output.isMuted()
        self.audio_output.setMuted(muted)
        self.mute_vid_btn.setText("🔇" if muted else "🔊")

    def disable_video(self):
        self.media_player.stop()
        self.media_player.setSource(QUrl())
        self.preview.set_video_enabled(False)
        self.play_vid_btn.setEnabled(False)
        self.play_vid_btn.setText("▶")
        self.vid_scrub.setEnabled(False)
        self.vid_scrub.setValue(0)
        self.mute_vid_btn.setEnabled(False)
        self.disable_vid_btn.setEnabled(False)

    def on_video_duration_changed(self, duration: int):
        self.video_duration = duration
        self.vid_scrub.setRange(0, duration)

    def on_video_position_changed(self, position: int):
        if not self.vid_scrub.isSliderDown():
            self.vid_scrub.setValue(position)

    def scrub_video(self, position: int):
        self.media_player.setPosition(position)

    # ---- Update Checker Logic ----

    def check_for_updates(self):
        self.update_worker = GitHubUpdateWorker()
        self.update_worker.update_available.connect(self.prompt_update)
        self.update_worker.start()

    def prompt_update(self, latest_version: str, release_notes: str, url: str):
        if latest_version and latest_version > self.CURRENT_VERSION:
            reply = QMessageBox.question(
                self,
                "Update Available",
                f"A new version of ChromaLyric ({latest_version}) is available!\n\n"
                f"You are currently running {self.CURRENT_VERSION}.\n\n"
                "Would you like to open the download page?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl(url))

    # ---- Typography Editing ----

    def _check_timeline_safety(
        self, size: int, fontname: str, bold: bool, italic: bool
    ) -> tuple[bool, str]:
        from PySide6.QtGui import QFontMetrics
        from core.ass_parser import strip_ass_tags

        current_st = self.current_style()
        if not current_st:
            return True, ""

        sync_sz = self.sync_sizes_cb.isChecked()
        sync_tf = self.sync_typefaces_cb.isChecked()

        style_metrics = {}
        style_alignments = {}
        style_padding = {}
        style_scalex = {}
        style_scaley = {}
        style_sizes = {}

        for st in self.project.doc.styles:
            sz = (
                size
                if (st.name == current_st.name or sync_sz)
                else style_get_int(st, "Fontsize", 48)
            )
            fname = (
                fontname
                if (st.name == current_st.name or sync_tf)
                else st.fields.get("Fontname", "Arial")
            )
            is_b = (
                bold
                if st.name == current_st.name
                else (style_get_int(st, "Bold", 0) != 0)
            )
            is_i = (
                italic
                if st.name == current_st.name
                else (style_get_int(st, "Italic", 0) != 0)
            )

            font = QFont(fname)
            font.setPixelSize(max(1, sz))
            font.setBold(is_b)
            font.setItalic(is_i)

            style_metrics[st.name] = QFontMetrics(font)
            style_alignments[st.name] = style_get_int(st, "Alignment", 2)
            style_padding[st.name] = style_get_int(st, "Outline", 0) + style_get_int(
                st, "Shadow", 0
            )
            style_scalex[st.name] = style_get_int(st, "ScaleX", 100) / 100.0
            style_scaley[st.name] = style_get_int(st, "ScaleY", 100) / 100.0
            style_sizes[st.name] = sz

        events = []
        for i, diag in enumerate(self.project.doc.parsed_dialogues):
            events.append((diag["start"], "start", i))
            events.append((diag["end"], "end", i))

        events.sort(key=lambda x: (x[0], x[1] == "start"))

        active_diags = set()

        for time, ev_type, idx in events:
            if ev_type == "start":
                active_diags.add(idx)
            else:
                active_diags.discard(idx)

            if ev_type == "start":
                rects = []
                align_groups = {}

                for active_idx in active_diags:
                    d = self.project.doc.parsed_dialogues[active_idx]
                    metrics = style_metrics.get(d["style"])
                    if not metrics:
                        continue

                    align = style_alignments.get(d["style"], 2)
                    padding = style_padding.get(d["style"], 0)
                    sx = style_scalex.get(d["style"], 1.0)
                    sy = style_scaley.get(d["style"], 1.0)
                    sz = style_sizes.get(d["style"], 48)

                    h = sz * sy * len(d["lines"])

                    w = 0
                    for l in d["lines"]:
                        clean_l = strip_ass_tags(l)
                        if clean_l.strip():
                            w = max(w, metrics.horizontalAdvance(clean_l) * sx)

                    if d["pos"]:
                        ax, ay = d["pos"]

                        if align in (1, 4, 7):
                            L, R = ax, ax + w
                        elif align in (3, 6, 9):
                            L, R = ax - w, ax
                        else:
                            L, R = ax - w / 2.0, ax + w / 2.0

                        if align in (7, 8, 9):
                            T, B = ay, ay + h
                        elif align in (4, 5, 6):
                            T, B = ay - h / 2.0, ay + h / 2.0
                        else:
                            T, B = ay - h, ay

                        L -= padding
                        R += padding
                        T -= padding
                        B += padding

                        if L < 0 or R > 1920 or T < 0 or B > 1080:
                            return (
                                False,
                                "Lyric bleeds off screen edge! (Exceeds 1920x1080)",
                            )

                        rect_key = (d["raw_text_clean"], ax, ay)
                        rects.append((rect_key, L, T, R, B))
                    else:
                        align_groups.setdefault(align, []).append(
                            (d["raw_text_clean"], w + padding * 2, h + padding * 2)
                        )

                unique_rects = []
                seen_keys = set()
                for r in rects:
                    if r[0] not in seen_keys:
                        seen_keys.add(r[0])
                        unique_rects.append(r)

                for i in range(len(unique_rects)):
                    for j in range(i + 1, len(unique_rects)):
                        _, L1, T1, R1, B1 = unique_rects[i]
                        _, L2, T2, R2, B2 = unique_rects[j]
                        if L1 < R2 - 1 and R1 > L2 + 1 and T1 < B2 - 1 and B1 > T2 + 1:
                            return (
                                False,
                                "Overlapping lyrics detected! (Crash collision)",
                            )

                for align, group in align_groups.items():
                    unique_stacked = {}
                    for txt, gw, gh in group:
                        if txt not in unique_stacked:
                            unique_stacked[txt] = (gw, gh)

                    total_w, total_h = 0, 0
                    for gw, gh in unique_stacked.values():
                        total_w = max(total_w, gw)
                        total_h += gh

                    if total_w > 1920 or total_h > 1080:
                        return False, "Stacked lyrics exceed screen boundary!"

        return True, "Font Size (pt)"

    def on_typography_group_toggled(self, checked: bool):
        self.typography_body.setVisible(checked)

    def check_font_boundaries(self):
        if not self.project.doc or not self.project.doc.parsed_dialogues:
            return

        ui_fontname = self.font_combo.currentText()
        ui_fontsize = self.font_size_spin.value()
        ui_bold = self.bold_cb.isChecked()
        ui_italic = self.italic_cb.isChecked()

        is_safe, msg = self._check_timeline_safety(
            ui_fontsize, ui_fontname, ui_bold, ui_italic
        )

        if not is_safe:
            self.font_size_spin.setStyleSheet(
                "QSpinBox { background-color: #8B0000; color: white; }"
            )
            self.font_size_spin.setToolTip(msg)
        else:
            self.font_size_spin.setStyleSheet("")
            self.font_size_spin.setToolTip("Font Size (pt)")

    def on_font_name_changed(self, idx: int):
        st = self.current_style()
        if not st:
            return
        fontname = self.font_combo.currentText()
        if self.sync_typefaces_cb.isChecked():
            for s in self.project.doc.styles:
                s.fields["Fontname"] = fontname
        else:
            st.fields["Fontname"] = fontname

        self.project.commit_change()
        self.check_font_boundaries()
        self.preview.update()

    def on_sync_typefaces_toggled(self, checked: bool):
        if checked:
            current_font_text = self.font_combo.currentText()
            reply = QMessageBox.question(
                self,
                "Synchronize Typefaces",
                f"Synchronize all typefaces to {current_font_text}?\nThis will overwrite the font choices for all other styles in the project.",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Ok:
                for s in self.project.doc.styles:
                    s.fields["Fontname"] = current_font_text
                self.project.commit_change()
                self.check_font_boundaries()
                self.preview.update()
            else:
                self.sync_typefaces_cb.blockSignals(True)
                self.sync_typefaces_cb.setChecked(False)
                self.sync_typefaces_cb.blockSignals(False)

    def on_font_size_changed(self):
        st = self.current_style()
        if not st:
            return
        size = self.font_size_spin.value()
        if self.sync_sizes_cb.isChecked():
            for s in self.project.doc.styles:
                s.fields["Fontsize"] = str(size)
        else:
            st.fields["Fontsize"] = str(size)

        self.project.commit_change()
        self.check_font_boundaries()
        self.preview.update()

    def on_font_format_changed(self, checked: bool):
        st = self.current_style()
        if not st:
            return

        b_val = "-1" if self.bold_cb.isChecked() else "0"
        i_val = "-1" if self.italic_cb.isChecked() else "0"

        st.fields["Bold"] = b_val
        st.fields["Italic"] = i_val

        self.project.commit_change()
        self.check_font_boundaries()
        self.preview.update()

    def snap_to_safe_size(self):
        if not self.project.doc or not self.project.doc.parsed_dialogues:
            return

        ui_fontname = self.font_combo.currentText()
        ui_bold = self.bold_cb.isChecked()
        ui_italic = self.italic_cb.isChecked()
        size = self.font_size_spin.value()

        while size > 1:
            is_safe, _ = self._check_timeline_safety(
                size, ui_fontname, ui_bold, ui_italic
            )
            if is_safe:
                break
            size -= 1

        self.font_size_spin.setValue(size)
        self.on_font_size_changed() # this will commit_change

    # ---- Outline / Shadow editing ----

    def on_outline_changed(self):
        st = self.current_style()
        if not st:
            return
        value = self.outline_spin.value()
        st.fields["Outline"] = str(value)
        self.project.commit_change()
        self.preview.update()

    def on_shadow_group_toggled(self, checked: bool):
        self.shadow_body.setVisible(checked)
        self.shadow_distance.setEnabled(checked)
        self.shadow_opacity_slider.setEnabled(checked)
        self.shadow_opacity_spin.setEnabled(checked)
        self.sw_shadow.setEnabled(checked)
        self.quick_black_btn.setEnabled(checked)

    def on_shadow_distance_changed(self):
        st = self.current_style()
        if not st:
            return
        value = self.shadow_distance.value()
        st.fields["Shadow"] = str(value)
        self.project.commit_change()
        self.preview.update()

    def on_shadow_angle_changed(self, angle: int):
        self.preview.shadow_angle = angle
        st = self.current_style()
        if st:
            st.fields["ChromaAngle"] = str(angle)
            self.project.commit_change()
        self.preview.update()

    def on_shadow_3d_toggled(self, checked: bool):
        self.preview.shadow_3d = checked
        self.shadow_steps.setEnabled(checked)
        st = self.current_style()
        if st:
            st.fields["Chroma3D"] = "True" if checked else "False"
            self.project.commit_change()
        self.preview.update()

    def on_shadow_steps_changed(self):
        steps = self.shadow_steps.value()
        self.preview.shadow_steps = steps
        st = self.current_style()
        if st:
            st.fields["ChromaSteps"] = str(steps)
            self.project.commit_change()
        self.preview.update()

    def preview_shadow_opacity(self, pct: int):
        # Only updates the preview visually while dragging, does not commit to state
        st = self.current_style()
        if not st:
            return
        pct = max(0, min(100, int(pct)))
        alpha = int(round(pct * 255 / 100))
        col = style_get_color(st, "BackColour") or (0, 0, 0, alpha)
        r, g, b, _ = col
        
        # update preview temporarily without modifying project state yet
        st.fields["BackColour"] = f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}"
        self.sw_shadow.set_rgba((r, g, b, alpha))
        self.preview.update()

    def on_shadow_opacity_changed(self):
        # Fires on release
        pct = self.shadow_opacity_spin.value()
        st = self.current_style()
        if not st:
            return
        pct = max(0, min(100, int(pct)))
        alpha = int(round(pct * 255 / 100))

        col = style_get_color(st, "BackColour") or (0, 0, 0, alpha)
        r, g, b, _ = col
        style_set_color(st, "BackColour", (r, g, b, alpha))
        self.sw_shadow.set_rgba((r, g, b, alpha))
        
        self.project.commit_change()
        self.preview.update()

    # ---- File loading ----

    def load_ass(self, path: str):
        try:
            self.project.load(path)
            
            if self.project.doc.bg_color:
                c = QColor(self.project.doc.bg_color)
                if c.isValid():
                    self.preview.set_bg_color(c)
                    self.bg_hex.setText(self.format_bg_hex(c))

            self.styles_list.clear()
            for st in self.project.doc.styles:
                self.styles_list.addItem(QListWidgetItem(st.name))

            self.info.setText(f"Loaded:\n{path}\n\nSelect a style to edit its colors.")
            self.style_line_idx = {}

            self.save_btn.setEnabled(True)
            self.save_as_btn.setEnabled(True)
            self.font_size_spin.setEnabled(True)
            self.font_combo.setEnabled(True)
            self.bold_cb.setEnabled(True)
            self.italic_cb.setEnabled(True)
            self.snap_safe_btn.setEnabled(True)

            has_lyrics = bool(self.project.doc.all_dialogues)
            self.use_first_line_btn.setEnabled(has_lyrics)
            self.next_line_btn.setEnabled(has_lyrics)

            if self.project.doc.styles:
                self.styles_list.setCurrentRow(0)

            if has_lyrics:
                self.use_first_song_line()
            else:
                self.preview_text.setText("Sample Text  AaBb  123  ♪")

        except Exception as e:
            QMessageBox.critical(self, "Load error", str(e))

    def current_style(self) -> Optional[AssStyle]:
        if not self.project.doc:
            return None
        idx = self.styles_list.currentRow()
        if idx < 0 or idx >= len(self.project.doc.styles):
            return None
        return self.project.doc.styles[idx]

    def on_style_selected(self, row: int):
        st = self.current_style()
        self.preview.set_style(st)
        self.show_current_song_line()

        if not st:
            self.sw_highlight.set_rgba(None)
            self.sw_base.set_rgba(None)
            self.sw_outline.set_rgba(None)
            self.sw_shadow.set_rgba(None)

            self.outline_spin.blockSignals(True)
            self.outline_spin.setValue(0)
            self.outline_spin.blockSignals(False)

            self.shadow_distance.blockSignals(True)
            self.shadow_distance.setValue(0)
            self.shadow_distance.blockSignals(False)

            self.shadow_opacity_spin.blockSignals(True)
            self.shadow_opacity_spin.setValue(0)
            self.shadow_opacity_spin.blockSignals(False)

            self.shadow_opacity_slider.blockSignals(True)
            self.shadow_opacity_slider.setValue(0)
            self.shadow_opacity_slider.blockSignals(False)

            self.font_size_spin.blockSignals(True)
            self.font_size_spin.setValue(0)
            self.font_size_spin.blockSignals(False)

            self.bold_cb.blockSignals(True)
            self.bold_cb.setChecked(False)
            self.bold_cb.blockSignals(False)

            self.italic_cb.blockSignals(True)
            self.italic_cb.setChecked(False)
            self.italic_cb.blockSignals(False)

            self.font_size_spin.setStyleSheet("")
            self.font_size_spin.setToolTip("")
            return

        self.sw_highlight.set_rgba(style_get_color(st, "PrimaryColour"))
        self.sw_base.set_rgba(style_get_color(st, "SecondaryColour"))
        self.sw_outline.set_rgba(style_get_color(st, "OutlineColour"))

        self.outline_spin.blockSignals(True)
        self.outline_spin.setValue(style_get_int(st, "Outline", 0))
        self.outline_spin.blockSignals(False)

        self.shadow_distance.blockSignals(True)
        self.shadow_distance.setValue(style_get_int(st, "Shadow", 0))
        self.shadow_distance.blockSignals(False)

        shadow_rgba = style_get_color(st, "BackColour")
        self.sw_shadow.set_rgba(shadow_rgba)
        if shadow_rgba:
            a = shadow_rgba[3]
            pct = int(round(a * 100 / 255))
            self.shadow_opacity_spin.blockSignals(True)
            self.shadow_opacity_spin.setValue(pct)
            self.shadow_opacity_spin.blockSignals(False)

            self.shadow_opacity_slider.blockSignals(True)
            self.shadow_opacity_slider.setValue(pct)
            self.shadow_opacity_slider.blockSignals(False)
        else:
            self.shadow_opacity_spin.blockSignals(True)
            self.shadow_opacity_spin.setValue(0)
            self.shadow_opacity_spin.blockSignals(False)

            self.shadow_opacity_slider.blockSignals(True)
            self.shadow_opacity_slider.setValue(0)
            self.shadow_opacity_slider.blockSignals(False)

        angle = int(st.fields.get("ChromaAngle", 45))
        self.shadow_angle_picker.angle = angle
        self.shadow_angle_picker.update()
        self.preview.shadow_angle = angle

        is_3d = st.fields.get("Chroma3D", "False") == "True"
        self.shadow_3d_cb.blockSignals(True)
        self.shadow_3d_cb.setChecked(is_3d)
        self.shadow_3d_cb.blockSignals(False)
        self.preview.shadow_3d = is_3d
        self.shadow_steps.setEnabled(is_3d)

        steps = int(st.fields.get("ChromaSteps", 10))
        self.shadow_steps.blockSignals(True)
        self.shadow_steps.setValue(steps)
        self.shadow_steps.blockSignals(False)
        self.preview.shadow_steps = steps

        # Load Typography into UI
        fontname = st.fields.get("Fontname", "Arial")
        fontsize = style_get_int(st, "Fontsize", 48)
        is_bold = style_get_int(st, "Bold", 0) != 0
        is_italic = style_get_int(st, "Italic", 0) != 0

        self.font_combo.blockSignals(True)
        self.font_combo.setCurrentFont(QFont(fontname))
        self.font_combo.blockSignals(False)

        self.font_size_spin.blockSignals(True)
        self.font_size_spin.setValue(fontsize)
        self.font_size_spin.blockSignals(False)

        self.bold_cb.blockSignals(True)
        self.bold_cb.setChecked(is_bold)
        self.bold_cb.blockSignals(False)

        self.italic_cb.blockSignals(True)
        self.italic_cb.setChecked(is_italic)
        self.italic_cb.blockSignals(False)

        self.check_font_boundaries()

    def open_chroma_picker(self):
        if not self.picker:
            self.picker = ChromaPickerWindow(self)
            self.picker.colorTransferred.connect(self.receive_chromapicker_color)

        self.picker.show()
        self.picker.raise_()
        self.picker.activateWindow()

    def receive_chromapicker_color(self, target: str, color: QColor):
        if target == "Background":
            self.preview.set_bg_color(color)
            self.bg_hex.setText(self.format_bg_hex(color))
            if self.project.doc:
                self.project.doc.bg_color = self.format_bg_hex(color)
                self.project.commit_change()
            return

        st = self.current_style()
        if not st:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("No Style Loaded")
            msg_box.setText("Please load an .ass file first!")
            msg_box.setIcon(QMessageBox.Icon.Warning)

            load_btn = msg_box.addButton(
                "Load an .ass file", QMessageBox.ButtonRole.ActionRole
            )
            cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            msg_box.exec()

            if msg_box.clickedButton() == load_btn:
                self.drop.open_file_dialog()
            return

        current = style_get_color(st, target) or (255, 255, 255, 0)
        alpha = current[3]
        style_set_color(st, target, (color.red(), color.green(), color.blue(), alpha))
        self.save_custom_colors()
        self.project.commit_change()
        self.on_style_selected(self.styles_list.currentRow())
        self.preview.update()

    # ---- Editing ----

    def pick_color(self, key: str):
        st = self.current_style()
        if not st:
            return

        current = style_get_color(st, key) or (255, 255, 255, 0)
        r, g, b, a = current

        chosen = QColorDialog.getColor(QColor(r, g, b), self, f"Pick {key}")
        if not chosen.isValid():
            return

        self.save_custom_colors()
        style_set_color(st, key, (chosen.red(), chosen.green(), chosen.blue(), a))
        
        self.project.commit_change()
        self.on_style_selected(self.styles_list.currentRow())
        self.preview.update()

    def set_shadow_to_black(self):
        st = self.current_style()
        if not st:
            return
        current = style_get_color(st, "BackColour") or (0, 0, 0, 0)
        _, _, _, a = current
        style_set_color(st, "BackColour", (0, 0, 0, a))
        self.project.commit_change()
        self.on_style_selected(self.styles_list.currentRow())
        self.preview.update()

    def swap_highlight_base(self):
        st = self.current_style()
        if not st:
            return
        prim = style_get_color(st, "PrimaryColour") or (255, 255, 255, 0)
        sec = style_get_color(st, "SecondaryColour") or (255, 255, 0, 0)
        style_set_color(st, "PrimaryColour", sec)
        style_set_color(st, "SecondaryColour", prim)
        self.project.commit_change()
        self.on_style_selected(self.styles_list.currentRow())
        self.preview.update()

    def show_swap_menu(self, pos):
        menu = QMenu(self)
        swap_action = menu.addAction("🔄 Swap Highlight && Base")

        action = menu.exec(QCursor.pos())
        if action == swap_action:
            self.swap_highlight_base()

    def save_file(self):
        if not self.project.doc or not self.project.current_path:
            return
        self._do_save(self.project.current_path)

    def save_as(self):
        if not self.project.doc or not self.project.current_path:
            return
        default_out = str(Path(self.project.current_path).with_suffix("")) + "_edited.ass"
        out_path, _ = QFileDialog.getSaveFileName(
            self, "Save ASS As", default_out, "ASS (*.ass)"
        )
        if out_path:
            self._do_save(out_path)

    def _do_save(self, out_path: str):
        try:
            self.project.save(out_path)
            QMessageBox.information(
                self, "Saved", f"Saved successfully to:\n{out_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Save error", str(e))

    def show_about(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("About ChromaLyric")
        dlg.setModal(True)

        logo = QLabel()
        pix = QPixmap(resource_path("assets/ChromaLyricLogo.png"))
        if not pix.isNull():
            pix = pix.scaled(
                520,
                220,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo.setPixmap(pix)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_lbl = QLabel(
            "Vibe Coded in 2026 by Matt Joy.<br>"
            + '<a href="https://www.youtube.com/@MattJoyKaraoke" style="color: #708090;">youtube.com/@MattJoyKaraoke</a><br>'
            + '<a href="https://github.com/mattjoykaraoke" style="color: #708090;">github.com/mattjoykaraoke</a><br><br>'
            + f"Version {self.CURRENT_VERSION}.<br>"
            + "Built with Qt / PySide6 (LGPL v3).<br>"
            + "Includes community color names curated by meodai.<br>"
            + "See licenses folder for details."
        )
        text_lbl.setOpenExternalLinks(True)
        text_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_lbl.setStyleSheet("font-size: 14px; color: white;")

        ok = QPushButton("OK")
        ok.clicked.connect(dlg.accept)

        lay = QVBoxLayout()
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)
        lay.addWidget(logo)
        lay.addWidget(text_lbl)
        lay.addWidget(ok, alignment=Qt.AlignmentFlag.AlignCenter)

        dlg.setLayout(lay)
        dlg.setStyleSheet(
            "QDialog { background-color: #1E1E1E; } QPushButton { padding: 6px 14px; }"
        )
        dlg.exec()

    # ---- Preview controls ----

    def reset_zoom(self):
        self.zoom_slider.setValue(100)

    def on_zoom_changed(self, v: int):
        self.zoom_lbl.setText(f"Zoom: {v}%")
        effective_scale = self.base_preview_scale * (v / 100.0)
        self.preview.set_preview_scale(effective_scale)

    def on_preview_text_changed(self, text: str):
        self.preview.set_text(text.replace("\\N", "\n"))

    def show_current_song_line(self):
        if not self.project.doc:
            return
        st = self.current_style()
        text_to_use = None

        if st and st.name in self.project.doc.dialogues_by_style:
            style_lines = self.project.doc.dialogues_by_style[st.name]
            if style_lines:
                idx = self.style_line_idx.get(st.name, 0)
                text_to_use = style_lines[idx]

        if not text_to_use and self.project.doc.all_dialogues:
            text_to_use = self.project.doc.all_dialogues[0]

        if text_to_use:
            self.preview_text.setText(text_to_use[:200])

    def use_first_song_line(self):
        st = self.current_style()
        if st:
            self.style_line_idx[st.name] = 0
        self.show_current_song_line()

    def next_song_line(self):
        st = self.current_style()
        if st and st.name in self.project.doc.dialogues_by_style:
            style_lines = self.project.doc.dialogues_by_style[st.name]
            if style_lines:
                current_idx = self.style_line_idx.get(st.name, 0)
                self.style_line_idx[st.name] = (current_idx + 1) % len(style_lines)
        self.show_current_song_line()

    def pick_bg(self):
        initial = self.preview.bg_color
        chosen = QColorDialog.getColor(initial, self, "Pick preview background")
        if not chosen.isValid():
            return
        self.preview.set_bg_color(chosen)
        self.bg_hex.setText(self.format_bg_hex(chosen))
        if self.project.doc:
            self.project.doc.bg_color = self.format_bg_hex(chosen)
            self.project.commit_change()

    def on_bg_hex_changed(self):
        t = self.bg_hex.text().strip()
        if not t.startswith("#"):
            t = "#" + t
        c = QColor(t)
        if not c.isValid():
            QMessageBox.warning(
                self, "Invalid hex", "That hex color couldn't be parsed."
            )
            return
        self.preview.set_bg_color(c)
        self.bg_hex.setText(self.format_bg_hex(c))
        if self.project.doc:
            self.project.doc.bg_color = self.format_bg_hex(c)
            self.project.commit_change()

    def on_k_changed(self, v: int):
        self.k_lbl.setText(f"K: {v}%")
        self.preview.set_k_progress(v / 100.0)

    def toggle_k_play(self):
        if self.k_timer.isActive():
            self.k_timer.stop()
            self.k_play_btn.setText("▶ Play")
        else:
            if self.k_slider.value() >= 100:
                self.k_slider.setValue(0)
            self.k_timer.start()
            self.k_play_btn.setText("⏸ Stop")

    def on_k_timer_tick(self):
        val = self.k_slider.value()
        if val >= 100:
            self.k_timer.stop()
            self.k_play_btn.setText("▶ Play")
        else:
            self.k_slider.setValue(val + 1)

    # ==========================================
    # ---- THEME LIBRARY LOGIC ----
    # ==========================================

    def get_current_style_colors(self):
        st = self.current_style()
        if not st:
            return None
        return {
            "primary": style_get_color(st, "PrimaryColour") or (255, 255, 255, 0),
            "secondary": style_get_color(st, "SecondaryColour") or (255, 255, 0, 0),
            "outline": style_get_color(st, "OutlineColour") or (0, 0, 0, 0),
            "shadow_color": style_get_color(st, "BackColour") or (0, 0, 0, 0),
            "outline_thick": style_get_int(st, "Outline", 0),
            "shadow_dist": style_get_int(st, "Shadow", 0),
            "shadow_angle": self.shadow_angle_picker.angle,
            "shadow_3d": self.shadow_3d_cb.isChecked(),
            "shadow_steps": self.shadow_steps.value(),
        }

    def load_presets(self):
        self.preset_list.clear()
        saved_data = str(self.settings.value("theme_presets", "[]"))
        try:
            self.presets = json.loads(saved_data)
        except json.JSONDecodeError:
            self.presets = []

        for p in self.presets:
            self.preset_list.addItem(QListWidgetItem(p["name"]))

    def save_presets_to_storage(self):
        self.settings.setValue("theme_presets", json.dumps(self.presets))

    def save_new_preset(self):
        colors = self.get_current_style_colors()
        if not colors:
            QMessageBox.warning(
                self, "No Style", "Please select a style first to save its colors."
            )
            return

        name, ok = QInputDialog.getText(
            self, "Save Preset", "Enter a name for this Theme:"
        )
        if ok and name.strip():
            new_preset = {"name": name.strip(), **colors}
            self.presets.append(new_preset)
            self.preset_list.addItem(QListWidgetItem(name.strip()))
            self.save_presets_to_storage()

    def apply_preset(self, item: QListWidgetItem):
        st = self.current_style()
        if not st:
            return

        row = self.preset_list.row(item)
        preset = self.presets[row]

        style_set_color(st, "PrimaryColour", preset["primary"])
        style_set_color(st, "SecondaryColour", preset["secondary"])
        style_set_color(st, "OutlineColour", preset["outline"])

        if "shadow_color" in preset:
            style_set_color(st, "BackColour", preset["shadow_color"])

        if "outline_thick" in preset:
            st.fields["Outline"] = str(preset["outline_thick"])
        if "shadow_dist" in preset:
            st.fields["Shadow"] = str(preset["shadow_dist"])

        if "shadow_angle" in preset:
            self.shadow_angle_picker.angle = preset["shadow_angle"]
            self.shadow_angle_picker.update()
            self.preview.shadow_angle = preset["shadow_angle"]

        if "shadow_3d" in preset:
            self.shadow_3d_cb.setChecked(preset["shadow_3d"])

        if "shadow_steps" in preset:
            self.shadow_steps.setValue(preset["shadow_steps"])

        self.project.commit_change()
        self.on_style_selected(self.styles_list.currentRow())
        self.preview.update()

    def show_preset_context_menu(self, pos):
        item = self.preset_list.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        rename_action = menu.addAction("Rename Preset")
        update_action = menu.addAction("Update with Current Colors")
        delete_action = menu.addAction("Delete Preset")

        action = menu.exec(self.preset_list.mapToGlobal(pos))
        row = self.preset_list.row(item)

        if action == rename_action:
            new_name, ok = QInputDialog.getText(
                self, "Rename Preset", "New name:", text=item.text()
            )
            if ok and new_name.strip():
                self.presets[row]["name"] = new_name.strip()
                item.setText(new_name.strip())
                self.save_presets_to_storage()

        elif action == update_action:
            colors = self.get_current_style_colors()
            if colors:
                self.presets[row].update(colors)
                self.save_presets_to_storage()
                QMessageBox.information(
                    self,
                    "Updated",
                    f"'{item.text()}' updated with your current swatches.",
                )

        elif action == delete_action:
            self.presets.pop(row)
            self.preset_list.takeItem(row)
            self.save_presets_to_storage()

    def export_presets(self):
        if not self.presets:
            QMessageBox.information(
                self, "Empty Library", "There are no presets to export."
            )
            return

        out_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Theme Library",
            "ChromaLyric_Themes.json",
            "JSON Files (*.json)",
        )
        if out_path:
            try:
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(self.presets, f, indent=4)
                QMessageBox.information(
                    self, "Success", "Theme Library exported successfully!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Export Error", f"Failed to export themes:\n{str(e)}"
                )

    def import_presets(self):
        in_path, _ = QFileDialog.getOpenFileName(
            self, "Import Theme Library", "", "JSON Files (*.json)"
        )
        if in_path:
            try:
                with open(in_path, "r", encoding="utf-8") as f:
                    imported_data = json.load(f)

                if isinstance(imported_data, list) and all(
                    "name" in item for item in imported_data
                ):
                    self.presets.extend(imported_data)
                    self.save_presets_to_storage()
                    self.load_presets()
                    QMessageBox.information(
                        self, "Success", f"Imported {len(imported_data)} themes!"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Invalid File",
                        "This file does not contain valid ChromaLyric themes.",
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Import Error", f"Failed to import themes:\n{str(e)}"
                )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            if any(
                u.isLocalFile() and is_supported_file(u.toLocalFile())
                for u in event.mimeData().urls()
            ):
                event.acceptProposedAction()
                return
            event.ignore()

    def load_custom_colors(self):
        saved_colors = list(self.settings.value("custom_colors", []))
        for i, hex_val in enumerate(saved_colors):
            if i < QColorDialog.customCount():
                QColorDialog.setCustomColor(i, QColor(hex_val))

    def save_custom_colors(self):
        custom_colors = []
        for i in range(QColorDialog.customCount()):
            color = QColorDialog.customColor(i)
            custom_colors.append(color.name())
        self.settings.setValue("custom_colors", custom_colors)

    def dropEvent(self, event):
        for u in event.mimeData().urls():
            if u.isLocalFile() and is_supported_file(u.toLocalFile()):
                self.load_ass(u.toLocalFile())
                event.acceptProposedAction()
                return
        event.ignore()
