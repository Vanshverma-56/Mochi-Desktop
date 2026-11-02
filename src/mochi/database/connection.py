
from pathlib import Path
import sqlite3

from PySide6.QtCore import QStandardPaths


class Database:
    """Manages Mochi's local SQLite database connection."""

    def __init__(self):
        app_data = Path(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation
            )
        )

        app_data.mkdir(parents=True, exist_ok=True)

        self.database_path = app_data / "mochi.db"
        self.connection = None

    def connect(self):
        """Create and return the database connection."""

        if self.connection is None:
            self.connection = sqlite3.connect(
                self.database_path
            )

            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")

        return self.connection

    def close(self):
        """Close the database connection safely."""

        if self.connection is not None:
            self.connection.close()
            self.connection = None
