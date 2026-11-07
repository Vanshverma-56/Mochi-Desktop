from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QFrame,
)

from mochi.services.music_player import MusicPlaybackController


class MusicMiniPlayerWidget(QWidget):
    """Compact floating music player for the Windows desktop."""

    open_library_requested = Signal()

    def __init__(
        self,
        playback_controller: MusicPlaybackController,
        parent=None,
    ):
        super().__init__(parent)

        self.playback_controller = playback_controller
        self._drag_position = None

        self.setWindowTitle("Widget - Music Player")
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            False,
        )
        self.setFixedSize(370, 205)

        self.setStyleSheet("""
            QWidget#PlayerWindow {
                background-color: #263C32;
                border: 1px solid #526B58;
                border-radius: 17px;
            }

            QLabel {
                color: #F7F4EA;
                font-family: "Segoe UI";
                border: none;
            }

            QLabel#PlayerHeading {
                color: #B9CBB4;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
            }

            QLabel#TrackTitle {
                color: #FFFDF5;
                font-size: 16px;
                font-weight: bold;
            }

            QLabel#TrackArtist {
                color: #C3CCBF;
                font-size: 11px;
            }

            QLabel#TimeLabel {
                color: #C3CCBF;
                font-size: 9px;
            }

            QPushButton {
                background-color: #405B49;
                color: #FFFDF5;
                border: none;
                border-radius: 9px;
                padding: 7px;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #58735C;
            }

            QPushButton#PlayButton {
                background-color: #D5DFCA;
                color: #263C32;
                font-size: 15px;
                font-weight: bold;
                min-width: 38px;
                min-height: 32px;
            }

            QPushButton#PlayButton:hover {
                background-color: #E6EBDD;
            }

            QPushButton#CloseButton {
                background-color: transparent;
                color: #C3CCBF;
                font-size: 15px;
                padding: 2px 7px;
            }

            QPushButton#CloseButton:hover {
                background-color: #684B45;
                color: white;
            }

            QPushButton#LibraryButton {
                background-color: transparent;
                color: #D5DFCA;
                border: 1px solid #526B58;
                padding: 6px 10px;
                font-size: 10px;
            }

            QSlider::groove:horizontal {
                height: 4px;
                background: #526B58;
                border-radius: 2px;
            }

            QSlider::sub-page:horizontal {
                background: #D5DFCA;
                border-radius: 2px;
            }

            QSlider::handle:horizontal {
                background: #FFFDF5;
                width: 10px;
                margin: -4px 0;
                border-radius: 5px;
            }
        """)

        self.setObjectName("PlayerWindow")
        self.build_interface()
        self.connect_playback_signals()

        self.update_track(
            self.playback_controller.current_track
        )
        self.update_playback_state("playing" if self.playback_controller.is_playing else "stopped")
        self.update_volume(self.playback_controller.volume)

    def build_interface(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(17, 13, 17, 13)
        main_layout.setSpacing(8)

        # Header
        header = QHBoxLayout()

        heading = QLabel("NOW PLAYING")
        heading.setObjectName("PlayerHeading")

        self.library_button = QPushButton("Music Library")
        self.library_button.setObjectName("LibraryButton")
        self.library_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.library_button.clicked.connect(
            self.open_library_requested.emit
        )

        self.close_button = QPushButton("×")
        self.close_button.setObjectName("CloseButton")
        self.close_button.setFixedSize(27, 25)
        self.close_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.close_button.clicked.connect(self.hide)

        header.addWidget(heading)
        header.addStretch()
        header.addWidget(self.library_button)
        header.addWidget(self.close_button)

        main_layout.addLayout(header)

        # Track information
        self.track_title = QLabel("Nothing playing")
        self.track_title.setObjectName("TrackTitle")
        self.track_title.setWordWrap(False)

        self.track_artist = QLabel(
            "Choose a song from your music library"
        )
        self.track_artist.setObjectName("TrackArtist")
        self.track_artist.setWordWrap(False)

        main_layout.addWidget(self.track_title)
        main_layout.addWidget(self.track_artist)

        # Progress
        self.progress_slider = QSlider(
            Qt.Orientation.Horizontal
        )
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderReleased.connect(
            self.seek_to_slider_position
        )

        main_layout.addWidget(self.progress_slider)

        time_row = QHBoxLayout()

        self.current_time_label = QLabel("0:00")
        self.current_time_label.setObjectName("TimeLabel")

        self.duration_label = QLabel("0:00")
        self.duration_label.setObjectName("TimeLabel")

        time_row.addWidget(self.current_time_label)
        time_row.addStretch()
        time_row.addWidget(self.duration_label)

        main_layout.addLayout(time_row)

        # Playback controls and volume
        controls = QHBoxLayout()
        controls.setSpacing(7)

        self.previous_button = QPushButton("|◀")
        self.previous_button.setFixedSize(38, 34)
        self.previous_button.clicked.connect(
            self.playback_controller.previous_track
        )

        self.play_button = QPushButton("▶")
        self.play_button.setObjectName("PlayButton")
        self.play_button.clicked.connect(
            self.playback_controller.toggle_play_pause
        )

        self.next_button = QPushButton("▶|")
        self.next_button.setFixedSize(38, 34)
        self.next_button.clicked.connect(
            self.playback_controller.next_track
        )

        self.volume_label = QLabel("VOL")
        self.volume_label.setObjectName("TimeLabel")

        self.volume_slider = QSlider(
            Qt.Orientation.Horizontal
        )
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setFixedWidth(65)
        self.volume_slider.valueChanged.connect(
            lambda value: self.playback_controller.set_volume(
                value / 100
            )
        )

        controls.addWidget(self.previous_button)
        controls.addWidget(self.play_button)
        controls.addWidget(self.next_button)
        controls.addStretch()
        controls.addWidget(self.volume_label)
        controls.addWidget(self.volume_slider)

        main_layout.addLayout(controls)

    def connect_playback_signals(self):
        self.playback_controller.track_changed.connect(
            self.update_track
        )
        self.playback_controller.position_changed.connect(
            self.update_position
        )
        self.playback_controller.duration_changed.connect(
            self.update_duration
        )
        self.playback_controller.playback_state_changed.connect(
            self.update_playback_state
        )
        self.playback_controller.volume_changed.connect(
            self.update_volume
        )
        self.playback_controller.playback_error.connect(
            self.show_playback_error
        )

    @staticmethod
    def format_time(milliseconds):
        seconds = max(0, int(milliseconds // 1000))
        minutes, seconds = divmod(seconds, 60)

        return f"{minutes}:{seconds:02d}"

    def update_track(self, track):
        if not track:
            self.track_title.setText("Nothing playing")
            self.track_artist.setText(
                "Choose a song from your music library"
            )
            self.progress_slider.setValue(0)
            self.current_time_label.setText("0:00")
            self.duration_label.setText("0:00")
            return

        self.track_title.setText(
            track.get("title") or Path(
                track.get("file_path", "Unknown")
            ).stem
        )
        self.track_artist.setText(
            track.get("artist") or "Unknown Artist"
        )

        self.progress_slider.setValue(0)
        self.current_time_label.setText("0:00")

    def update_position(self, position):
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(position)

        self.current_time_label.setText(
            self.format_time(position)
        )

    def update_duration(self, duration):
        self.progress_slider.setRange(0, max(0, duration))
        self.duration_label.setText(
            self.format_time(duration)
        )

    def seek_to_slider_position(self):
        self.playback_controller.seek(
            self.progress_slider.value()
        )

    def update_playback_state(self, state):
        self.play_button.setText(
            "Ⅱ" if state == "playing" else "▶"
        )

    def update_volume(self, volume):
        self.volume_slider.blockSignals(True)
        self.volume_slider.setValue(
            round(volume * 100)
        )
        self.volume_slider.blockSignals(False)

    def show_playback_error(self, message):
        self.track_artist.setText(message)

    # Allow dragging the frameless floating window.
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self._drag_position is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint()
                - self._drag_position
            )
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_position = None
        super().mouseReleaseEvent(event)

    def closeEvent(self, event):
        # Closing the mini-player hides it; it does not stop music.
        event.ignore()
        self.hide()