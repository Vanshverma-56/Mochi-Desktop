
from datetime import datetime

from mochi.database.connection import Database


class TaskService:
    """Handles all task-related database operations."""

    VALID_PRIORITIES = {"Low", "Medium", "High"}

    def __init__(self, database: Database):
        self.database = database

    def create_task(
        self,
        title,
        description="",
        priority="Medium",
        category="General",
        due_date=None,
    ):
        title = title.strip()

        if not title:
            raise ValueError("Task title cannot be empty.")

        if priority not in self.VALID_PRIORITIES:
            raise ValueError("Invalid task priority.")

        now = datetime.now().isoformat(timespec="seconds")

        connection = self.database.connect()

        cursor = connection.execute(
            """
            INSERT INTO tasks (
                title, description, priority, category,
                due_date, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title, description, priority, category,
                due_date, now, now,
            ),
        )

        connection.commit()

        return self.get_task(cursor.lastrowid)

    def get_task(self, task_id):
        connection = self.database.connect()

        row = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        return dict(row) if row else None

    def get_all_tasks(self):
        connection = self.database.connect()

        rows = connection.execute(
            """
            SELECT * FROM tasks
            ORDER BY is_completed ASC, created_at DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]

    def update_task(
        self,
        task_id,
        title,
        description="",
        priority="Medium",
        category="General",
        due_date=None,
    ):
        title = title.strip()

        if not title:
            raise ValueError("Task title cannot be empty.")

        if priority not in self.VALID_PRIORITIES:
            raise ValueError("Invalid task priority.")

        now = datetime.now().isoformat(timespec="seconds")

        connection = self.database.connect()

        cursor = connection.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, priority = ?,
                category = ?, due_date = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                title, description, priority,
                category, due_date, now, task_id,
            ),
        )

        connection.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_task(task_id)

    def delete_task(self, task_id):
        connection = self.database.connect()

        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )

        connection.commit()

        return cursor.rowcount > 0

    def set_task_completed(self, task_id, completed=True):
        connection = self.database.connect()

        cursor = connection.execute(
            """
            UPDATE tasks
            SET is_completed = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                int(completed),
                datetime.now().isoformat(timespec="seconds"),
                task_id,
            ),
        )

        connection.commit()

        return cursor.rowcount > 0
