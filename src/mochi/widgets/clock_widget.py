
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)


class ClockWidget(QWidget):
    """Independent floating digital desktop clock."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.drag_position = None

        self.setWindowTitle("Widget Clock")
        self.setFixedSize(270, 125)

        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_ShowWithoutActivating,
            False,
        )

        self.setStyleSheet("""
            QWidget {
                background-color: #29362C;
                color: #F5F1E9;
                font-family: "Segoe UI";
                border: 1px solid #485A48;
                border-radius: 15px;
            }

            QLabel#Header {
                color: #C3D0BC;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
                border: none;
            }

            QLabel#Time {
                color: #F5F1E9;
                font-size: 39px;
                font-weight: bold;
                border: none;
            }

            QLabel#Date {
                color: #C3D0BC;
                font-size: 11px;
                border: none;
            }

            QPushButton#Close {
                background-color: transparent;
                color: #C3D0BC;
                border: none;
                border-radius: 8px;
                font-size: 17px;
                padding: 2px 7px;
            }

            QPushButton#Close:hover {
                background-color: #754B46;
                color: white;
            }
        """)

        self.build_interface()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.update_time()

    def build_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(17, 11, 17, 12)
        layout.setSpacing(0)

        header = QHBoxLayout()

        heading = QLabel("MOCHI  /  TIME")
        heading.setObjectName("Header")

        close_button = QPushButton("×")
        close_button.setObjectName("Close")
        close_button.setFixedSize(27, 25)
        close_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        close_button.clicked.connect(self.hide)

        header.addWidget(heading)
        header.addStretch()
        header.addWidget(close_button)

        self.time_label = QLabel()
        self.time_label.setObjectName("Time")

        self.date_label = QLabel()
        self.date_label.setObjectName("Date")

        layout.addLayout(header)
        layout.addStretch()
        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)
        layout.addStretch()

    def update_time(self):
        now = datetime.now()

        self.time_label.setText(
            now.strftime("%I:%M:%S %p")
        )

        self.date_label.setText(
            now.strftime("%A, %d %B %Y")
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self.drag_position is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        super().mouseReleaseEvent(event)
