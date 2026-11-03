
import pytest

from mochi.database.connection import Database
from mochi.database.schema import initialise_database
from mochi.services.note_service import NoteService


@pytest.fixture
def note_service(tmp_path):
    db = Database()
    db.database_path = tmp_path / "test_notes.db"

    initialise_database(db)

    service = NoteService(db)

    yield service

    db.close()


def test_create_and_retrieve_note(note_service):
    note = note_service.create_note(
        title="Mochi project ideas",
        content="Plan the Notes page.",
        category="Development",
    )

    retrieved = note_service.get_note(note["id"])

    assert retrieved is not None
    assert retrieved["title"] == "Mochi project ideas"
    assert retrieved["content"] == "Plan the Notes page."
    assert retrieved["category"] == "Development"


def test_create_note_rejects_empty_title(note_service):
    with pytest.raises(ValueError):
        note_service.create_note(title="   ")


def test_update_note(note_service):
    note = note_service.create_note(
        title="Original note",
        content="Original content",
        category="Personal",
    )

    updated = note_service.update_note(
        note["id"],
        title="Updated note",
        content="Updated content",
        category="Development",
    )

    assert updated["title"] == "Updated note"
    assert updated["content"] == "Updated content"
    assert updated["category"] == "Development"


def test_update_note_rejects_empty_title(note_service):
    note = note_service.create_note(title="Existing note")

    with pytest.raises(ValueError):
        note_service.update_note(
            note["id"],
            title="   ",
        )


def test_delete_note(note_service):
    note = note_service.create_note(
        title="Note to delete",
    )

    deleted = note_service.delete_note(note["id"])

    assert deleted is True
    assert note_service.get_note(note["id"]) is None


def test_get_all_notes(note_service):
    note_service.create_note(title="First note")
    note_service.create_note(title="Second note")

    notes = note_service.get_all_notes()

    assert len(notes) == 2


def test_search_notes(note_service):
    note_service.create_note(
        title="Python development",
        content="Build a desktop application.",
        category="Programming",
    )

    note_service.create_note(
        title="Weekend plans",
        content="Read a book.",
        category="Personal",
    )

    results = note_service.search_notes("Python")

    assert len(results) == 1
    assert results[0]["title"] == "Python development"


def test_search_notes_in_content_and_category(note_service):
    note_service.create_note(
        title="First note",
        content="Remember the database design.",
        category="Development",
    )

    content_results = note_service.search_notes("database")
    category_results = note_service.search_notes("Development")

    assert len(content_results) == 1
    assert len(category_results) == 1


def test_search_empty_query_returns_all_notes(note_service):
    note_service.create_note(title="First note")
    note_service.create_note(title="Second note")

    results = note_service.search_notes("   ")

    assert len(results) == 2
