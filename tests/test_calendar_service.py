
import pytest

from mochi.database.connection import Database
from mochi.database.schema import initialise_database
from mochi.services.calendar_service import CalendarService


@pytest.fixture
def calendar_service(tmp_path):
    database = Database()
    database.database_path = tmp_path / "test_calendar.db"

    initialise_database(database)

    service = CalendarService(database)

    yield service

    database.close()


def test_create_and_retrieve_event(calendar_service):
    event = calendar_service.create_event(
        title="Project Meeting",
        start_datetime="2026-11-10T10:00:00",
        end_datetime="2026-11-10T11:00:00",
        description="Discuss project progress",
        category="Work",
    )

    assert event["id"] is not None
    assert event["title"] == "Project Meeting"
    assert event["description"] == "Discuss project progress"
    assert event["category"] == "Work"

    retrieved = calendar_service.get_event(event["id"])

    assert retrieved == event


def test_get_all_events_orders_by_start_time(calendar_service):
    calendar_service.create_event(
        "Later Meeting",
        "2026-11-12T14:00:00",
    )

    calendar_service.create_event(
        "Earlier Meeting",
        "2026-11-10T09:00:00",
    )

    events = calendar_service.get_all_events()

    assert [event["title"] for event in events] == [
        "Earlier Meeting",
        "Later Meeting",
    ]


def test_get_events_between_returns_overlapping_events(calendar_service):
    calendar_service.create_event(
        "Morning Meeting",
        "2026-11-10T09:00:00",
        "2026-11-10T10:00:00",
    )

    calendar_service.create_event(
        "Afternoon Meeting",
        "2026-11-10T14:00:00",
        "2026-11-10T15:00:00",
    )

    calendar_service.create_event(
        "All Day Reminder",
        "2026-11-10T00:00:00",
    )

    events = calendar_service.get_events_between(
        "2026-11-10T08:00:00",
        "2026-11-10T12:00:00",
    )

    assert [event["title"] for event in events] == [
        "All Day Reminder",
        "Morning Meeting",
    ]


def test_update_event(calendar_service):
    event = calendar_service.create_event(
        "Original Event",
        "2026-11-10T10:00:00",
    )

    updated = calendar_service.update_event(
        event_id=event["id"],
        title="Updated Event",
        start_datetime="2026-11-11T11:00:00",
        end_datetime="2026-11-11T12:00:00",
        description="Updated description",
        category="Personal",
    )

    assert updated["title"] == "Updated Event"
    assert updated["start_datetime"] == "2026-11-11T11:00:00"
    assert updated["description"] == "Updated description"
    assert updated["category"] == "Personal"


def test_delete_event(calendar_service):
    event = calendar_service.create_event(
        "Event to Delete",
        "2026-11-10T10:00:00",
    )

    assert calendar_service.delete_event(event["id"]) is True
    assert calendar_service.get_event(event["id"]) is None
    assert calendar_service.delete_event(event["id"]) is False


def test_create_event_rejects_empty_title(calendar_service):
    with pytest.raises(ValueError):
        calendar_service.create_event(
            "   ",
            "2026-11-10T10:00:00",
        )


def test_create_event_rejects_invalid_datetime(calendar_service):
    with pytest.raises(ValueError):
        calendar_service.create_event(
            "Invalid Event",
            "not-a-date",
        )


def test_create_event_rejects_end_before_start(calendar_service):
    with pytest.raises(ValueError):
        calendar_service.create_event(
            "Invalid Event",
            "2026-11-10T12:00:00",
            "2026-11-10T11:00:00",
        )


def test_update_nonexistent_event_returns_none(calendar_service):
    result = calendar_service.update_event(
        event_id=999,
        title="Missing Event",
        start_datetime="2026-11-10T10:00:00",
    )

    assert result is None
