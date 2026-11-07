
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
)

import psutil


class SystemMonitorWidget(QWidget):
    """Independent floating CPU, RAM and battery monitor."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.drag_position = None

        self.setWindowTitle("Widget System Monitor")
        self.setFixedSize(330, 245)

        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setStyleSheet("""
            QWidget {
                background-color: #29362C;
                color: #F5F1E9;
                font-family: "Segoe UI";
                border: 1px solid #485A48;
                border-radius: 15px;
            }

            QLabel {
                border: none;
            }

            QLabel#Header {
                color: #C3D0BC;
                font-size: 10px;
                font-weight: bold;
            }

            QLabel#MetricTitle {
                color: #C3D0BC;
                font-size: 11px;
                font-weight: bold;
            }

            QLabel#MetricValue {
                color: #F5F1E9;
                font-size: 13px;
                font-weight: bold;
            }

            QLabel#Footer {
                color: #AAB9A3;
                font-size: 10px;
            }

            QPushButton#Close {
                background-color: transparent;
                color: #C3D0BC;
                border: none;
                font-size: 17px;
                padding: 2px 7px;
            }

            QPushButton#Close:hover {
                background-color: #754B46;
                color: white;
            }

            QProgressBar {
                background-color: #465448;
                border: none;
                border-radius: 4px;
                height: 9px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: #A8BD91;
                border-radius: 4px;
            }
        """)

        self.build_interface()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)

        self.update_metrics()

    def build_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(17, 12, 17, 13)
        layout.setSpacing(10)

        header = QHBoxLayout()

        heading = QLabel("MOCHI  /  SYSTEM")
        heading.setObjectName("Header")

        close_button = QPushButton("X")
        close_button.setObjectName("Close")
        close_button.setFixedSize(27, 25)
        close_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        close_button.clicked.connect(self.hide)

        header.addWidget(heading)
        header.addStretch()
        header.addWidget(close_button)

        layout.addLayout(header)

        # CPU section
        cpu_row = QHBoxLayout()

        cpu_title = QLabel("CPU Usage")
        cpu_title.setObjectName("MetricTitle")

        self.cpu_value = QLabel("0%")
        self.cpu_value.setObjectName("MetricValue")

        cpu_row.addWidget(cpu_title)
        cpu_row.addStretch()
        cpu_row.addWidget(self.cpu_value)

        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setValue(0)
        self.cpu_bar.setTextVisible(False)

        layout.addLayout(cpu_row)
        layout.addWidget(self.cpu_bar)

        # RAM section
        ram_row = QHBoxLayout()

        ram_title = QLabel("Memory Usage")
        ram_title.setObjectName("MetricTitle")

        self.ram_value = QLabel("0%")
        self.ram_value.setObjectName("MetricValue")

        ram_row.addWidget(ram_title)
        ram_row.addStretch()
        ram_row.addWidget(self.ram_value)

        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        self.ram_bar.setValue(0)
        self.ram_bar.setTextVisible(False)

        layout.addLayout(ram_row)
        layout.addWidget(self.ram_bar)

        # Battery section
        battery_row = QHBoxLayout()

        battery_title = QLabel("Battery")
        battery_title.setObjectName("MetricTitle")

        self.battery_value = QLabel("Checking...")
        self.battery_value.setObjectName("MetricValue")

        battery_row.addWidget(battery_title)
        battery_row.addStretch()
        battery_row.addWidget(self.battery_value)

        self.battery_bar = QProgressBar()
        self.battery_bar.setRange(0, 100)
        self.battery_bar.setValue(0)
        self.battery_bar.setTextVisible(False)

        layout.addLayout(battery_row)
        layout.addWidget(self.battery_bar)

        self.footer = QLabel("Updating every second")
        self.footer.setObjectName("Footer")

        layout.addWidget(self.footer)

    def update_metrics(self):
        """Refresh CPU, memory and battery information."""

        try:
            cpu = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()

            self.cpu_value.setText(f"{cpu:.0f}%")
            self.cpu_bar.setValue(round(cpu))

            self.ram_value.setText(
                f"{memory.percent:.0f}%"
            )
            self.ram_bar.setValue(round(memory.percent))

        except (OSError, RuntimeError):
            self.cpu_value.setText("Unavailable")
            self.ram_value.setText("Unavailable")

        # Battery information may not exist on desktop PCs.
        try:
            battery = psutil.sensors_battery()
        except (AttributeError, OSError):
            battery = None

        if battery is None:
            self.battery_value.setText("Not detected")
            self.battery_bar.setValue(0)
            self.battery_bar.setEnabled(False)
            self.footer.setText(
                "CPU and memory update every second"
            )
            return

        self.battery_bar.setEnabled(True)

        percentage = round(battery.percent)
        self.battery_bar.setValue(percentage)

        if battery.power_plugged:
            status = "Charging"
        else:
            status = "On battery"

        self.battery_value.setText(
            f"{percentage}%  |  {status}"
        )

        self.footer.setText(
            "CPU, memory and battery update every second"
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
