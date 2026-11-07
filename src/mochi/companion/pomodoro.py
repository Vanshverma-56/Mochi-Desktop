
import os
import time
import ctypes
from ctypes import wintypes
import winsound

from pathlib import Path

from PySide6.QtCore import (
    Qt, QTimer, Signal, QObject, QPropertyAnimation,
    QEasingCurve, QPoint, QSettings,
)
from PySide6.QtGui import (
    QColor, QPainter, QPen, QFont, QGuiApplication,
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedLayout, QFrame,
    QGraphicsDropShadowEffect,
)


class PomodoroController(QObject):
    """Single source of truth for Mochi's Pomodoro timer."""

    updated = Signal()
    overlay_dismissed = Signal()
    session_completed = Signal()

    MODES = {
        "Focus": 25,
        "Short Break": 5,
        "Long Break": 15,
    }

    SOUND_FILES = {
        "Default": "default.wav",
        "Chime": "chime.wav",
        "Alert": "alert.wav",
        "Gentle": "gentle.wav",
    }

    def __init__(self, focus_service):
        super().__init__()

        self.focus_service = focus_service
        self.mode = "Focus"
        self.duration_minutes = 25
        self.remaining_seconds = 1500
        self.deadline = None
        self.session_id = None

        self.is_running = False
        self.is_paused = False
        self.is_completed = False
        self.overlay_ready = False

        self.sound_directory = (
            Path(__file__).resolve().parents[3]
            / "assets" / "sounds"
        )

        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self._update_countdown)

        self.recovered_session = (
            self.focus_service.interrupt_active_session()
        )

    @property
    def has_overlay_state(self):
        return (
            self.is_running
            or self.is_paused
            or self.is_completed
            or self.overlay_ready
        )

    def set_mode(self, mode, duration=None):
        # A ready overlay may still have its duration adjusted.
        if self.is_running or self.is_paused or self.is_completed:
            return False

        if mode not in self.MODES:
            raise ValueError("Invalid Pomodoro mode.")

        value = duration if duration is not None else self.MODES[mode]

        if type(value) is not int or not 1 <= value <= 180:
            raise ValueError("Duration must be between 1 and 180 minutes.")

        self.mode = mode
        self.duration_minutes = value
        self.remaining_seconds = value * 60
        self.updated.emit()
        return True

    def start(self):
        if self.is_paused:
            return self.resume()

        if self.is_running or self.is_completed:
            return False

        # overlay_ready deliberately does not block a new session.
        session = self.focus_service.start_session(
            duration_minutes=self.duration_minutes,
            session_type="Focus",
        )

        self.session_id = session["id"]
        self.remaining_seconds = self.duration_minutes * 60
        self.deadline = time.monotonic() + self.remaining_seconds

        self.is_running = True
        self.is_paused = False
        self.is_completed = False
        self.overlay_ready = False

        self.timer.start()
        self.updated.emit()
        return True

    def pause(self):
        if not self.is_running:
            return False

        self._calculate_remaining()
        self.timer.stop()

        self.is_running = False
        self.is_paused = True
        self.deadline = None

        self.updated.emit()
        return True

    def resume(self):
        if not self.is_paused:
            return False

        self.deadline = time.monotonic() + self.remaining_seconds
        self.is_paused = False
        self.is_running = True

        self.timer.start()
        self.updated.emit()
        return True

    def reset(self):
        """Interrupt the current session and leave its overlay ready to restart."""
        keep_overlay = self.has_overlay_state

        if self.session_id is not None:
            self.focus_service.interrupt_session(self.session_id)

        self.timer.stop()
        self.session_id = None
        self.deadline = None

        self.is_running = False
        self.is_paused = False
        self.is_completed = False
        self.overlay_ready = keep_overlay

        self.remaining_seconds = self.duration_minutes * 60

        self.updated.emit()

        if not keep_overlay:
            self.overlay_dismissed.emit()

    def stop(self):
        """Stop the timer and dismiss the floating overlay."""
        self.reset()
        self.overlay_ready = False
        self.updated.emit()
        self.overlay_dismissed.emit()

    def dismiss_completed(self):
        """Dismiss the completed overlay without changing saved history."""
        if not self.is_completed:
            return False

        self.is_completed = False
        self.overlay_ready = False
        self.remaining_seconds = self.duration_minutes * 60

        self.updated.emit()
        self.overlay_dismissed.emit()
        return True

    def _calculate_remaining(self):
        if self.deadline is None:
            return

        self.remaining_seconds = max(
            0,
            int(self.deadline - time.monotonic() + 0.999),
        )

    def _update_countdown(self):
        if not self.is_running:
            return

        self._calculate_remaining()
        self.updated.emit()

        if self.remaining_seconds <= 0:
            self._complete()

    def _complete(self):
        self.timer.stop()

        if self.session_id is not None:
            self.focus_service.complete_session(self.session_id)

        self.session_id = None
        self.deadline = None
        self.remaining_seconds = 0

        self.is_running = False
        self.is_paused = False
        self.is_completed = True
        self.overlay_ready = False

        self.play_completion_sound()
        self.updated.emit()
        self.session_completed.emit()

    def play_completion_sound(self):
        settings = QSettings("Mochi", "Mochi")
        sound = settings.value("focus/completion_sound", "Default")
        self.play_sound(sound)

    def preview_sound(self, sound):
        self.play_sound(sound)

    def play_sound(self, sound):
        filename = self.SOUND_FILES.get(sound, "default.wav")
        path = self.sound_directory / filename

        try:
            if path.exists():
                winsound.PlaySound(
                    str(path),
                    winsound.SND_FILENAME | winsound.SND_ASYNC,
                )
            else:
                QApplication.beep()
        except Exception:
            QApplication.beep()


class CircularTimerFace(QWidget):
    """Light circular countdown with a progress ring."""

    def __init__(self, controller, toggle_callback, restore_callback):
        super().__init__()

        self.controller = controller
        self.toggle_callback = toggle_callback
        self.restore_callback = restore_callback

        # Delay a single click so a double-click can take priority.
        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.setInterval(280)
        self.click_timer.timeout.connect(self.toggle_callback)

        self.setFixedSize(116, 116)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(3, 3, -3, -3)

        painter.setPen(QPen(QColor("#E9E2D6"), 1))
        painter.setBrush(QColor("#FFFCF6"))
        painter.drawEllipse(rect)

        ring = rect.adjusted(9, 9, -9, -9)

        painter.setPen(QPen(QColor("#DED8CC"), 6))
        painter.drawArc(ring, 0, 360 * 16)

        total = max(1, self.controller.duration_minutes * 60)
        progress = self.controller.remaining_seconds / total
        progress = max(0.0, min(1.0, progress))

        painter.setPen(QPen(
            QColor("#596B55"),
            6,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
        ))

        painter.drawArc(
            ring,
            90 * 16,
            int(-360 * progress * 16),
        )

        painter.setPen(QColor("#292B28"))
        painter.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))

        minutes, seconds = divmod(
            max(0, self.controller.remaining_seconds), 60
        )

        painter.drawText(
            self.rect().adjusted(0, -5, 0, -5),
            Qt.AlignmentFlag.AlignCenter,
            f"{minutes:02d}:{seconds:02d}",
        )

        painter.setPen(QColor("#77796F"))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(
            self.rect().adjusted(0, 48, 0, 0),
            Qt.AlignmentFlag.AlignCenter,
            "MOCHI",
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_timer.start()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_timer.stop()
            self.restore_callback()


class FloatingTimerWindow(QWidget):
    """Independent bottom-right Pomodoro overlay."""

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.workspace_window = None
        self.expanded = False
        self._allow_close = False

        self.setWindowTitle("Mochi Focus Timer")
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_ShowWithoutActivating, True
        )

        self.stack = QStackedLayout(self)
        self.stack.setContentsMargins(0, 0, 0, 0)

        self.circle = CircularTimerFace(
            controller,
            self.toggle_expanded,
            self.restore_workspace,
        )

        self.card = self.build_expanded_card()

        self.stack.addWidget(self.circle)
        self.stack.addWidget(self.card)
        self.stack.setCurrentWidget(self.circle)

        self.controller.updated.connect(self.refresh)
        self.controller.overlay_dismissed.connect(self.hide)

        self.setFixedSize(116, 116)

        self.coverage_timer = QTimer(self)
        self.coverage_timer.setInterval(450)
        self.coverage_timer.timeout.connect(
            self.check_workspace_visibility
        )

        self.show_delay = QTimer(self)
        self.show_delay.setSingleShot(True)
        self.show_delay.setInterval(1300)
        self.show_delay.timeout.connect(self.show_for_session)

        self.animation = QPropertyAnimation(self, b"pos", self)
        self.animation.setDuration(280)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 45))
        self.setGraphicsEffect(shadow)

    def set_workspace_window(self, window):
        self.workspace_window = window
        self.coverage_timer.start()

    def build_expanded_card(self):
        card = QFrame()
        card.setObjectName("FloatingCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(17, 13, 17, 14)
        layout.setSpacing(9)

        header = QHBoxLayout()

        title = QLabel("MOCHI  ·  FOCUS")
        title.setStyleSheet(
            "font-size: 10px; font-weight: bold; color: #77796F;"
        )

        collapse = QPushButton("−")
        collapse.setFixedSize(27, 25)
        collapse.clicked.connect(self.toggle_expanded)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(collapse)
        layout.addLayout(header)

        self.expanded_time = QLabel("25:00")
        self.expanded_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.expanded_time.setStyleSheet(
            "font-size: 34px; font-weight: bold; color: #292B28;"
        )
        layout.addWidget(self.expanded_time)

        controls = QHBoxLayout()

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_from_overlay)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.controller.reset)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.controller.stop)

        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(
            self.controller.dismiss_completed
        )

        controls.addWidget(self.start_button)
        controls.addWidget(self.pause_button)
        controls.addWidget(self.reset_button)
        controls.addWidget(self.stop_button)
        controls.addWidget(self.done_button)
        layout.addLayout(controls)

        card.setStyleSheet("""
            QFrame#FloatingCard {
                background-color: #FFFCF6;
                border: 1px solid #E9E2D6;
                border-radius: 18px;
            }
            QLabel { background: transparent; }
            QPushButton {
                background-color: #EAE5DA;
                color: #454940;
                border: none;
                border-radius: 8px;
                padding: 7px 10px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #DDD7CA; }
        """)

        return card

    def toggle_expanded(self):
        self.expanded = not self.expanded

        if self.expanded:
            self.setFixedSize(280, 155)
            self.stack.setCurrentWidget(self.card)
        else:
            self.setFixedSize(116, 116)
            self.stack.setCurrentWidget(self.circle)

        self.position_bottom_right()

    def start_from_overlay(self):
        try:
            self.controller.start()
        except ValueError:
            return

        self.refresh()

    def toggle_pause(self):
        if self.controller.is_running:
            self.controller.pause()
        elif self.controller.is_paused:
            self.controller.resume()

    def refresh(self):
        minutes, seconds = divmod(
            max(0, self.controller.remaining_seconds), 60
        )
        self.expanded_time.setText(f"{minutes:02d}:{seconds:02d}")

        completed = self.controller.is_completed
        running = self.controller.is_running
        paused = self.controller.is_paused
        ready = self.controller.overlay_ready

        self.start_button.setVisible(ready and not completed)
        self.pause_button.setVisible(running or paused)
        self.stop_button.setVisible(running or paused)
        self.done_button.setVisible(completed)
        self.reset_button.setVisible(
            ready or running or paused or completed
        )

        self.pause_button.setText(
            "Resume" if paused else "Pause"
        )

        self.circle.update()

    def position_bottom_right(self):
        screen = None

        if self.workspace_window is not None:
            screen = self.workspace_window.screen()

        if screen is None:
            screen = QGuiApplication.primaryScreen()

        if screen is None:
            return

        area = screen.availableGeometry()

        self.move(
            area.right() - self.width() - 22,
            area.bottom() - self.height() - 18,
        )

    def show_for_session(self):
        if not self.controller.has_overlay_state:
            return

        self.show_delay.stop()
        self.refresh()
        self.position_bottom_right()

        final_position = self.pos()
        start_position = QPoint(
            final_position.x(),
            final_position.y() + 35,
        )

        self.move(start_position)
        self.show()
        self.raise_()

        self.animation.stop()
        self.animation.setStartValue(start_position)
        self.animation.setEndValue(final_position)
        self.animation.start()

    def check_workspace_visibility(self):
        if not self.controller.has_overlay_state:
            self.show_delay.stop()
            if self.isVisible():
                self.hide()
            return

        if self.workspace_window is None:
            return

        # Show the timer if the Dashboard is hidden, minimized,
        # or substantially covered by another window.
        should_show = (
            not self.workspace_window.isVisible()
            or self.workspace_window.isMinimized()
        )

        if not should_show:
            coverage = self.get_workspace_coverage()
            should_show = coverage >= 70.0

        if should_show:
            if not self.isVisible() and not self.show_delay.isActive():
                self.show_delay.start()
        else:
            self.show_delay.stop()
            if self.isVisible():
                self.hide()

    def get_workspace_coverage(self):
        """Calculate exact union coverage from windows above Mochi."""
        if os.name != "nt" or self.workspace_window is None:
            return 0.0

        user32 = ctypes.windll.user32
        dwmapi = ctypes.windll.dwmapi

        RECT = wintypes.RECT
        HWND = wintypes.HWND
        BOOL = wintypes.BOOL
        DWORD = wintypes.DWORD
        LPARAM = wintypes.LPARAM

        # Explicit prototypes prevent 64-bit HWND truncation.
        callback_type = ctypes.WINFUNCTYPE(BOOL, HWND, LPARAM)

        user32.GetWindowRect.argtypes = [
            HWND, ctypes.POINTER(RECT)
        ]
        user32.GetWindowRect.restype = BOOL

        user32.IsWindowVisible.argtypes = [HWND]
        user32.IsWindowVisible.restype = BOOL

        user32.IsIconic.argtypes = [HWND]
        user32.IsIconic.restype = BOOL

        user32.GetWindowThreadProcessId.argtypes = [
            HWND, ctypes.POINTER(DWORD)
        ]
        user32.GetWindowThreadProcessId.restype = DWORD

        user32.EnumWindows.argtypes = [
            callback_type, LPARAM
        ]
        user32.EnumWindows.restype = BOOL

        dwmapi.DwmGetWindowAttribute.argtypes = [
            HWND, DWORD, ctypes.c_void_p, DWORD
        ]
        dwmapi.DwmGetWindowAttribute.restype = ctypes.c_long

        target_value = int(self.workspace_window.winId())
        target = HWND(target_value)
        target_rect = RECT()

        if not user32.GetWindowRect(target, ctypes.byref(target_rect)):
            return 0.0

        left = target_rect.left
        top = target_rect.top
        right = target_rect.right
        bottom = target_rect.bottom

        width = max(0, right - left)
        height = max(0, bottom - top)

        if width == 0 or height == 0:
            return 0.0

        own_pid = os.getpid()
        rectangles = []
        found_target = False

        def visit(hwnd, lparam):
            nonlocal found_target

            hwnd_value = int(hwnd or 0)

            # EnumWindows visits top-level windows in Z-order.
            # Stop at Mochi: windows below it cannot cover it.
            if hwnd_value == target_value:
                found_target = True
                return False

            if not user32.IsWindowVisible(hwnd):
                return True

            if user32.IsIconic(hwnd):
                return True

            pid = DWORD()
            user32.GetWindowThreadProcessId(
                hwnd, ctypes.byref(pid)
            )

            # Ignore Mochi's own windows, including its pet/overlay.
            if pid.value == own_pid:
                return True

            cloaked = DWORD(0)
            try:
                result = dwmapi.DwmGetWindowAttribute(
                    hwnd,
                    14,
                    ctypes.cast(
                        ctypes.byref(cloaked),
                        ctypes.c_void_p,
                    ),
                    ctypes.sizeof(cloaked),
                )
                if result == 0 and cloaked.value:
                    return True
            except (OSError, ValueError):
                pass

            rect = RECT()
            if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                return True

            x1 = max(left, rect.left)
            y1 = max(top, rect.top)
            x2 = min(right, rect.right)
            y2 = min(bottom, rect.bottom)

            if x2 > x1 and y2 > y1:
                rectangles.append((x1, y1, x2, y2))

            return True

        callback = callback_type(visit)
        user32.EnumWindows(callback, LPARAM(0))

        if not found_target:
            return 0.0

        # Exact rectangle-union area: overlapping windows are not
        # double-counted.
        xs = sorted({
            coordinate
            for rect in rectangles
            for coordinate in (rect[0], rect[2])
        })

        covered_area = 0

        for index in range(len(xs) - 1):
            x1 = xs[index]
            x2 = xs[index + 1]

            intervals = [
                (rect[1], rect[3])
                for rect in rectangles
                if rect[0] < x2 and rect[2] > x1
            ]

            if not intervals:
                continue

            intervals.sort()
            y_start, y_end = intervals[0]
            covered_height = 0

            for start, end in intervals[1:]:
                if start <= y_end:
                    y_end = max(y_end, end)
                else:
                    covered_height += y_end - y_start
                    y_start, y_end = start, end

            covered_height += y_end - y_start
            covered_area += (x2 - x1) * covered_height

        return min(
            100.0,
            covered_area / (width * height) * 100.0,
        )

    def restore_workspace(self):
        if self.workspace_window is None:
            return

        self.workspace_window.showNormal()
        self.workspace_window.raise_()
        self.workspace_window.activateWindow()

        if os.name == "nt":
            try:
                user32 = ctypes.windll.user32
                hwnd = wintypes.HWND(
                    int(self.workspace_window.winId())
                )

                user32.SetForegroundWindow.argtypes = [
                    wintypes.HWND
                ]
                user32.SetForegroundWindow.restype = wintypes.BOOL
                user32.SetForegroundWindow(hwnd)
            except (AttributeError, OSError, ValueError):
                pass

    def shutdown(self):
        """Allow application shutdown even when a session is active."""
        self._allow_close = True
        self.coverage_timer.stop()
        self.show_delay.stop()
        self.animation.stop()
        self.hide()
        self.close()

    def closeEvent(self, event):
        if self.controller.has_overlay_state and not self._allow_close:
            event.ignore()
        else:
            event.accept()
