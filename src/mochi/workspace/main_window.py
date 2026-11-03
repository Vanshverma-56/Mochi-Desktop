
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QStackedWidget,
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve

from mochi.workspace.pages.dashboard_page import DashboardPage
from mochi.workspace.pages.calendar_page import CalendarPage
from mochi.workspace.pages.tasks_page import TasksPage
from mochi.workspace.pages.notes_page import NotesPage
from mochi.workspace.pages.logbook_page import LogbookPage
from mochi.workspace.pages.focus_page import FocusPage
from mochi.workspace.pages.settings_page import SettingsPage


class MainWindow(QMainWindow):
    def __init__(self, task_service, calendar_service, note_service):
        super().__init__()

        self.task_service = task_service
        self.calendar_service = calendar_service
        self.note_service = note_service

        self.sidebar_expanded = True
        self.sidebar_expanded_width = 215
        self.sidebar_collapsed_width = 76

        self.setWindowTitle("Mochi Workspace")
        self.resize(1200, 760)
        self.setMinimumSize(950, 600)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F1E9;
            }

            QLabel {
                color: #292B28;
            }

            QFrame#Sidebar {
                background-color: #292E29;
                border-radius: 18px;
            }

            QLabel#Brand {
                color: #F5F1E9;
                font-size: 27px;
                font-weight: bold;
            }

            QPushButton#SidebarToggle {
                color: #D8D8CE;
                background-color: transparent;
                border: none;
                border-radius: 9px;
                font-size: 21px;
                font-weight: bold;
                padding: 8px;
            }

            QPushButton#SidebarToggle:hover {
                background-color: #41483F;
                color: white;
            }

            QPushButton#NavButton {
                color: #D8D8CE;
                background-color: transparent;
                border: none;
                border-radius: 10px;
                padding: 13px;
                text-align: left;
                font-size: 14px;
            }

            QPushButton#NavButton:hover {
                background-color: #41483F;
                color: white;
            }

            QPushButton#NavButton:checked {
                background-color: #596B55;
                color: white;
                font-weight: bold;
            }
        """)

        self.build_interface()

    def build_interface(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(18)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setMinimumWidth(self.sidebar_collapsed_width)
        self.sidebar.setMaximumWidth(self.sidebar_expanded_width)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(12, 20, 12, 20)
        sidebar_layout.setSpacing(12)

        # Sidebar header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.brand = QLabel("mochi 🐾")
        self.brand.setObjectName("Brand")

        self.toggle_button = QPushButton("‹")
        self.toggle_button.setObjectName("SidebarToggle")
        self.toggle_button.setFixedSize(38, 38)
        self.toggle_button.setToolTip("Collapse sidebar")
        self.toggle_button.clicked.connect(self.toggle_sidebar)

        header_layout.addWidget(self.brand)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_button)

        sidebar_layout.addLayout(header_layout)
        sidebar_layout.addSpacing(20)

        # Page definitions
        self.pages = {
            "Dashboard": DashboardPage(
                self.task_service,
                self.change_page,
            ),
            "Calendar": CalendarPage(self.calendar_service),
            "Tasks": TasksPage(self.task_service),
            "Notes": NotesPage(self.note_service),
            "Logbook": LogbookPage(),
            "Focus": FocusPage(),
            "Settings": SettingsPage(),
        }

        self.stack = QStackedWidget()

        for page in self.pages.values():
            self.stack.addWidget(page)

        # Navigation definitions
        navigation = [
            ("⌂", "Dashboard"),
            ("▦", "Calendar"),
            ("✓", "Tasks"),
            ("✎", "Notes"),
            ("▤", "Logbook"),
            ("◷", "Focus"),
            ("⚙", "Settings"),
        ]

        self.nav_buttons = {}
        self.navigation_data = {}

        for icon, page_name in navigation:
            button = QPushButton(f"{icon}   {page_name}")
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)

            button.clicked.connect(
                lambda checked=False, name=page_name:
                    self.change_page(name)
            )

            sidebar_layout.addWidget(button)

            self.nav_buttons[page_name] = button
            self.navigation_data[page_name] = icon

        sidebar_layout.addStretch()

        self.version_label = QLabel("MOCHI  •  VERSION 0.1")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label.setStyleSheet(
            "color: #A6A99C; font-size: 10px;"
        )

        sidebar_layout.addWidget(self.version_label)

        # Main content
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack, 1)

        # Sidebar width animation
        self.sidebar_animation = QPropertyAnimation(
            self.sidebar,
            b"maximumWidth",
        )
        self.sidebar_animation.setDuration(220)
        self.sidebar_animation.setEasingCurve(
            QEasingCurve.Type.InOutCubic
        )

        # Open Dashboard by default
        self.change_page("Dashboard")

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded

        self.sidebar_animation.stop()

        if self.sidebar_expanded:
            target_width = self.sidebar_expanded_width

            self.brand.setVisible(True)
            self.version_label.setVisible(True)

            self.toggle_button.setText("‹")
            self.toggle_button.setToolTip("Collapse sidebar")

        else:
            target_width = self.sidebar_collapsed_width

            self.brand.setVisible(False)
            self.version_label.setVisible(False)

            self.toggle_button.setText("›")
            self.toggle_button.setToolTip("Expand sidebar")

        # Update navigation labels and tooltips
        for page_name, button in self.nav_buttons.items():
            icon = self.navigation_data[page_name]

            if self.sidebar_expanded:
                button.setText(f"{icon}   {page_name}")
                button.setToolTip("")
                button.setStyleSheet(
                    "QPushButton#NavButton { text-align: left; }"
                )
            else:
                button.setText(icon)
                button.setToolTip(page_name)
                button.setStyleSheet(
                    "QPushButton#NavButton { text-align: center; }"
                )

        # Animate sidebar width
        self.sidebar_animation.setStartValue(
            self.sidebar.width()
        )
        self.sidebar_animation.setEndValue(target_width)
        self.sidebar_animation.start()

    def change_page(self, page_name):
        if page_name not in self.pages:
            return

        selected_page = self.pages[page_name]

        self.stack.setCurrentWidget(selected_page)

        for name, button in self.nav_buttons.items():
            button.setChecked(name == page_name)
