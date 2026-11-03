
from datetime import datetime

from mochi.database.connection import Database


class NoteService:
    """Handles all note-related database operations."""

    def __init__(self, database: Database):
        self.database = database

    @staticmethod
    def _validate_note(title):
        title = title.strip()

        if not title:
            raise ValueError("Note title cannot be empty.")

        return title

    def create_note(
        self,
        title,
        content="",
        category="General",
    ):
        title = self._validate_note(title)

        now = datetime.now().isoformat(timespec="seconds")

        connection = self.database.connect()

        cursor = connection.execute(
            """
            INSERT INTO notes (
                title,
                content,
                category,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                title,
                content,
                category,
                now,
                now,
            ),
        )

        connection.commit()

        return self.get_note(cursor.lastrowid)

    def get_note(self, note_id):
        connection = self.database.connect()

        row = connection.execute(
            "SELECT * FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()

        return dict(row) if row else None

    def get_all_notes(self):
        connection = self.database.connect()

        rows = connection.execute(
            """
            SELECT * FROM notes
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]

    def search_notes(self, query):
        """Search note titles, content, and categories."""

        query = query.strip()

        if not query:
            return self.get_all_notes()

        connection = self.database.connect()

        search_term = f"%{query}%"

        rows = connection.execute(
            """
            SELECT * FROM notes
            WHERE title LIKE ?
               OR content LIKE ?
               OR category LIKE ?
            ORDER BY updated_at DESC, id DESC
            """,
            (
                search_term,
                search_term,
                search_term,
            ),
        ).fetchall()

        return [dict(row) for row in rows]

    def update_note(
        self,
        note_id,
        title,
        content="",
        category="General",
    ):
        title = self._validate_note(title)

        now = datetime.now().isoformat(timespec="seconds")

        connection = self.database.connect()

        cursor = connection.execute(
            """
            UPDATE notes
            SET title = ?,
                content = ?,
                category = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                title,
                content,
                category,
                now,
                note_id,
            ),
        )

        connection.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_note(note_id)

    def delete_note(self, note_id):
        connection = self.database.connect()

        cursor = connection.execute(
            "DELETE FROM notes WHERE id = ?",
            (note_id,),
        )

        connection.commit()

        return cursor.rowcount > 0
