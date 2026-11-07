
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)

from mochi.widgets.clock_widget import ClockWidget
from mochi.widgets.system_monitor import SystemMonitorWidget
from mochi.widgets.calendar_widget import CalendarWidget
from mochi.widgets.music_mini_player import MusicMiniPlayerWidget


class DesktopWidgetsWindow(QMainWindow):
    """Control hub for independent desktop widgets."""

    def __init__(self, calendar_service, music_service, music_player):
        super().__init__()

        self.setWindowTitle("Widget - Desktop Widgets")
        self.resize(560, 570)
        self.setMinimumSize(480, 480)

        # Existing desktop widgets
        self.clock_widget = ClockWidget()
        self.system_monitor = SystemMonitorWidget()
        self.calendar_widget = CalendarWidget(calendar_service)

        # Music System
        self.music_service = music_service
        self.music_player = music_player
        self.music_mini_player = MusicMiniPlayerWidget(music_player)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F1E9;
            }

            QLabel {
                color: #292B28;
                font-family: "Segoe UI";
            }

            QLabel#Heading {
                font-size: 25px;
                font-weight: bold;
                color: #354B38;
            }

            QLabel#Subtitle {
                color: #77796F;
                font-size: 12px;
            }

            QFrame#WidgetCard {
                background-color: #FFFCF6;
                border: 1px solid #DEDCCF;
                border-radius: 14px;
            }

            QLabel#WidgetTitle {
                font-size: 15px;
                font-weight: bold;
                color: #354B38;
            }

            QLabel#WidgetDescription {
                color: #77796F;
                font-size: 11px;
            }

            QLabel#Status {
                color: #71896B;
                font-size: 11px;
                font-weight: bold;
            }

            QPushButton {
                background-color: #596B55;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 9px 15px;
                font-size: 11px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #465641;
            }
        """)

        self.build_interface()
        self.refresh_status()

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.refresh_status)
        self.status_timer.start(500)

    def create_widget_card(
        self,
        title_text,
        description_text,
        status_attribute,
        button_attribute,
        toggle_callback,
    ):
        """Create a reusable widget control card."""

        card = QFrame()
        card.setObjectName("WidgetCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(17, 14, 17, 14)
        card_layout.setSpacing(8)

        top = QHBoxLayout()

        title = QLabel(title_text)
        title.setObjectName("WidgetTitle")

        status = QLabel("Hidden")
        status.setObjectName("Status")

        top.addWidget(title)
        top.addStretch()
        top.addWidget(status)

        description = QLabel(description_text)
        description.setObjectName("WidgetDescription")
        description.setWordWrap(True)

        
        button = QPushButton("Show")
        button.setObjectName("WidgetToggleButton")
        button.setMinimumHeight(36)
        button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        button.setStyleSheet("""
            QPushButton#WidgetToggleButton {
                background-color: #596B55;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 9px 15px;
                font-family: "Segoe UI";
                font-size: 12px;
                font-weight: bold;
            }

            QPushButton#WidgetToggleButton:hover {
                background-color: #465641;
                color: #FFFFFF;
            }

            QPushButton#WidgetToggleButton:pressed {
                background-color: #354B38;
                color: #FFFFFF;
            }
        """)

        button.clicked.connect(toggle_callback)


        card_layout.addLayout(top)
        card_layout.addWidget(description)
        card_layout.addWidget(button)

        setattr(self, status_attribute, status)
        setattr(self, button_attribute, button)

        return card

    def build_interface(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(12)

        heading = QLabel("Desktop Widgets")
        heading.setObjectName("Heading")

        subtitle = QLabel(
            "Your favourite tools, floating on your desktop."
        )
        subtitle.setObjectName("Subtitle")

        layout.addWidget(heading)
        layout.addWidget(subtitle)
        layout.addSpacing(5)

        # Digital Clock
        clock_card = self.create_widget_card(
            "Digital Clock",
            "A floating clock displaying the current time and date.",
            "clock_status",
            "clock_button",
            self.toggle_clock,
        )
        layout.addWidget(clock_card)

        # System Monitor
        monitor_card = self.create_widget_card(
            "System Monitor",
            "Live CPU usage, RAM utilization and battery status.",
            "monitor_status",
            "monitor_button",
            self.toggle_system_monitor,
        )
        layout.addWidget(monitor_card)

        # Calendar
        calendar_card = self.create_widget_card(
            "Calendar",
            "A floating monthly calendar with your events and schedule.",
            "calendar_status",
            "calendar_button",
            self.toggle_calendar,
        )
        layout.addWidget(calendar_card)

        # Music Player
        music_card = self.create_widget_card(
            "Music Player",
            "Control your music from a compact floating mini-player.",
            "music_status",
            "music_button",
            self.toggle_music_player,
        )
        layout.addWidget(music_card)

        layout.addStretch()

        footer = QLabel("WIDGET DESKTOP TOOLS")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            "color: #96978D; font-size: 9px;"
        )

        layout.addWidget(footer)

    def toggle_clock(self):
        if self.clock_widget.isVisible():
            self.clock_widget.hide()
        else:
            self.clock_widget.show()
            self.clock_widget.raise_()

        self.refresh_status()

    def toggle_system_monitor(self):
        if self.system_monitor.isVisible():
            self.system_monitor.hide()
        else:
            self.system_monitor.show()
            self.system_monitor.raise_()

        self.refresh_status()

    def toggle_calendar(self):
        if self.calendar_widget.isVisible():
            self.calendar_widget.hide()
        else:
            self.calendar_widget.show()
            self.calendar_widget.raise_()

        self.refresh_status()

    def toggle_music_player(self):
        if self.music_mini_player.isVisible():
            self.music_mini_player.hide()
        else:
            self.music_mini_player.show()
            self.music_mini_player.raise_()

        self.refresh_status()

    def refresh_status(self):
        clock_visible = self.clock_widget.isVisible()
        monitor_visible = self.system_monitor.isVisible()
        calendar_visible = self.calendar_widget.isVisible()
        music_visible = self.music_mini_player.isVisible()

        self.clock_status.setText(
            "Running" if clock_visible else "Hidden"
        )
        self.clock_button.setText(
            "Hide Clock" if clock_visible else "Show Clock"
        )

        self.monitor_status.setText(
            "Running" if monitor_visible else "Hidden"
        )
        self.monitor_button.setText(
            "Hide Monitor" if monitor_visible else "Show Monitor"
        )

        self.calendar_status.setText(
            "Running" if calendar_visible else "Hidden"
        )
        self.calendar_button.setText(
            "Hide Calendar" if calendar_visible else "Show Calendar"
        )

        self.music_status.setText(
            "Running" if music_visible else "Hidden"
        )
        self.music_button.setText(
            "Hide Music Player" if music_visible else "Show Music Player"
        )

    def shutdown(self):
        """Close independently floating widgets during app exit."""

        self.status_timer.stop()

        self.clock_widget.close()
        self.system_monitor.close()
        self.calendar_widget.close()
        self.music_mini_player.hide()

        self.close()
