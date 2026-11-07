import pytest

from mochi.database.connection import Database
from mochi.database.schema import initialise_database
from mochi.services.focus_service import FocusService


@pytest.fixture
def focus_service(tmp_path):
    database = Database()
    database.database_path = tmp_path / "test_focus.db"

    initialise_database(database)

    service = FocusService(database)

    yield service

    database.close()


def test_start_focus_session(focus_service):
    session = focus_service.start_session()

    assert session["id"] is not None
    assert session["duration_minutes"] == 25
    assert session["session_type"] == "Focus"
    assert session["ended_at"] is None
    assert session["completed"] == 0


def test_start_custom_session(focus_service):
    session = focus_service.start_session(
        duration_minutes=5,
        session_type="Short Break",
    )

    assert session["duration_minutes"] == 5
    assert session["session_type"] == "Short Break"


def test_reject_invalid_duration(focus_service):
    with pytest.raises(ValueError):
        focus_service.start_session(duration_minutes=0)

    with pytest.raises(ValueError):
        focus_service.start_session(duration_minutes=1441)


def test_reject_invalid_session_type(focus_service):
    with pytest.raises(ValueError):
        focus_service.start_session(session_type="Invalid")


def test_only_one_active_session_allowed(focus_service):
    focus_service.start_session()

    with pytest.raises(ValueError):
        focus_service.start_session()


def test_get_active_session(focus_service):
    session = focus_service.start_session()

    active = focus_service.get_active_session()

    assert active["id"] == session["id"]


def test_complete_session(focus_service):
    session = focus_service.start_session()

    completed = focus_service.complete_session(session["id"])

    assert completed["completed"] == 1
    assert completed["ended_at"] is not None
    assert focus_service.get_active_session() is None


def test_interrupt_session(focus_service):
    session = focus_service.start_session()

    interrupted = focus_service.interrupt_session(
        session["id"]
    )

    assert interrupted["completed"] == 0
    assert interrupted["ended_at"] is not None
    assert focus_service.get_active_session() is None


def test_cannot_complete_session_twice(focus_service):
    session = focus_service.start_session()

    focus_service.complete_session(session["id"])

    result = focus_service.complete_session(session["id"])

    assert result is None


def test_daily_summary_counts_completed_focus_only(
    focus_service,
):
    focus = focus_service.start_session(
        duration_minutes=25,
        session_type="Focus",
    )
    focus_service.complete_session(focus["id"])

    short_break = focus_service.start_session(
        duration_minutes=5,
        session_type="Short Break",
    )
    focus_service.complete_session(short_break["id"])

    interrupted = focus_service.start_session(
        duration_minutes=25,
        session_type="Focus",
    )
    focus_service.interrupt_session(interrupted["id"])

    summary = focus_service.get_daily_summary()

    assert summary["completed_sessions"] == 1
    assert summary["focused_minutes"] == 25


def test_get_sessions(focus_service):
    first = focus_service.start_session()
    focus_service.complete_session(first["id"])

    second = focus_service.start_session(
        duration_minutes=5,
        session_type="Short Break",
    )

    sessions = focus_service.get_sessions()

    assert len(sessions) == 2
    assert {session["id"] for session in sessions} == {
        first["id"],
        second["id"],
    }


def test_get_sessions_rejects_invalid_limit(focus_service):
    with pytest.raises(ValueError):
        focus_service.get_sessions(limit=0)

def test_recover_active_session(focus_service):
    session = focus_service.start_session()

    recovered = focus_service.interrupt_active_session()

    assert recovered is True

    interrupted = focus_service.get_session(session["id"])

    assert interrupted["ended_at"] is not None
    assert interrupted["completed"] == 0
    assert focus_service.get_active_session() is None


def test_recovery_when_no_active_session(focus_service):
    recovered = focus_service.interrupt_active_session()

    assert recovered is False