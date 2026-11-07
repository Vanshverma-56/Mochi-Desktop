from datetime import date, datetime, time, timedelta

import pytest
from PySide6.QtWidgets import QApplication

from mochi.database.connection import Database
from mochi.database.schema import initialise_database
from mochi.services.calendar_service import CalendarService
from mochi.widgets.calendar_widget import CalendarWidget
from mochi.widgets.desktop_widgets import DesktopWidgetsWindow
from mochi.workspace.pages.calendar_page import MochiMessageDialog
from mochi.services.music_service import MusicService
from mochi.services.music_player import MusicPlaybackController


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def calendar_service(tmp_path):
    db = Database()
    db.database_path = tmp_path / "test_calendar_widget.db"
    initialise_database(db)

    service = CalendarService(db)
    yield service
    db.close()

@pytest.fixture
def music_dependencies(tmp_path):
    db = Database()
    db.database_path = tmp_path / "test_music_widget.db"
    initialise_database(db)

    music_service = MusicService(db)
    music_player = MusicPlaybackController()

    yield music_service, music_player

    music_player.stop()
    db.close()


def test_calendar_widget_constructs(qapp, calendar_service):
    widget = CalendarWidget(calendar_service)

    assert widget.calendar_service is calendar_service
    assert widget.windowTitle() == "Widget - Calendar"
    assert widget.calendar is not None
    assert widget.event_list is not None

    widget.close()


def test_calendar_widget_loads_events_for_selected_date(
    qapp,
    calendar_service,
):
    selected_date = date.today()

    calendar_service.create_event(
        title="Widget Test Event",
        start_datetime=datetime.combine(
            selected_date,
            time(10, 0),
        ).isoformat(),
        end_datetime=datetime.combine(
            selected_date,
            time(11, 0),
        ).isoformat(),
        category="Study",
    )

    widget = CalendarWidget(calendar_service)
    widget.selected_date = selected_date
    widget.refresh_event_list()

    assert widget.event_list.count() == 1
    assert "Widget Test Event" in widget.event_list.item(0).text()
    assert widget.event_count.text() == "1 event"

    widget.close()


def test_calendar_widget_shows_empty_date(
    qapp,
    calendar_service,
):
    widget = CalendarWidget(calendar_service)
    widget.selected_date = date.today() + timedelta(days=5)
    widget.refresh_event_list()

    assert widget.event_list.count() == 0
    assert widget.empty_label.isVisible() is False or (
        widget.empty_label.isHidden()
    )
    assert widget.event_count.text() == "0 events"

    widget.close()


def test_calendar_widget_disables_add_and_edit_for_past_dates(
    qapp,
    calendar_service,
):
    widget = CalendarWidget(calendar_service)
    widget.selected_date = date.today() - timedelta(days=1)
    widget.refresh_event_list()

    assert not widget.add_button.isEnabled()
    assert not widget.edit_button.isEnabled()

    widget.close()


def test_calendar_widget_delete_emits_change_signal(
    qapp,
    calendar_service,
    monkeypatch,
):
    selected_date = date.today()

    event = calendar_service.create_event(
        title="Event to Delete",
        start_datetime=datetime.combine(
            selected_date,
            time(10, 0),
        ).isoformat(),
        end_datetime=datetime.combine(
            selected_date,
            time(11, 0),
        ).isoformat(),
    )

    widget = CalendarWidget(calendar_service)
    widget.selected_date = selected_date
    widget.refresh_event_list()
    widget.event_list.setCurrentRow(0)

    confirmations = []
    monkeypatch.setattr(
        MochiMessageDialog,
        "ask_confirmation",
        staticmethod(
            lambda parent, title, message: confirmations.append(
                (title, message)
            ) or True
        ),
    )

    changes = []
    widget.events_changed.connect(lambda: changes.append(True))

    widget.delete_selected_event()

    assert calendar_service.get_event(event["id"]) is None
    assert len(confirmations) == 1
    assert changes == [True]
    assert widget.event_list.count() == 0

    widget.close()


def test_desktop_widgets_hub_uses_shared_calendar_service(
    qapp,
    calendar_service,
    music_dependencies,
):
    music_service, music_player = music_dependencies

    hub = DesktopWidgetsWindow(
        calendar_service,
        music_service,
        music_player,
    )

    assert hub.calendar_widget.calendar_service is calendar_service

    assert hub.music_service is music_service
    assert hub.music_player is music_player
    assert hub.music_mini_player.playback_controller is music_player

    assert hasattr(hub, "calendar_button")
    assert hasattr(hub, "calendar_status")

    assert hasattr(hub, "music_button")
    assert hasattr(hub, "music_status")

    hub.shutdown()
