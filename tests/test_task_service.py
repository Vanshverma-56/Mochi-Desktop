import pytest

from mochi.database.connection import Database
from mochi.database.schema import initialise_database
from mochi.services.task_service import TaskService


@pytest.fixture
def task_service(tmp_path):
    db = Database()
    db.database_path = tmp_path / "test_tasks.db"

    initialise_database(db)
    service = TaskService(db)

    yield service

    db.close()


def test_create_and_retrieve_task(task_service):
    task = task_service.create_task(
        title="Complete Mochi development",
        description="Test task creation.",
        priority="High",
        category="Development",
    )

    retrieved = task_service.get_task(task["id"])

    assert retrieved is not None
    assert retrieved["title"] == "Complete Mochi development"
    assert retrieved["priority"] == "High"
    assert retrieved["category"] == "Development"


def test_update_task(task_service):
    task = task_service.create_task(
        title="Original title",
        priority="Low",
        category="Development",
    )

    updated = task_service.update_task(
        task["id"],
        title="Updated title",
        description="Updated description.",
        priority="Medium",
        category="Development",
    )

    assert updated["title"] == "Updated title"
    assert updated["description"] == "Updated description."
    assert updated["priority"] == "Medium"


def test_complete_task(task_service):
    task = task_service.create_task(
        title="Test completion",
        priority="Medium",
        category="Testing",
    )

    task_service.set_task_completed(task["id"], True)

    completed = task_service.get_task(task["id"])

    assert bool(completed["is_completed"]) is True


def test_delete_task(task_service):
    task = task_service.create_task(
        title="Test deletion",
        priority="Low",
        category="Testing",
    )

    deleted = task_service.delete_task(task["id"])

    assert deleted is True
    assert task_service.get_task(task["id"]) is None


def test_get_all_tasks(task_service):
    task_service.create_task(
        title="First task",
        priority="High",
        category="Testing",
    )
    task_service.create_task(
        title="Second task",
        priority="Low",
        category="Testing",
    )

    tasks = task_service.get_all_tasks()

    assert len(tasks) == 2
