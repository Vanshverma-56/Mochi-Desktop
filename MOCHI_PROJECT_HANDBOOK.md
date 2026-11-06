# Mochi Project Handbook

**Technical source of truth — updated 4 November 2026**  
**Project:** Mochi Desktop · **Version:** 0.1.0 · **Platform target:** Windows

## 1\. Purpose and product boundaries

Mochi is a Windows desktop productivity application paired with a separate floating virtual-pet companion. The workspace is intended to provide a calm, polished home for everyday planning and reflection.

The pet/ordinary productivity experience is **not AI-powered**. A separately scoped, optional AI helper has been discussed as a future feature; it is not present in this source snapshot and must not be represented as implemented. Core app features must remain usable without an internet connection.

Product direction recorded in the project discussions:

* A customizable virtual pet, not restricted to a cat.
* A small independent companion window and a separate full workspace.
* An uncluttered, expressive-minimalist interface with warm neutrals, forest green, charcoal, navy, muted teal, dusty pink, brown and restrained gold.
* Planned workspace areas: Dashboard, Calendar, Tasks, Notes, Daily Logbook, Focus, Settings and Appearance.
* Future independent desktop widgets and appearance/customization options.
* Any future AI helper must be optional and clearly separated from the non-AI pet/productivity experience. Do not silently capture screens or send app data; user-selected context and explicit consent are required. Do not add paid API dependencies or paid fallbacks without explicit approval.

These are product requirements/directions, not proof that each feature exists in this code snapshot.

## 2\. Repository and snapshot provenance

* Repository: https://github.com/Vanshverma-56/Mochi-Desktop
* Branch reported by the developer: `main`
* Local Windows working directory reported by the developer: `C:\\\\\\\\\\\\\\\\Users\\\\\\\\\\\\\\\\VANSH\\\\\\\\\\\\\\\\Documents\\\\\\\\\\\\\\\\Projects\\\\\\\\\\\\\\\\Widget`
* Source delivered for this handoff: `Mochi\\\\\\\\\\\\\\\_Source\\\\\\\\\\\\\\\_For\\\\\\\\\\\\\\\_Handoff.zip`, generated with `git archive` from `HEAD`.
* The archive is a source snapshot, not a Git bundle. It does **not** contain `.git`, commit objects, branches, remotes or reflog. Use the GitHub repository for history.
* The working tree was reported clean immediately before archive creation.

Known pushed history, newest first (as reported by the developer):

|Commit|Subject|
|-|-|
| `e609e52` | Fix Calendar dialog Qt event collision (local, not yet pushed) |
|`6fde62d`|Integrate calendar and notes into workspace|
|`bd3e82f`|Redesign dashboard and add analog clock|
|`dde2f73`|Implement notes management interface|
|`ea9c293`|Implement calendar management interface|
|`cf8f1c7`|Add notes service tests|
|`6447cd7`|Add notes service|
|`f963fec`|Add calendar service tests|
|`bff9097`|Add calendar event service|
|`dd6341e`|Add animated collapsible sidebar navigation|
|`75e4380`|Initial commit: establish Mochi desktop application foundation|

The archive itself cannot independently verify this history because `.git` is excluded.

## 3\. Technology and setup

Declared project metadata (`pyproject.toml`):

* Python `>=3.11`
* PySide6 pinned to `6.12.0`
* Pillow
* psutil
* setuptools build backend
* pytest configured with `src` on `pythonpath` and `tests` as the test directory.

`requirements.txt` additionally lists pytest. Installation through the project metadata installs runtime dependencies; install pytest separately if needed.

### Windows PowerShell setup

```powershell
cd "$env:USERPROFILE\\\\\\\\\\\\\\\\Documents\\\\\\\\\\\\\\\\Projects\\\\\\\\\\\\\\\\Widget"
py -3.11 -m venv .venv
.\\\\\\\\\\\\\\\\.venv\\\\\\\\\\\\\\\\Scripts\\\\\\\\\\\\\\\\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest
```

If the project is freshly cloned:

```powershell
git clone https://github.com/Vanshverma-56/Mochi-Desktop.git
cd Mochi-Desktop
```

Run:

```powershell
python app.py
```

Test:

```powershell
python -m pytest -q
```

The source archive does not contain the virtual environment. Do not copy `.venv` between machines.

## 4\. Source layout in this snapshot

```text
.
├── app.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── src/
│   └── mochi/
│       ├── appearance/
│       ├── companion/
│       │   └── pet\\\\\\\\\\\\\\\_window.py
│       ├── core/
│       │   └── application.py
│       ├── database/
│       │   ├── connection.py
│       │   └── schema.py
│       ├── integrations/
│       │   └── windows/
│       ├── services/
│       │   ├── calendar\\\\\\\\\\\\\\\_service.py
│       │   ├── note\\\\\\\\\\\\\\\_service.py
│       │   └── task\\\\\\\\\\\\\\\_service.py
│       ├── widgets/
│       └── workspace/
│           ├── main\\\\\\\\\\\\\\\_window.py
│           └── pages/
│               ├── calendar\\\\\\\\\\\\\\\_page.py
│               ├── dashboard\\\\\\\\\\\\\\\_page.py
│               ├── focus\\\\\\\\\\\\\\\_page.py
│               ├── logbook\\\\\\\\\\\\\\\_page.py
│               ├── notes\\\\\\\\\\\\\\\_page.py
│               ├── section\\\\\\\\\\\\\\\_page.py
│               ├── settings\\\\\\\\\\\\\\\_page.py
│               └── tasks\\\\\\\\\\\\\\\_page.py
├── tests/
│   ├── test\\\\\\\\\\\\\\\_calendar\\\\\\\\\\\\\\\_dialog.py
│   ├── test\\\\\\\\\\\\\\\_calendar\\\\\\\\\\\\\\\_service.py
│   ├── test\\\\\\\\\\\\\\\_database.py
│   ├── test\\\\\\\\\\\\\\\_note\\\\\\\\\\\\\\\_service.py
│   └── test\\\\\\\\\\\\\\\_task\\\\\\\\\\\\\\\_service.py
├── test\\\\\\\\\\\\\\\_database.py
└── test\\\\\\\\\\\\\\\_task\\\\\\\\\\\\\\\_service.py
```

Some packages/directories are currently placeholders. Their presence does not mean the associated functionality is complete.

## 5\. Application startup and architecture

`app.py` imports `MochiApplication`, constructs it and exits with `application.run()`.

`src/mochi/core/application.py`:

1. Reuses an existing `QApplication` or creates one.
2. Sets application and organization names to `Mochi`.
3. Creates `Database` and calls `initialise\\\\\\\\\\\\\\\_database`.
4. Creates shared `TaskService`, `CalendarService` and `NoteService`.
5. Creates `MainWindow` with those services and creates `PetWindow`.
6. Connects application shutdown to `database.close`.
7. Shows workspace and companion, then enters the Qt event loop.

`MainWindow` builds a stacked workspace with sidebar navigation for Dashboard, Calendar, Tasks, Notes, Logbook, Focus and Settings. It includes a collapsible/animated sidebar. Dashboard, Calendar, Tasks and Notes receive their corresponding services. Logbook, Focus and Settings pages are instantiated without services in this snapshot.

The service layer performs SQLite persistence. UI pages call the relevant service; keep business validation and persistence out of presentation code when extending the application.

## 6\. Database

`Database` uses `QStandardPaths.StandardLocation.AppLocalDataLocation`, creates that directory, and stores the database as `mochi.db` within it. The exact resolved Windows path depends on Qt's application/organization path resolution on the machine. The SQLite connection is lazily created, uses `sqlite3.Row`, and enables foreign keys. It is shared by the services and closed on application shutdown.

`initialise\\\\\\\\\\\\\\\_database` creates these tables if absent:

* `tasks`: title, description, priority, category, due date, completion flag, created/updated timestamps.
* `calendar\\\\\\\\\\\\\\\_events`: title, description, start/end datetimes, category, created timestamp.
* `notes`: title, content, category, created/updated timestamps.
* `logbook\\\\\\\\\\\\\\\_entries`: entry date, title, content, created/updated timestamps.
* `focus\\\\\\\\\\\\\\\_sessions`: start/end, duration minutes, session type, completed flag.
* `preferences`: key/value.

The schema is an initial schema creation script; no migration framework is present in this snapshot. Make schema changes backward-compatible or introduce explicit migrations. Do not delete the user's existing `mochi.db` as a debugging shortcut.

## 7\. Implemented functionality — source inspection

### Companion

`src/mochi/companion/pet\\\\\\\\\\\\\\\_window.py` provides a separate companion window. The source snapshot establishes its presence; full customization, pet selection and a complete interaction/animation system are not verified here.

### Tasks

`TaskService` supports create, retrieve, list, update, delete and completion state. It validates non-empty titles and priorities in `Low`, `Medium`, `High`. The Tasks page is present and the README describes search, filtering, due-date grouping and completion undo. GUI behavior should still be manually checked after changes.

### Calendar

`CalendarService` supports create, retrieve, list, range query, update and delete. It validates a non-empty title, ISO-formatted start/end values and end-after-start when an end value is supplied.

`CalendarPage` includes month/date navigation, event listing, date highlighting, add/edit/delete flows, custom Mochi dialogs, category selection and restrictions on adding/editing events on past dates. The `EventDialog` uses `QDateTimeEdit` controls with calendar popups.

**Resolved blocking defect — Calendar dialog native Windows access violation:**
Previously, launching the GUI and entering the Calendar add-event flow caused a native Windows access violation:

```text
Windows fatal exception: access violation

Current thread 0x0000a3cc (most recent call first):
  File "src/mochi/workspace/pages/calendar\\\\\\\\\\\\\\\_page.py", line 187 in \\\\\\\\\\\\\\\_\\\\\\\\\\\\\\\_init\\\\\\\\\\\\\\\_\\\\\\\\\\\\\\\_
  File "src/mochi/workspace/pages/calendar\\\\\\\\\\\\\\\_page.py", line 887 in add\\\\\\\\\\\\\\\_event
```

**Investigation and Root Cause:**

* The crash was reproduced and isolated under Python `faulthandler` during `EventDialog` construction.
* Controlled experiments established that the crash was caused by assigning `self.event = event` in `EventDialog.\\\\\\\\\\\\\\\_\\\\\\\\\\\\\\\_init\\\\\\\\\\\\\\\_\\\\\\\\\\\\\\\_`.
* `QObject` defines an `event()` method used throughout Qt's event handling. Assigning `self.event = event` shadowed that method name on the dialog instance, causing a collision with the Qt/PySide6 event-handling interface when `self.setWindowTitle(...)` was invoked.
* Because the collision occurred in the native Qt / PySide6 interface layer rather than ordinary Python code, Windows raised a fatal native access violation (`0xC0000005`) instead of an ordinary Python exception.
* Renaming the instance attribute to `self.event\\\\\\\\\\\\\\\_item` eliminated the collision, allowing the dialog to construct and initialize cleanly without crashing.

**Resolution:**

* Renamed `self.event` to `self.event\\\\\\\\\\\\\\\_item` inside `EventDialog.\\\\\\\\\\\\\\\_\\\\\\\\\\\\\\\_init\\\\\\\\\\\\\\\_\\\\\\\\\\\\\\\_` to prevent collision with `QObject.event()`.
* Updated `EventDialog` construction in both `CalendarPage.add\\\\\\\\\\\\\\\_event` and `edit\\\\\\\\\\\\\\\_selected\\\\\\\\\\\\\\\_event` to use `parent=self` instead of `parent=None`, establishing consistent modal parenting and proper window hierarchy matching other Mochi pages.
* The fix was strictly confined to `src/mochi/workspace/pages/calendar\\\\\\\\\\\\\\\_page.py` and verified through new dedicated regression tests in `tests/test\\\\\\\\\\\\\\\_calendar\\\\\\\\\\\\\\\_dialog.py`.

### Notes

`NoteService` supports create, retrieve, list, search, update and delete. Service search checks title, content and category. `NotesPage` and its editor dialog are present; the developer previously reported that the Notes page worked well in manual use. The current source should still be manually rechecked. Compare UI search behavior with service behavior: do not accidentally narrow or change search semantics.

### Dashboard

`DashboardPage` includes a redesigned dashboard, metrics/progress areas, today's tasks/upcoming deadlines and Calendar/Notes shortcuts. It includes a custom `AnalogClock` drawn with `QPainter`, with a one-second update mechanism and digital toggle. Dashboard display and clock toggling were verified using automated Qt test harnesses; interactive mouse-driven testing has not been performed.

### Logbook, Focus, Settings

Page modules exist and are wired into navigation, but the current `MainWindow` constructs them without persistence/service dependencies. Do not describe full logbook entry management, focus-session tracking or settings persistence as complete until code and manual tests demonstrate it.

## 8\. Automated test status

The automated test suite was executed in the Windows environment (`Python 3.11.9`, `PySide6 6.12.0`, `pytest 9.2.0`).

### Latest Reported Test Results

* **Full test suite (`pytest tests/`)**: **31 passed** (latest reported: 31 passed in 1.34s).
* **Original test files (`tests/test\\\\\\\\\\\\\\\_calendar\\\\\\\\\\\\\\\_service.py`, `tests/test\\\\\\\\\\\\\\\_database.py`, `tests/test\\\\\\\\\\\\\\\_note\\\\\\\\\\\\\\\_service.py`, `tests/test\\\\\\\\\\\\\\\_task\\\\\\\\\\\\\\\_service.py`)**: **24 passed** (latest reported: 24 passed in 0.53s).
* **Zero existing tests modified or removed**: all original service and database assertions remain completely untouched.

These figures represent the results of the latest reported test run in this Windows environment, not an invariant guarantee that every environment or machine will yield identical execution timing.

### Dedicated Calendar Dialog Regression Suite

The test file `tests/test\\\\\\\\\\\\\\\_calendar\\\\\\\\\\\\\\\_dialog.py` was introduced to prevent regressions in Calendar dialog instantiation and event validation:

* **New Event dialog construction**: verifies clean construction with `parent=None` and `selected\\\\\\\\\\\\\\\_date`.
* **Edit Event dialog construction**: verifies clean construction with `parent=None` and pre-populated event dictionaries.
* **Parented construction**: verifies dialog construction when parented to a `CalendarPage` widget (`parent=self`).
* **Temporary database path fixture verification**: The `calendar\\\\\\\\\\\\\\\_service` test fixture explicitly overrides `database.database\\\\\\\\\\\\\\\_path` with pytest's `tmp\\\\\\\\\\\\\\\_path / "test\\\\\\\\\\\\\\\_calendar.db"` before database initialization or connection. A dedicated test (`test\\\\\\\\\\\\\\\_calendar\\\\\\\\\\\\\\\_service\\\\\\\\\\\\\\\_fixture\\\\\\\\\\\\\\\_isolation`) specifically verifies that this fixture configures `database\\\\\\\\\\\\\\\_path` to the temporary path rather than the default `mochi.db` path; this test verifies that fixture's path configuration without asserting broader guarantees across all possible database operations.
* **Empty-title validation**: verifies that submitting an event with whitespace/empty title halts acceptance and raises a user warning.
* **Invalid time-range validation**: verifies that submitting an event where `end\\\\\\\\\\\\\\\_datetime <= start\\\\\\\\\\\\\\\_datetime` halts acceptance and raises a user warning.
* **Successful submission**: verifies that valid title and times trigger `self.accept()` and return expected event data.

The project root also contains `test\\\\\\\\\\\\\\\_database.py` and `test\\\\\\\\\\\\\\\_task\\\\\\\\\\\\\\\_service.py`; these are standalone manual inspection scripts from initial development that run against the active database rather than pytest fixtures.

### GUI Verification Levels and Limitations

Automated Qt/PySide6 programmatic test harnesses in the local Windows environment reportedly verified the application lifecycle (`MochiApplication`), Calendar operations (month navigation, date selection, past-date restrictions, event add/edit/delete flows), Dashboard components (analog clock, digital toggle, date display), Tasks and Notes lifecycles, and companion window initialization.
**Verification limitation:** Most reported GUI checks were conducted through automated Qt event loops and Python test scripts. The developer subsequently launched the original Windows application and manually confirmed that the Calendar Add Event flow works after the fix. This manual confirmation does not establish that every Calendar workflow or other GUI feature has been manually tested.

## 9\. Current status matrix

|Area|Source status|Verification status|
|-|-|-|
|Python/PySide6 app startup|Implemented|Verified via automated harness (app launches without native crash; workspace and companion display)|
|SQLite database/schema|Implemented|Verified via automated harness (automated tests passing; isolated temporary DB used in fixture tests)|
|Floating companion window|Implemented foundation|Foundation verified present and independently displayed via automated harness|
|Tasks service/UI|Implemented|Automated tests passing; GUI task lifecycle verified via automated harness|
| Calendar service/UI | Implemented | Service and dialog tests passing; GUI operations verified through automated harness; Add Event flow additionally confirmed manually by the developer |
|Notes service/UI|Implemented|Service tests passing; note creation/refresh verified via automated harness|
|Dashboard/analog clock|Implemented|Verified via automated harness (analog/digital clock toggle, date rendering, shortcuts verified)|
|Logbook|Page placeholder/foundation|Not verified as functional|
|Focus|Page placeholder/foundation|Not verified as functional|
|Settings/appearance|Page placeholder/foundation|Not verified as functional|
|Independent widgets|Directories/future scope|Not implemented/verified|
|AI helper|Future product discussion only|Not implemented|

## 10\. Engineering rules for future work

* Preserve working functionality and the current visual direction.
* Make the smallest evidence-based change that solves the task; avoid broad refactors.
* Inspect the actual source and runtime versions before diagnosing platform-specific behavior.
* Keep UI, services and database responsibilities separated.
* Use parameterized SQL.
* Validate user input in services as well as in the UI where appropriate.
* Do not silently discard, reset or migrate user data.
* Do not claim an operation succeeded until persistence succeeds.
* Add/update tests for service and database changes.
* Manually verify Qt GUI interactions on Windows; pytest alone is insufficient.
* Update this handbook and `MOCHI\\\\\\\\\\\\\\\_PROJECT\\\\\\\\\\\\\\\_GUIDE\\\\\\\\\\\\\\\_AND\\\\\\\\\\\\\\\_HANDOFF.md` together whenever architecture, setup, requirements, status or known defects change.
* Keep the README and CHANGELOG aligned with actual implementation.
* Do not commit or push new changes unless the developer explicitly authorizes it.

## 11\. Immediate technical priority

The blocking Calendar native Windows access violation has been diagnosed and resolved. The full automated test suite passes (31 tests). Automated regression checks cover Dashboard, Tasks, Notes, Calendar, and the companion window. The developer also manually confirmed that the Calendar Add Event flow works in the original Windows application.

