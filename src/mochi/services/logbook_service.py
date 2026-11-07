from datetime import date, datetime

from mochi.database.connection import Database


class LogbookService:
    """Handles daily logbook database operations."""

    def __init__(self, database: Database):
        self.database = database

    @staticmethod
    def _validate_date(entry_date):
        try:
            return date.fromisoformat(entry_date).isoformat()
        except (TypeError, ValueError):
            raise ValueError("Please provide a valid date in YYYY-MM-DD format.")

    def get_entry(self, entry_date):
        entry_date = self._validate_date(entry_date)
        connection = self.database.connect()

        row = connection.execute(
            """
            SELECT * FROM logbook_entries
            WHERE entry_date = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (entry_date,),
        ).fetchone()

        return dict(row) if row else None

    def get_all_entries(self):
        connection = self.database.connect()

        rows = connection.execute(
            """
            SELECT * FROM logbook_entries
            ORDER BY entry_date DESC, id DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]

    def save_entry(self, entry_date, title="", content=""):
        entry_date = self._validate_date(entry_date)

        if not isinstance(title, str) or not isinstance(content, str):
            raise ValueError("The entry title and content must be text.")

        now = datetime.now().isoformat(timespec="seconds")
        connection = self.database.connect()

        existing = connection.execute(
            """
            SELECT id FROM logbook_entries
            WHERE entry_date = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (entry_date,),
        ).fetchone()

        if existing:
            connection.execute(
                """
                UPDATE logbook_entries
                SET title = ?, content = ?, updated_at = ?
                WHERE id = ?
                """,
                (title.strip(), content, now, existing["id"]),
            )
            entry_id = existing["id"]
        else:
            cursor = connection.execute(
                """
                INSERT INTO logbook_entries (
                    entry_date, title, content, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (entry_date, title.strip(), content, now, now),
            )
            entry_id = cursor.lastrowid

        connection.commit()

        row = connection.execute(
            "SELECT * FROM logbook_entries WHERE id = ?",
            (entry_id,),
        ).fetchone()

        return dict(row)

    def delete_entry(self, entry_date):
        entry_date = self._validate_date(entry_date)
        connection = self.database.connect()

        cursor = connection.execute(
            "DELETE FROM logbook_entries WHERE entry_date = ?",
            (entry_date,),
        )

        connection.commit()
        return cursor.rowcount > 0