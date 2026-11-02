from mochi.database.connection import Database
from mochi.database.schema import initialise_database


def test_database_initialises_required_tables(tmp_path):
    db = Database()
    db.database_path = tmp_path / "test_mochi.db"

    try:
        initialise_database(db)

        rows = db.connect().execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' ORDER BY name"
        ).fetchall()

        table_names = {row["name"] for row in rows}

        expected_tables = {
            "tasks",
            "calendar_events",
            "notes",
            "logbook_entries",
            "focus_sessions",
            "preferences",
        }

        assert expected_tables.issubset(table_names)
    finally:
        db.close()
