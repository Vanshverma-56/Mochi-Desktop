
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSpinBox,
)


class FocusPage(QWidget):
    """Pomodoro interface connected to Mochi's shared timer."""

    def __init__(self, focus_service, pomodoro):
        super().__init__()

        self.focus_service = focus_service
        self.pomodoro = pomodoro

        self.build_interface()

        self.pomodoro.updated.connect(self.refresh_timer)
        self.pomodoro.session_completed.connect(
            self.on_session_completed
        )

        self.refresh_timer()
        self.refresh_dashboard()

        if self.pomodoro.recovered_session:
            self.state_label.setText(
                "A previous session was interrupted when Mochi closed."
            )

    def build_interface(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(10, 10, 10, 10)
        main.setSpacing(16)

        heading = QLabel("Focus")
        heading.setStyleSheet("""
            font-size: 29px;
            font-weight: bold;
            color: #292B28;
            background: transparent;
        """)

        subtitle = QLabel(
            "Make space for deep work, one session at a time."
        )
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #77796F;
            background: transparent;
        """)

        main.addWidget(heading)
        main.addWidget(subtitle)

        timer_card = QFrame()
        timer_card.setObjectName("FocusTimerCard")

        timer_layout = QVBoxLayout(timer_card)
        timer_layout.setContentsMargins(28, 24, 28, 24)
        timer_layout.setSpacing(18)

        duration_row = QHBoxLayout()

        duration_label = QLabel("FOCUS DURATION")
        duration_label.setStyleSheet("""
            font-size: 11px;
            font-weight: bold;
            color: #77796F;
        """)

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 180)
        self.duration_spin.setSuffix(" min")
        self.duration_spin.setValue(
            self.pomodoro.duration_minutes
        )
        self.duration_spin.valueChanged.connect(
            self.duration_changed
        )

        duration_row.addWidget(duration_label)
        duration_row.addStretch()
        duration_row.addWidget(self.duration_spin)

        timer_layout.addLayout(duration_row)

        self.timer_label = QLabel("25:00")
        self.timer_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.timer_label.setStyleSheet("""
            font-size: 76px;
            font-weight: bold;
            color: #292B28;
            background: transparent;
            padding: 8px;
        """)

        timer_layout.addWidget(self.timer_label)

        self.state_label = QLabel("Ready when you are.")
        self.state_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.state_label.setStyleSheet("""
            font-size: 13px;
            color: #77796F;
            background: transparent;
        """)

        timer_layout.addWidget(self.state_label)

        controls = QHBoxLayout()
        controls.addStretch()

        self.start_button = QPushButton("Start Focus")
        self.start_button.setObjectName("PrimaryButton")
        self.start_button.clicked.connect(self.start_or_resume)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_timer)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_timer)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_timer)

        self.done_button = QPushButton("Done")
        self.done_button.clicked.connect(self.done_completed)

        controls.addWidget(self.start_button)
        controls.addWidget(self.pause_button)
        controls.addWidget(self.reset_button)
        controls.addWidget(self.stop_button)
        controls.addWidget(self.done_button)
        controls.addStretch()

        timer_layout.addLayout(controls)
        main.addWidget(timer_card)

        stats_heading = QLabel("Today's progress")
        stats_heading.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #292B28;
            background: transparent;
        """)

        main.addWidget(stats_heading)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)

        self.sessions_value = self.create_stat_card(
            stats_row,
            "COMPLETED FOCUS SESSIONS",
        )

        self.minutes_value = self.create_stat_card(
            stats_row,
            "FOCUSED MINUTES",
        )

        main.addLayout(stats_row)
        main.addStretch()

        self.setStyleSheet("""
            QFrame#FocusTimerCard,
            QFrame#StatCard {
                background-color: #FFFCF6;
                border: 1px solid #E9E2D6;
                border-radius: 16px;
            }

            QSpinBox {
                background: #FFFCF6;
                color: #292B28;
                border: 1px solid #E9E2D6;
                border-radius: 8px;
                padding: 8px;
                min-width: 95px;
            }

            QPushButton {
                background-color: #EAE5DA;
                color: #454940;
                border: 1px solid #E4DED2;
                border-radius: 9px;
                padding: 10px 16px;
                font-size: 12px;
            }

            QPushButton:hover {
                background-color: #DDD7CA;
            }

            QPushButton:disabled {
                color: #A6A99C;
                background-color: #F0EDE6;
            }

            QPushButton#PrimaryButton {
                background-color: #596B55;
                color: white;
                border: none;
                font-weight: bold;
            }

            QPushButton#PrimaryButton:hover {
                background-color: #465843;
            }
        """)

    def create_stat_card(self, parent_layout, caption):
        card = QFrame()
        card.setObjectName("StatCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 15, 18, 15)

        title = QLabel(caption)
        title.setStyleSheet("""
            font-size: 10px;
            font-weight: bold;
            color: #77796F;
            background: transparent;
        """)

        value = QLabel("0")
        value.setStyleSheet("""
            font-size: 29px;
            font-weight: bold;
            color: #596B55;
            background: transparent;
        """)

        layout.addWidget(title)
        layout.addWidget(value)
        parent_layout.addWidget(card)

        return value

    def duration_changed(self, minutes):
        if (
            self.pomodoro.is_running
            or self.pomodoro.is_paused
            or self.pomodoro.is_completed
        ):
            return

        self.pomodoro.set_mode("Focus", minutes)
        self.refresh_timer()

    def start_or_resume(self):
        try:
            started = self.pomodoro.start()
        except ValueError as error:
            self.state_label.setText(str(error))
            return

        if started:
            self.state_label.setText(
                "You're doing great. Stay in the moment."
            )

        self.refresh_timer()

    def pause_timer(self):
        if self.pomodoro.pause():
            self.state_label.setText(
                "Paused. Take your time."
            )

        self.refresh_timer()

    def reset_timer(self):
        self.pomodoro.reset()
        self.state_label.setText(
            "Timer reset. Ready for a fresh start."
        )
        self.refresh_timer()

    def done_completed(self):
        if self.pomodoro.dismiss_completed():
            self.state_label.setText(
                "Completed session saved. Ready when you are."
            )

        self.refresh_timer()

    def stop_timer(self):
        self.pomodoro.stop()
        self.state_label.setText(
            "Session stopped. Take a breath."
        )
        self.refresh_timer()
        self.refresh_dashboard()

    def refresh_timer(self):
        minutes, seconds = divmod(
            max(0, self.pomodoro.remaining_seconds),
            60,
        )

        self.timer_label.setText(
            f"{minutes:02d}:{seconds:02d}"
        )

        running = self.pomodoro.is_running
        paused = self.pomodoro.is_paused
        completed = self.pomodoro.is_completed
        ready = self.pomodoro.overlay_ready

        # Duration can be adjusted in idle/ready state only.
        self.duration_spin.setEnabled(
            not (running or paused or completed)
        )

        if completed:
            self.start_button.setText("Completed")
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.reset_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.done_button.setEnabled(True)

            self.state_label.setText(
                "Session complete. Nicely done!"
            )

        elif running:
            self.start_button.setText("Running")
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.done_button.setEnabled(False)

        elif paused:
            self.start_button.setText("Resume")
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.reset_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.done_button.setEnabled(False)

        elif ready:
            self.start_button.setText("Start Focus")
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.reset_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.done_button.setEnabled(False)

        else:
            self.start_button.setText("Start Focus")
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.reset_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.done_button.setEnabled(False)

    def on_session_completed(self):
        self.state_label.setText(
            "Session complete. Nicely done!"
        )
        self.refresh_timer()
        self.refresh_dashboard()

    def refresh_dashboard(self):
        summary = self.focus_service.get_daily_summary(
            date.today()
        )

        self.sessions_value.setText(
            str(summary["completed_sessions"])
        )

        self.minutes_value.setText(
            str(summary["focused_minutes"])
        )
