from datetime import date
import pytest
from PySide6.QtWidgets import QApplication, QDialog

from mochi.database.connection import Database
from mochi.database.schema import initialise_database
from mochi.services.calendar_service import CalendarService
from mochi.workspace.pages.calendar_page import (
    CalendarPage,
    EventDialog,
    MochiMessageDialog,
)


@pytest.fixture(scope="session")
def qapp():
    """Ensure a single QApplication instance exists for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def calendar_service(tmp_path):
    """Create an isolated test database and calendar service."""
    db = Database()
    db.database_path = tmp_path / "test_calendar.db"
    initialise_database(db)
    service = CalendarService(db)
    yield service
    db.close()


def test_calendar_service_fixture_isolation(calendar_service, tmp_path):
    """Confirm the fixture uses an isolated temporary DB and not the app DB."""
    default_db = Database()
    assert calendar_service.database.database_path == tmp_path / "test_calendar.db"
    assert calendar_service.database.database_path != default_db.database_path
    assert calendar_service.database.database_path.exists()


def test_event_dialog_add_construction(qapp):
    """Verify EventDialog constructs cleanly without native crash for new events."""
    today = date.today()
    dialog = EventDialog(parent=None, selected_date=today)

    assert dialog.windowTitle() == "New Event"
    assert dialog.event_item is None
    assert dialog.title_input.text() == ""
    assert dialog.category_input.currentText() == "General"

    data = dialog.get_event_data()
    assert "start_datetime" in data
    assert "end_datetime" in data
    assert data["category"] == "General"


def test_event_dialog_edit_construction(qapp):
    """Verify EventDialog constructs cleanly without native crash for existing events."""
    sample_event = {
        "id": 1,
        "title": "Quarterly Review",
        "description": "Discuss roadmap and goals.",
        "start_datetime": "2026-11-04T10:00:00",
        "end_datetime": "2026-11-04T11:30:00",
        "category": "Work",
    }

    dialog = EventDialog(parent=None, event=sample_event)

    assert dialog.windowTitle() == "Edit Event"
    assert dialog.event_item == sample_event
    assert dialog.title_input.text() == "Quarterly Review"
    assert dialog.description_input.toPlainText() == "Discuss roadmap and goals."
    assert dialog.category_input.currentText() == "Work"

    data = dialog.get_event_data()
    assert data["title"] == "Quarterly Review"
    assert data["description"] == "Discuss roadmap and goals."
    assert data["start_datetime"] == "2026-11-04T10:00:00"
    assert data["end_datetime"] == "2026-11-04T11:30:00"
    assert data["category"] == "Work"


def test_event_dialog_parented_construction(qapp, calendar_service):
    """Verify EventDialog can be parented to CalendarPage without native crash."""
    page = CalendarPage(calendar_service)
    dialog = EventDialog(parent=page, selected_date=date.today())

    assert dialog.parent() is page
    assert dialog.event_item is None


def test_event_dialog_empty_title_validation(qapp, monkeypatch):
    """Verify that validate_and_accept rejects an empty title and warns the user."""
    dialog = EventDialog(parent=None, selected_date=date.today())
    dialog.title_input.setText("   ")

    warnings = []
    monkeypatch.setattr(
        MochiMessageDialog,
        "show_message",
        staticmethod(lambda parent, title, message: warnings.append((title, message))),
    )

    dialog.validate_and_accept()

    assert len(warnings) == 1
    assert warnings[0][0] == "Missing title"
    assert dialog.result() != QDialog.DialogCode.Accepted


def test_event_dialog_invalid_time_validation(qapp, monkeypatch):
    """Verify that validate_and_accept rejects end time <= start time."""
    dialog = EventDialog(parent=None, selected_date=date.today())
    dialog.title_input.setText("Valid Title")
    dialog.end_input.setDateTime(dialog.start_input.dateTime())

    warnings = []
    monkeypatch.setattr(
        MochiMessageDialog,
        "show_message",
        staticmethod(lambda parent, title, message: warnings.append((title, message))),
    )

    dialog.validate_and_accept()

    assert len(warnings) == 1
    assert warnings[0][0] == "Invalid time"
    assert dialog.result() != QDialog.DialogCode.Accepted


def test_event_dialog_valid_submission_accepts(qapp):
    """Verify that validate_and_accept accepts valid input."""
    dialog = EventDialog(parent=None, selected_date=date.today())
    dialog.title_input.setText("Valid Title")

    dialog.validate_and_accept()

    assert dialog.result() == QDialog.DialogCode.Accepted
