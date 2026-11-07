import pytest

from mochi.database.connection import Database
from mochi.database.schema import initialise_database
from mochi.services.logbook_service import LogbookService


@pytest.fixture
def logbook_service(tmp_path):
    database = Database()
    database.database_path = tmp_path / "test_mochi.db"

    initialise_database(database)

    yield LogbookService(database)

    database.close()


def test_save_and_get_entry(logbook_service):
    saved = logbook_service.save_entry(
        "2026-11-06",
        "A productive day",
        "Worked on Mochi.",
    )

    assert saved["entry_date"] == "2026-11-06"
    assert saved["title"] == "A productive day"
    assert saved["content"] == "Worked on Mochi."

    entry = logbook_service.get_entry("2026-11-06")

    assert entry["id"] == saved["id"]


def test_saving_same_date_updates_existing_entry(logbook_service):
    first = logbook_service.save_entry(
        "2026-11-06",
        "First title",
        "First content",
    )

    second = logbook_service.save_entry(
        "2026-11-06",
        "Updated title",
        "Updated content",
    )

    assert second["id"] == first["id"]
    assert second["title"] == "Updated title"
    assert second["content"] == "Updated content"
    assert len(logbook_service.get_all_entries()) == 1


def test_get_entry_returns_none_for_missing_date(logbook_service):
    assert logbook_service.get_entry("2026-11-06") is None


def test_get_all_entries_returns_entries_newest_first(logbook_service):
    logbook_service.save_entry("2026-11-04", "Day one", "Entry one")
    logbook_service.save_entry("2026-11-06", "Day two", "Entry two")
    logbook_service.save_entry("2026-11-05", "Day three", "Entry three")

    entries = logbook_service.get_all_entries()

    assert [entry["entry_date"] for entry in entries] == [
        "2026-11-06",
        "2026-11-05",
        "2026-11-04",
    ]


def test_delete_entry(logbook_service):
    logbook_service.save_entry(
        "2026-11-06",
        "A day",
        "Some thoughts.",
    )

    assert logbook_service.delete_entry("2026-11-06") is True
    assert logbook_service.get_entry("2026-11-06") is None


def test_delete_missing_entry_returns_false(logbook_service):
    assert logbook_service.delete_entry("2026-11-06") is False


@pytest.mark.parametrize("invalid_date", ["", "06-11-2026", "not-a-date"])
def test_invalid_date_is_rejected(logbook_service, invalid_date):
    with pytest.raises(ValueError):
        logbook_service.get_entry(invalid_date)


def test_non_text_content_is_rejected(logbook_service):
    with pytest.raises(ValueError):
        logbook_service.save_entry(
            "2026-11-06",
            "Title",
            None,
        )