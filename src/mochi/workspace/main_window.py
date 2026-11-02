
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
from PySide6.QtCore import Qt

from mochi.workspace.pages.dashboard_page import DashboardPage
from mochi.workspace.pages.calendar_page import CalendarPage
from mochi.workspace.pages.tasks_page import TasksPage
from mochi.workspace.pages.notes_page import NotesPage
from mochi.workspace.pages.logbook_page import LogbookPage
from mochi.workspace.pages.focus_page import FocusPage
from mochi.workspace.pages.settings_page import SettingsPage


class MainWindow(QMainWindow):
    def __init__(self, task_service):
        super().__init__()

        self.task_service = task_service

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
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(215)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 25, 16, 20)
        sidebar_layout.setSpacing(12)

        brand = QLabel("mochi 🐾")
        brand.setObjectName("Brand")

        sidebar_layout.addWidget(brand)
        sidebar_layout.addSpacing(28)

        # Page definitions
        self.pages = {
            "Dashboard": DashboardPage(
    self.task_service,
    self.change_page,
),
            "Calendar": CalendarPage(),
            "Tasks": TasksPage(self.task_service),
            "Notes": NotesPage(),
            "Logbook": LogbookPage(),
            "Focus": FocusPage(),
            "Settings": SettingsPage(),
        }

        self.stack = QStackedWidget()

        for page in self.pages.values():
            self.stack.addWidget(page)

        # Navigation buttons
        self.nav_buttons = {}

        navigation = [
            ("⌂   Dashboard", "Dashboard"),
            ("▦   Calendar", "Calendar"),
            ("✓   Tasks", "Tasks"),
            ("✎   Notes", "Notes"),
            ("▤   Logbook", "Logbook"),
            ("◷   Focus", "Focus"),
            ("⚙   Settings", "Settings"),
        ]

        for label, page_name in navigation:
            button = QPushButton(label)
            button.setObjectName("NavButton")
            button.setCheckable(True)

            button.clicked.connect(
                lambda checked=False, name=page_name:
                    self.change_page(name)
            )

            sidebar_layout.addWidget(button)
            self.nav_buttons[page_name] = button

        sidebar_layout.addStretch()

        version = QLabel("MOCHI  •  VERSION 0.1")
        version.setStyleSheet(
            "color: #A6A99C; font-size: 10px;"
        )
        sidebar_layout.addWidget(version)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, 1)

        # Open Dashboard by default
        self.change_page("Dashboard")

    def change_page(self, page_name):
        if page_name not in self.pages:
            return

        selected_page = self.pages[page_name]

        self.stack.setCurrentWidget(selected_page)

        for name, button in self.nav_buttons.items():
            button.setChecked(name == page_name)
