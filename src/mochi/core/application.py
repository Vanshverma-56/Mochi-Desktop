
from PySide6.QtWidgets import QApplication

from mochi.workspace.main_window import MainWindow
from mochi.companion.pet_window import PetWindow

from mochi.database.connection import Database
from mochi.database.schema import initialise_database
from mochi.services.task_service import TaskService


class MochiApplication:
    def __init__(self):
        self.app = QApplication.instance() or QApplication([])

        self.app.setApplicationName("Mochi")
        self.app.setOrganizationName("Mochi")

        # Initialise the local database.
        self.database = Database()
        initialise_database(self.database)

        # Create shared application services.
        self.task_service = TaskService(self.database)

        # Create application windows.
        self.workspace = MainWindow(self.task_service)
        self.companion = PetWindow()

        self.app.aboutToQuit.connect(self.database.close)

    def run(self):
        self.workspace.show()
        self.companion.show()

        return self.app.exec()
