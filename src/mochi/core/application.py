from PySide6.QtWidgets import QApplication

from mochi.companion.pet_window import PetWindow
from mochi.companion.pomodoro import (
    PomodoroController,
    FloatingTimerWindow,
)
from mochi.database.connection import Database
from mochi.database.schema import initialise_database
from mochi.services.calendar_service import CalendarService
from mochi.services.focus_service import FocusService
from mochi.services.logbook_service import LogbookService
from mochi.services.note_service import NoteService
from mochi.services.task_service import TaskService
from mochi.widgets.desktop_widgets import DesktopWidgetsWindow
from mochi.workspace.main_window import MainWindow
from mochi.core.launcher import LauncherWindow
from mochi.services.music_service import MusicService
from mochi.services.music_player import MusicPlaybackController


class MochiApplication:
    def __init__(self):
        self.app = QApplication.instance() or QApplication([])

        self.app.setApplicationName("Widget")
        self.app.setOrganizationName("Mochi")
        self.app.setQuitOnLastWindowClosed(True)

        self._shutting_down = False

        # Database and services
        self.database = Database()
        initialise_database(self.database)

        self.task_service = TaskService(self.database)
        self.calendar_service = CalendarService(self.database)
        self.note_service = NoteService(self.database)
        self.logbook_service = LogbookService(self.database)
        self.focus_service = FocusService(self.database)
        self.music_service = MusicService(self.database)
        self.music_player = MusicPlaybackController()

        # Focus timer
        self.pomodoro = PomodoroController(self.focus_service)
        self.floating_timer = FloatingTimerWindow(self.pomodoro)

        # Main components
        self.workspace = MainWindow(
            self.task_service,
            self.calendar_service,
            self.note_service,
            self.logbook_service,
            self.focus_service,
            self.pomodoro,
            self.floating_timer,
        )

        self.floating_timer.set_workspace_window(self.workspace)

        self.companion = PetWindow()
        self.desktop_widgets = DesktopWidgetsWindow(
            self.calendar_service,
            self.music_service,
            self.music_player,
        )

        self.desktop_widgets.calendar_widget.events_changed.connect(
            self.workspace.refresh_calendar
        )

        # Track whether each component has been launched before.
        self.dashboard_started = False
        self.widgets_started = False
        self.companion_started = False

        # Persistent launcher
        self.launcher = LauncherWindow(self)

        self.app.aboutToQuit.connect(self.shutdown)

    def show_dashboard(self):
        self.dashboard_started = True
        self.workspace.showNormal()
        self.workspace.raise_()
        self.workspace.activateWindow()

    def show_desktop_widgets(self):
        self.widgets_started = True
        self.desktop_widgets.showNormal()
        self.desktop_widgets.raise_()
        self.desktop_widgets.activateWindow()

    def show_companion(self):
        self.companion_started = True
        self.companion.show()
        self.companion.raise_()

    def launch_all(self):
        self.show_dashboard()
        self.show_desktop_widgets()
        self.show_companion()

    def exit_widget(self):
        self.shutdown()

        self.music_player.stop()
        self.launcher.allow_close = True
        self.launcher.close()

        self.app.quit()

    def shutdown(self):
        if self._shutting_down:
            return

        self._shutting_down = True

        # Stop Focus and close its independent floating overlay.
        self.pomodoro.stop()
        self.floating_timer.shutdown()

        # Close all application components.
        self.workspace.hide()
        self.desktop_widgets.shutdown()
        self.companion.close()

        # Close the database after all components have stopped.
        self.database.close()

    def run(self):
        self.launcher.show()
        return self.app.exec()