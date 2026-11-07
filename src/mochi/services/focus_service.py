from datetime import date, datetime

from mochi.database.connection import Database


class FocusService:
    """Handles focus timer sessions and daily focus statistics."""

    VALID_SESSION_TYPES = {
        "Focus",
        "Short Break",
        "Long Break",
    }

    DEFAULT_DURATION = 25
    MAX_DURATION = 1440

    def __init__(self, database: Database):
        self.database = database

    @staticmethod
    def _validate_date(entry_date):
        if isinstance(entry_date, date):
            return entry_date.isoformat()

        try:
            return date.fromisoformat(entry_date).isoformat()
        except (TypeError, ValueError):
            raise ValueError("Date must be in YYYY-MM-DD format.")

    def start_session(
        self,
        duration_minutes=DEFAULT_DURATION,
        session_type="Focus",
    ):
        if (
            type(duration_minutes) is not int
            or not 1 <= duration_minutes <= self.MAX_DURATION
        ):
            raise ValueError(
                "Duration must be between 1 and 1440 minutes."
            )

        if session_type not in self.VALID_SESSION_TYPES:
            raise ValueError("Invalid focus session type.")

        connection = self.database.connect()

        active_session = connection.execute(
            """
            SELECT id
            FROM focus_sessions
            WHERE ended_at IS NULL
            ORDER BY started_at DESC
            LIMIT 1
            """
        ).fetchone()

        if active_session:
            raise ValueError(
                "A focus session is already in progress."
            )

        started_at = datetime.now().isoformat(timespec="seconds")

        cursor = connection.execute(
            """
            INSERT INTO focus_sessions (
                started_at,
                ended_at,
                duration_minutes,
                session_type,
                completed
            )
            VALUES (?, NULL, ?, ?, 0)
            """,
            (started_at, duration_minutes, session_type),
        )

        connection.commit()

        return self.get_session(cursor.lastrowid)

    def get_session(self, session_id):
        connection = self.database.connect()

        row = connection.execute(
            """
            SELECT *
            FROM focus_sessions
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()

        return dict(row) if row else None

    def get_active_session(self):
        connection = self.database.connect()

        row = connection.execute(
            """
            SELECT *
            FROM focus_sessions
            WHERE ended_at IS NULL
            ORDER BY started_at DESC
            LIMIT 1
            """
        ).fetchone()

        return dict(row) if row else None

    def end_session(self, session_id, completed=False):
        if type(completed) is not bool:
            raise ValueError("Completed must be True or False.")

        connection = self.database.connect()

        ended_at = datetime.now().isoformat(timespec="seconds")

        cursor = connection.execute(
            """
            UPDATE focus_sessions
            SET ended_at = ?, completed = ?
            WHERE id = ? AND ended_at IS NULL
            """,
            (ended_at, int(completed), session_id),
        )

        connection.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_session(session_id)

    def complete_session(self, session_id):
        """Mark an active session as successfully completed."""
        return self.end_session(session_id, completed=True)

    def interrupt_session(self, session_id):
        """End a session without counting it as completed."""
        return self.end_session(session_id, completed=False)

    def interrupt_active_session(self):
        """Recover a session left active after the application closed."""
        active_session = self.get_active_session()

        if active_session is None:
            return False

        self.interrupt_session(active_session["id"])
        return True
    def get_sessions(self, entry_date=None, limit=20):
        if type(limit) is not int or limit < 1:
            raise ValueError("Limit must be a positive integer.")

        connection = self.database.connect()

        if entry_date is not None:
            entry_date = self._validate_date(entry_date)

            rows = connection.execute(
                """
                SELECT *
                FROM focus_sessions
                WHERE substr(started_at, 1, 10) = ?
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (entry_date, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM focus_sessions
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in rows]

    def get_daily_summary(self, entry_date=None):
        if entry_date is None:
            entry_date = date.today().isoformat()
        else:
            entry_date = self._validate_date(entry_date)

        connection = self.database.connect()

        row = connection.execute(
            """
            SELECT
                COUNT(*) AS completed_sessions,
                COALESCE(SUM(duration_minutes), 0) AS focused_minutes
            FROM focus_sessions
            WHERE substr(started_at, 1, 10) = ?
              AND session_type = 'Focus'
              AND completed = 1
            """,
            (entry_date,),
        ).fetchone()

        return {
            "date": entry_date,
            "completed_sessions": row["completed_sessions"],
            "focused_minutes": row["focused_minutes"],
        }