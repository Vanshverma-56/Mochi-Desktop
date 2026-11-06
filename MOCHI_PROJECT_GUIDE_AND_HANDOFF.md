# Mochi — Project Guide & AI Developer Handoff
**Updated:** 3 November 2026 · **Version:** 0.1.0

## What Mochi is

Mochi is a Windows desktop productivity workspace accompanied by a separate floating virtual pet. It is designed to feel like a polished, calm desktop companion rather than a generic task tracker.

The pet and ordinary productivity functions are non-AI. An optional, separate AI helper is a future idea only; it is not implemented in this snapshot. Core features must not depend on AI or internet access.

**Repository:** https://github.com/Vanshverma-56/Mochi-Desktop  
**Branch:** `main` (reported)  
**Developer's local path:** `C:\Users\VANSH\Documents\Projects\Widget`

## Current state at handoff

The project has a functioning Python/PySide6 application structure, SQLite storage, service layers for Tasks/Calendar/Notes, workspace navigation, a floating companion window, a redesigned Dashboard with an analog clock, and stabilized Calendar and Notes interfaces.

The automated test suite has **31 passed** (`python -m pytest tests/` — latest reported: 31 passed in 1.34s). All 24 original service and database tests pass without modification (`24 passed in 0.53s`), supplemented by 7 dedicated dialog and validation tests in `tests/test_calendar_dialog.py`.

**Resolved issue:** the Calendar dialog crash on Windows has been investigated, diagnosed, and resolved.

## Completed First Task: Calendar Crash Diagnosis, Resolution, and Verification

### 1. Investigation and Verified Findings
- **Observed Failure:** The application encountered a native Windows access violation when constructing the Calendar `EventDialog` during Add Event or Edit Event actions:
  ```text
  Windows fatal exception: access violation
  File "src/mochi/workspace/pages/calendar_page.py", line 187 in __init__
  ```
- **Root Cause Isolation:** Using controlled experiments with Python `faulthandler`, the failure was isolated to the line `self.event = event` inside `EventDialog.__init__`.
- **Root Cause & Collision with Qt:** `QObject` defines an `event()` method used throughout Qt's event handling. Controlled experiments established that assigning `self.event = event` in `EventDialog.__init__` shadowed this method on the dialog instance, causing a collision with the Qt/PySide6 event-handling interface during widget initialization when `self.setWindowTitle(...)` was invoked. Because the collision occurred in the native Qt / PySide6 interface layer rather than ordinary Python application code, Windows raised a fatal native access violation (`0xC0000005`) instead of an ordinary Python exception.
- **The Fix:**
  - Renamed the attribute to `self.event_item = event` inside `EventDialog.__init__` in `src/mochi/workspace/pages/calendar_page.py`, completely eliminating the shadowing of `QObject.event()`.
  - Updated `EventDialog` construction in both `CalendarPage.add_event` and `edit_selected_event` to use `parent=self` instead of `parent=None`, establishing proper modal parenting and window hierarchy consistent with other Mochi dialogs.
  - The fix was strictly confined to `src/mochi/workspace/pages/calendar_page.py`.

### 2. Dedicated Regression Tests
Introduced `tests/test_calendar_dialog.py` without modifying any existing test files:
- **New Event dialog construction:** clean construction with `parent=None` and `selected_date`.
- **Edit Event dialog construction:** clean construction with `parent=None` and pre-populated event dictionaries.
- **Parented construction:** clean construction when parented to a `CalendarPage` widget (`parent=self`).
- **Temporary SQLite database fixture verification:** The `calendar_service` test fixture explicitly overrides `database.database_path` with pytest's `tmp_path / "test_calendar.db"` prior to database initialization or connection. A dedicated test (`test_calendar_service_fixture_isolation`) verifies that this fixture sets `database_path` to the temporary path rather than the default `mochi.db` path; this test specifically verifies that fixture's path configuration without asserting broader guarantees across all possible database operations.
- **Empty-title validation:** verifies that submitting with an empty/whitespace title is rejected and triggers a user warning.
- **Invalid time-range validation:** verifies that submitting with `end_datetime <= start_datetime` is rejected and triggers a user warning.
- **Successful submission:** verifies that valid title and times trigger `self.accept()` and return expected event data.

### 3. Verification Results
- **Full Test Suite:** `pytest tests/` — **31 passed** (latest reported: 31 passed in 1.34s).
- **Original Test Files:** **24 passed** (latest reported: 24 passed in 0.53s).
- **Zero Modifications to Existing Tests:** all 24 original tests remain completely untouched.
- *Note:* These figures represent the results of the latest reported test run in this Windows environment, not an invariant guarantee for every future environment.
**Reported Verification:**
  - Automated Qt/PySide6 test harnesses in the local Windows environment reportedly verified the application lifecycle (`MochiApplication`), Calendar operations (month navigation, date selection, past-date restrictions, event add/edit/delete flows), Dashboard components (analog clock, digital 24h toggle, date string), Tasks and Notes lifecycles, and companion window initialization.
*Verification limitation:* Most reported GUI checks were conducted through automated Qt event loops and Python test scripts. The developer subsequently launched the original Windows application and manually confirmed that the Calendar Add Event flow works after the fix. This manual confirmation does not establish that every Calendar workflow or other GUI feature has been manually tested.

### 4. Summary of Changes and File Scope
- **Calendar Defect Fix:**
  - Modified: `src/mochi/workspace/pages/calendar_page.py` (renamed `self.event` to `self.event_item`; passed `parent=self` to dialogs).
  - Added: `tests/test_calendar_dialog.py` (dedicated regression suite covering construction, validation, and fixture isolation).
- **Documentation Update Task:**
  - Modified four documentation files only: `MOCHI_PROJECT_HANDBOOK.md`, `MOCHI_PROJECT_GUIDE_AND_HANDOFF.md`, `README.md`, and `CHANGELOG.md`.
  - No source code, tests, configuration, or database files were altered during documentation updates.

## Next Task for Developers / AI: Daily Logbook

With the Calendar page stabilized and regression checks passing, the next planned workspace feature is **Daily Logbook**.

Guidelines for implementing Daily Logbook:
- Keep UI, service, and database layers strictly separated.
- Introduce `LogbookService` using parameterized SQL against the existing `logbook_entries` table in `schema.py`.
- Connect `LogbookPage` to `LogbookService` through `MainWindow`.
- Maintain Mochi's visual styling (warm neutrals, cards, Segoe UI typography).
- Add automated unit tests with temporary SQLite database isolation.
- Run regression tests to verify that Dashboard, Calendar, Tasks, Notes, and the companion continue functioning.

## Setup and commands

Requires Python 3.11+ and Windows. PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest
python app.py
```

Tests:

```powershell
python -m pytest -q
```

For native crash diagnostics (if needed for future debugging):

```powershell
python -X faulthandler app.py
```

Dependencies declared in `pyproject.toml`: `PySide6==6.12.0`, Pillow, psutil. pytest is in `requirements.txt` and configured in `pyproject.toml`.

## Architecture map

- `app.py` — entry point.
- `src/mochi/core/application.py` — QApplication, database, shared services, workspace and companion lifecycle.
- `src/mochi/database/connection.py` — SQLite connection and Qt app-local data location.
- `src/mochi/database/schema.py` — initial table creation.
- `src/mochi/services/task_service.py` — task persistence and validation.
- `src/mochi/services/calendar_service.py` — event CRUD, validation and range queries.
- `src/mochi/services/note_service.py` — note CRUD and search.
- `src/mochi/workspace/main_window.py` — stacked pages and collapsible sidebar.
- `src/mochi/workspace/pages/dashboard_page.py` — dashboard and analog clock.
- `src/mochi/workspace/pages/calendar_page.py` — calendar UI and event dialogs; stabilized after resolving QObject method shadowing.
- `src/mochi/workspace/pages/notes_page.py` — notes UI.
- `src/mochi/workspace/pages/tasks_page.py` — tasks UI.
- `src/mochi/companion/pet_window.py` — floating companion.
- `src/mochi/workspace/pages/logbook_page.py`, `focus_page.py`, `settings_page.py` — page modules present, but full functionality is not established.

SQLite database filename: `mochi.db`, under Qt `AppLocalDataLocation`. Existing user data must be preserved.

## Implemented vs planned

Implemented in source:
- Application startup and shared SQLite database.
- Task, calendar-event and note services.
- Workspace navigation and animated collapsible sidebar.
- Dashboard with analog clock and task-related overview.
- Calendar interface and stabilized event dialogs (reported verified via automated test harness).
- Notes interface.
- Floating companion window foundation.

Not verified as complete:
- Full pet customization and complete animation/interaction system.
- Full Logbook persistence/workflows.
- Focus timer and session tracking.
- Settings and appearance persistence.
- Independent desktop widgets.
- Optional AI helper.

The schema already includes tables for logbook entries, focus sessions and preferences; table existence alone does not mean those features are implemented.

## Data and implementation cautions

- Do not delete `mochi.db`, reset the app's data directory, or run destructive SQL.
- The schema currently uses `CREATE TABLE IF NOT EXISTS`; no migration system is visible. Plan migrations before changing existing tables.
- Keep SQL parameterized.
- Keep service validation and UI presentation separate.
- The Notes service searches title, content and category. Preserve this intended behavior when aligning UI search.
- The source archive is generated from committed `HEAD`; it excludes `.git` and therefore does not carry branch history.
- Root-level `test_database.py` and `test_task_service.py` coexist with `tests/` equivalents. Inspect before deduplicating or deleting.

## Git history supplied by developer

Latest pushed commits (newest first):
```text
6fde62d Integrate calendar and notes into workspace
bd3e82f Redesign dashboard and add analog clock
dde2f73 Implement notes management interface
ea9c293 Implement calendar management interface
cf8f1c7 Add notes service tests
6447cd7 Add notes service
f963fec Add calendar service tests
bff9097 Add calendar event service
dd6341e Add animated collapsible sidebar navigation
75e4380 Initial commit: establish Mochi desktop application foundation
```

These hashes/subjects were supplied by the developer; verify with GitHub or a clone if needed.

## Work protocol

- Do not make unrelated redesigns when stabilizing or extending features.
- Do not overwrite working modules or rewrite architecture wholesale.
- Before editing, inspect current files and establish a reproducible baseline.
- Make focused changes, add regression tests where meaningful, run the full suite and perform GUI verification.
- Report: root cause, exact files changed, why the fix works, test output, manual test results, remaining risks.
- Do not commit or push unless the developer explicitly authorizes it.
- Calendar stabilization and automated regression checks have been reported completed. The next planned feature is Daily Logbook.
- Update this handoff and the technical handbook together whenever project facts or status change.

## Full technical reference

See `MOCHI_PROJECT_HANDBOOK.md` for the detailed architecture, schema, source tree, current status and engineering rules.
