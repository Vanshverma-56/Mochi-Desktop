
from pathlib import Path
import random

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import (
    QAudioOutput,
    QMediaPlayer,
)


class MusicPlaybackController(QObject):
    """Controls local music playback independently of the UI."""

    track_changed = Signal(object)
    position_changed = Signal(int)
    duration_changed = Signal(int)
    playback_state_changed = Signal(str)
    volume_changed = Signal(float)
    playback_error = Signal(str)

    REPEAT_OFF = "off"
    REPEAT_ALL = "all"
    REPEAT_ONE = "one"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.audio_output = QAudioOutput(self)
        self.player = QMediaPlayer(self)

        self.player.setAudioOutput(self.audio_output)

        self.queue = []
        self.current_index = -1
        self.shuffle_enabled = False
        self.repeat_mode = self.REPEAT_OFF
        self._current_path = None

        self.audio_output.setVolume(0.7)

        self.player.positionChanged.connect(
            self.position_changed.emit
        )
        self.player.durationChanged.connect(
            self.duration_changed.emit
        )
        self.player.playbackStateChanged.connect(
            self._on_playback_state_changed
        )
        self.player.mediaStatusChanged.connect(
            self._on_media_status_changed
        )
        self.player.errorOccurred.connect(
            self._on_playback_error
        )
        self.audio_output.volumeChanged.connect(
            self.volume_changed.emit
        )

    @property
    def current_track(self):
        if 0 <= self.current_index < len(self.queue):
            return self.queue[self.current_index]

        return None

    @property
    def is_playing(self):
        return (
            self.player.playbackState()
            == QMediaPlayer.PlaybackState.PlayingState
        )

    @property
    def position(self):
        return self.player.position()

    @property
    def duration(self):
        return self.player.duration()

    @property
    def volume(self):
        return self.audio_output.volume()

    def set_queue(self, tracks, start_index=0, autoplay=True):
        """Replace the queue and optionally start a track."""

        if not tracks:
            self.stop()
            self.queue = []
            self.current_index = -1
            self._current_path = None
            self.track_changed.emit(None)
            return

        if not 0 <= start_index < len(tracks):
            raise IndexError("Invalid starting track index.")

        self.stop()

        self.queue = list(tracks)
        self.current_index = start_index
        self._current_path = None

        self.track_changed.emit(self.current_track)

        if autoplay:
            self.play()

    def play_track(self, track):
        """Play a single track as a new queue."""

        self.set_queue([track], autoplay=True)

    def play(self):
        track = self.current_track

        if track is None:
            return

        file_path = track.get("file_path")

        if not file_path or not Path(file_path).is_file():
            self.playback_error.emit(
                "The selected audio file could not be found."
            )
            return

        if self._current_path != file_path:
            self._current_path = file_path
            self.player.setSource(
                QUrl.fromLocalFile(str(Path(file_path).resolve()))
            )

        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def toggle_play_pause(self):
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def next_track(self, automatic=False):
        """Move to the next track in the queue."""

        if not self.queue:
            return

        if self.shuffle_enabled and len(self.queue) > 1:
            candidates = [
                index for index in range(len(self.queue))
                if index != self.current_index
            ]
            next_index = random.choice(candidates)

        elif self.current_index < len(self.queue) - 1:
            next_index = self.current_index + 1

        elif self.repeat_mode == self.REPEAT_ALL:
            next_index = 0

        else:
            if automatic:
                self.stop()
            return

        self.current_index = next_index
        self._current_path = None

        self.track_changed.emit(self.current_track)
        self.play()

    def previous_track(self):
        """Return to the previous track or restart the current one."""

        if not self.queue:
            return

        if self.position > 3000:
            self.seek(0)
            return

        if self.current_index > 0:
            self.current_index -= 1

        elif self.repeat_mode == self.REPEAT_ALL:
            self.current_index = len(self.queue) - 1

        else:
            self.seek(0)
            return

        self._current_path = None

        self.track_changed.emit(self.current_track)
        self.play()

    def seek(self, position_ms):
        self.player.setPosition(
            max(0, min(int(position_ms), self.duration))
        )

    def set_volume(self, volume):
        self.audio_output.setVolume(
            max(0.0, min(float(volume), 1.0))
        )

    def set_muted(self, muted):
        self.audio_output.setMuted(bool(muted))

    def set_shuffle(self, enabled):
        self.shuffle_enabled = bool(enabled)

    def set_repeat_mode(self, mode):
        if mode not in {
            self.REPEAT_OFF,
            self.REPEAT_ALL,
            self.REPEAT_ONE,
        }:
            raise ValueError("Invalid repeat mode.")

        self.repeat_mode = mode

    def _on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            value = "playing"
        elif state == QMediaPlayer.PlaybackState.PausedState:
            value = "paused"
        else:
            value = "stopped"

        self.playback_state_changed.emit(value)

    def _on_media_status_changed(self, status):
        if status != QMediaPlayer.MediaStatus.EndOfMedia:
            return

        if self.repeat_mode == self.REPEAT_ONE:
            self.player.setPosition(0)
            self.player.play()
        else:
            self.next_track(automatic=True)

    def _on_playback_error(self, error, error_string):
        if error == QMediaPlayer.Error.NoError:
            return

        self.playback_error.emit(
            error_string or "An unknown playback error occurred."
        )
