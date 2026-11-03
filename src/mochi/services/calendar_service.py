
from datetime import datetime

from mochi.database.connection import Database


class CalendarService:
    """Handles all calendar event-related database operations."""

    def __init__(self, database: Database):
        self.database = database

    @staticmethod
    def _validate_event(title, start_datetime, end_datetime=None):
        title = title.strip()

        if not title:
            raise ValueError("Event title cannot be empty.")

        try:
            start = datetime.fromisoformat(start_datetime)
        except (TypeError, ValueError):
            raise ValueError("A valid event start date and time is required.")

        if end_datetime is not None:
            try:
                end = datetime.fromisoformat(end_datetime)
            except (TypeError, ValueError):
                raise ValueError("Invalid event end date and time.")

            if end <= start:
                raise ValueError("Event end must be after its start.")

        return title

    def create_event(
        self,
        title,
        start_datetime,
        end_datetime=None,
        description="",
        category="General",
    ):
        title = self._validate_event(
            title,
            start_datetime,
            end_datetime,
        )

        now = datetime.now().isoformat(timespec="seconds")

        connection = self.database.connect()

        cursor = connection.execute(
            """
            INSERT INTO calendar_events (
                title,
                description,
                start_datetime,
                end_datetime,
                category,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                description,
                start_datetime,
                end_datetime,
                category,
                now,
            ),
        )

        connection.commit()

        return self.get_event(cursor.lastrowid)

    def get_event(self, event_id):
        connection = self.database.connect()

        row = connection.execute(
            "SELECT * FROM calendar_events WHERE id = ?",
            (event_id,),
        ).fetchone()

        return dict(row) if row else None

    def get_all_events(self):
        connection = self.database.connect()

        rows = connection.execute(
            """
            SELECT * FROM calendar_events
            ORDER BY start_datetime ASC
            """
        ).fetchall()

        return [dict(row) for row in rows]

    
    def get_events_between(self, start_datetime, end_datetime):
        """Return events that overlap the requested date-time range."""

        connection = self.database.connect()

        rows = connection.execute(
            """
            SELECT * FROM calendar_events
            WHERE (
                start_datetime <= ?
                AND end_datetime >= ?
            )
            OR (
                end_datetime IS NULL
                AND DATE(start_datetime) BETWEEN DATE(?) AND DATE(?)
            )
            ORDER BY start_datetime ASC
            """,
            (
                end_datetime,
                start_datetime,
                start_datetime,
                end_datetime,
            ),
        ).fetchall()

        return [dict(row) for row in rows]


    def update_event(
        self,
        event_id,
        title,
        start_datetime,
        end_datetime=None,
        description="",
        category="General",
    ):
        title = self._validate_event(
            title,
            start_datetime,
            end_datetime,
        )

        connection = self.database.connect()

        cursor = connection.execute(
            """
            UPDATE calendar_events
            SET title = ?,
                description = ?,
                start_datetime = ?,
                end_datetime = ?,
                category = ?
            WHERE id = ?
            """,
            (
                title,
                description,
                start_datetime,
                end_datetime,
                category,
                event_id,
            ),
        )

        connection.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_event(event_id)

    def delete_event(self, event_id):
        connection = self.database.connect()

        cursor = connection.execute(
            "DELETE FROM calendar_events WHERE id = ?",
            (event_id,),
        )

        connection.commit()

        return cursor.rowcount > 0
