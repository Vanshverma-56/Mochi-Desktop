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


class LauncherWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.allow_close = False
        self.setWindowTitle("Widget Launcher")
        self.setFixedSize(390, 490)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F1E9;
            }
            QLabel {
                color: #292B28;
            }
            QLabel#Heading {
                font-size: 27px;
                font-weight: bold;
            }
            QLabel#Subtitle {
                color: #77796F;
                font-size: 12px;
            }
            QFrame#ComponentCard {
                background-color: #FFFCF6;
                border: 1px solid #E9E2D6;
                border-radius: 13px;
            }
            QLabel#ComponentTitle {
                font-size: 14px;
                font-weight: bold;
            }
            QLabel#ComponentStatus {
                color: #77796F;
                font-size: 11px;
            }
            QPushButton {
                background-color: #596B55;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 9px 13px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #465641;
            }
            QPushButton#Secondary {
                background-color: #EAE5DA;
                color: #454940;
            }
            QPushButton#Secondary:hover {
                background-color: #DDD7CA;
            }
            QPushButton#Exit {
                background-color: #8B514B;
            }
            QPushButton#Exit:hover {
                background-color: #75413C;
            }
        """)

        self.build_interface()

        self.status_timer = QTimer(self)
        self.status_timer.setInterval(500)
        self.status_timer.timeout.connect(self.refresh_status)
        self.status_timer.start()

    def build_interface(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(23, 22, 23, 20)
        layout.setSpacing(13)

        heading = QLabel("Widget")
        heading.setObjectName("Heading")

        subtitle = QLabel("Your desktop, your space.")
        subtitle.setObjectName("Subtitle")

        layout.addWidget(heading)
        layout.addWidget(subtitle)
        layout.addSpacing(7)

        self.components = {}

        self.add_component(
            layout,
            "dashboard",
            "Dashboard",
            "Your productivity workspace",
            self.controller.show_dashboard,
        )

        self.add_component(
            layout,
            "widgets",
            "Desktop Widgets",
            "Your desktop tools and mini-widgets",
            self.controller.show_desktop_widgets,
        )

        self.add_component(
            layout,
            "companion",
            "Mochi Companion",
            "Your floating desktop companion",
            self.controller.show_companion,
        )

        layout.addStretch()

        launch_all = QPushButton("Launch All")
        launch_all.setFixedHeight(39)
        launch_all.clicked.connect(self.controller.launch_all)
        layout.addWidget(launch_all)

        exit_button = QPushButton("Exit Widget")
        exit_button.setObjectName("Exit")
        exit_button.setFixedHeight(36)
        exit_button.clicked.connect(self.controller.exit_widget)
        layout.addWidget(exit_button)

        footer = QLabel("VERSION 0.1  •  MANUAL LAUNCH")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            "color: #96978D; font-size: 9px; padding-top: 5px;"
        )
        layout.addWidget(footer)

    def add_component(
        self, parent_layout, key, title, description, launch_callback
    ):
        card = QFrame()
        card.setObjectName("ComponentCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 11, 14, 11)
        card_layout.setSpacing(5)

        top = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setObjectName("ComponentTitle")

        status_label = QLabel("Not launched")
        status_label.setObjectName("ComponentStatus")

        top.addWidget(title_label)
        top.addStretch()
        top.addWidget(status_label)

        description_label = QLabel(description)
        description_label.setObjectName("ComponentStatus")

        button = QPushButton("Launch")
        button.setObjectName("Secondary")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(launch_callback)

        card_layout.addLayout(top)
        card_layout.addWidget(description_label)
        card_layout.addWidget(button)

        parent_layout.addWidget(card)

        self.components[key] = {
            "status": status_label,
            "button": button,
        }

    def refresh_status(self):
        component_data = {
            "dashboard": (
                self.controller.workspace,
                self.controller.dashboard_started,
            ),
            "widgets": (
                self.controller.desktop_widgets,
                self.controller.widgets_started,
            ),
            "companion": (
                self.controller.companion,
                self.controller.companion_started,
            ),
        }

        for key, (window, started) in component_data.items():
            visible = window.isVisible()

            if visible:
                status = "Running"
                button_text = "Hide"
            elif started:
                status = "Hidden"
                button_text = "Show"
            else:
                status = "Not launched"
                button_text = "Launch"

            self.components[key]["status"].setText(status)
            self.components[key]["button"].setText(button_text)

    def closeEvent(self, event):
        if self.allow_close:
            event.accept()
        else:
            # Keep the launcher available in the Windows taskbar.
            event.ignore()
            self.showMinimized()