# Widget — Technical Project Handbook

**Document type:** Technical source of truth
**Application:** Widget
**Virtual companion:** Mochi
**GitHub repository:** `Vanshverma-56/Mochi-Desktop`
**Platform:** Windows
**Language:** Python 3.11+
**Interface framework:** PySide6
**Storage:** SQLite
**Development status:** Active development

---

# 1. Project Overview

Widget is a Windows desktop productivity application with three independently managed components:

1. **Dashboard** — the main productivity workspace.
2. **Desktop Widgets** — independent floating desktop tools.
3. **Mochi Companion** — a separate floating virtual pet.

The application is designed to be modular, locally functional, and customisable.

The core application does not require AI services. Mochi is explicitly a non-AI virtual pet.

The project prioritises functional implementation before comprehensive visual redesign and polish.

## 1.1 Core design principles

- Offline-first functionality.
- Local data storage.
- Modular application architecture.
- Separation of UI and business logic.
- Independent management of desktop components.
- Custom application dialogs and controls.
- No mandatory paid APIs, subscriptions, or hidden ongoing costs.
- Mochi remains non-AI.
- Preserve working functionality when implementing new features.

## 1.2 Current development philosophy

The current interface is a working prototype, not the final design.

The intended development order is:

1. Complete the planned functional foundations.
2. Verify integration and application lifecycle.
3. Improve visual consistency and usability.
4. Refine appearance, interactions, and customisation.
5. Consider packaging and distribution.

Avoid treating prototype UI decisions as permanent design requirements.

---

# 2. Application Architecture

## 2.1 High-level structure

Widget is organised into three main application components.

### Dashboard

The main productivity workspace contains:

- Dashboard
- Calendar
- Tasks
- Notes
- Daily Logbook
- Focus
- Settings / Appearance

The workspace uses a main window with navigation between pages.

### Desktop Widgets

A separate floating widget environment currently contains:

- Digital Clock
- System Monitor
- Calendar Widget
- Music Mini-player

These widgets are separate windows managed through the Desktop Widgets interface.

The intended behaviour is that widgets can remain independently visible even when the widget-management window is hidden.

### Mochi Companion

Mochi is a separate floating pet window.

It should remain independent from the productivity workspace and should not become an AI assistant.

## 2.2 Application launcher

**Source:** `src/mochi/core/launcher.py`

The launcher provides the initial application control interface.

It provides access to:

- Launch Dashboard
- Launch Desktop Widgets
- Launch Mochi Companion
- Launch All
- Exit Widget

The launcher communicates with the application controller and reflects component status.

The current launcher is functional but remains a prototype. Its visual design and some interactions can be improved later.

## 2.3 Application lifecycle

**Source:** `src/mochi/core/application.py`

`MochiApplication` coordinates application startup, services, windows, and shutdown.

Its responsibilities include:

- Initialising the Qt application.
- Creating the SQLite database.
- Initialising database tables.
- Instantiating application services.
- Creating the music playback controller.
- Creating the main workspace.
- Creating the Mochi companion.
- Creating the Focus timer controller and floating overlay.
- Creating the Desktop Widgets window.
- Creating the application launcher.
- Coordinating shutdown.

The application controller is the central integration point. New independent components should be connected here rather than creating unrelated application entry points.

### Lifecycle considerations

- Hiding a component is not necessarily equivalent to shutting it down.
- The launcher should remain available while the application is running.
- Closing a workspace window should not accidentally terminate unrelated floating components.
- The explicit Exit Widget action should shut down the complete application.
- Active timers and audio playback should be stopped or cleaned up appropriately during full shutdown.
- Database connections must be closed cleanly.

The application currently does not require automatic Windows startup.

---

# 3. Source Code Structure

The current source layout is:

```text
Widget/
│
├── app.py
│
├── assets/
│   └── sounds/
│       ├── default.wav
│       ├── chime.wav
│       ├── alert.wav
│       └── gentle.wav
│
├── src/
│   └── mochi/
│       │
│       ├── appearance/
│       │
│       ├── companion/
│       │   └── pomodoro.py
│       │
│       ├── core/
│       │   ├── application.py
│       │   └── launcher.py
│       │
│       ├── database/
│       │   ├── connection.py
│       │   └── schema.py
│       │
│       ├── integrations/
│       │   └── windows/
│       │
│       ├── services/
│       │   ├── calendar_service.py
│       │   ├── focus_service.py
│       │   ├── logbook_service.py
│       │   ├── music_player.py
│       │   ├── music_service.py
│       │   ├── note_service.py
│       │   └── task_service.py
│       │
│       ├── widgets/
│       │   ├── calendar_widget.py
│       │   ├── clock_widget.py
│       │   ├── desktop_widgets.py
│       │   ├── music_mini_player.py
│       │   └── system_monitor.py
│       │
│       └── workspace/
│           ├── main_window.py
│           └── pages/
│               ├── calendar_page.py
│               ├── dashboard_page.py
│               ├── focus_page.py
│               ├── logbook_page.py
│               ├── notes_page.py
│               ├── section_page.py
│               ├── settings_page.py
│               └── tasks_page.py
│
├── tests/
│
├── README.md
├── CHANGELOG.md
├── MOCHI_PROJECT_HANDBOOK.md
├── MOCHI_PROJECT_GUIDE_AND_HANDOFF.md
├── pyproject.toml
└── requirements.txt
```

This is the current conceptual layout. Check the actual repository before relying on the tree for newly added modules.

## 3.1 Module responsibilities

| Module | Responsibility |
|---|---|
| `core/` | Application startup, lifecycle, and launcher |
| `database/` | SQLite connection and schema |
| `services/` | Business logic and data operations |
| `workspace/` | Main productivity window |
| `workspace/pages/` | Individual productivity pages |
| `widgets/` | Independent floating desktop widgets |
| `companion/` | Mochi companion-related functionality and floating timer |
| `appearance/` | Appearance-related functionality |
| `integrations/` | Platform-specific integrations |
| `assets/` | Local sound and other application assets |
| `tests/` | Automated tests |

---

# 4. Database Architecture

## 4.1 Database implementation

**Files:**
- `src/mochi/database/connection.py`
- `src/mochi/database/schema.py`

Widget uses SQLite for persistent local data.

The database is initialised by the application during startup.

The database location is managed through Qt application-data location handling rather than requiring a database file to be committed to Git.

Local databases are excluded from version control.

## 4.2 Database structures

The current schema includes the following data areas.

| Table | Purpose |
|---|---|
| `tasks` | Task records |
| `calendar_events` | Calendar events |
| `notes` | Notes |
| `logbook_entries` | Daily Logbook entries |
| `focus_sessions` | Focus session history |
| `preferences` | Application preferences |
| `music_tracks` | Imported music metadata |
| `music_playlists` | User playlists |
| `music_playlist_tracks` | Playlist-to-track relationships |

The music schema also defines indexes for commonly searched music fields and playlist ordering.

### Music table details

`music_tracks` stores information such as:

- Track ID
- File path
- Title
- Artist
- Album
- Duration
- Genre
- Track number
- Year
- Artwork path
- File size
- Date added
- Favourite status

`music_playlists` stores playlist identity and descriptive information.

`music_playlist_tracks` stores playlist membership and ordering, with foreign-key relationships and cascading deletion of relationship records.

### Database rules

- Use parameterised SQL queries.
- Keep database operations inside services or database modules.
- Do not place SQL business logic directly inside UI widgets.
- Use transactions where multiple related operations must succeed together.
- Preserve foreign-key integrity.
- Avoid deleting original user files when removing database records.
- Keep schema changes compatible with existing user databases.

**Important:** The schema has been extended during development. Before introducing future schema changes, inspect the current initialisation and migration behaviour. Do not assume that changing the table-creation script automatically migrates an existing database.

---

# 5. Service Layer

Services contain application logic and database operations.

They should remain independent of the presentation layer wherever practical.

## 5.1 TaskService

**Source:** `src/mochi/services/task_service.py`

Responsible for task-related operations.

The Tasks page uses this service rather than implementing database operations itself.

## 5.2 CalendarService

**Source:** `src/mochi/services/calendar_service.py`

Responsible for calendar-event operations.

It is shared by the Calendar workspace and the floating Calendar Widget.

This allows both interfaces to operate on the same calendar data.

## 5.3 NoteService

**Source:** `src/mochi/services/note_service.py`

Responsible for Notes data operations.

The Notes workspace uses this service for local notes management.

## 5.4 LogbookService

**Source:** `src/mochi/services/logbook_service.py`

Responsible for Daily Logbook data operations.

The Logbook page uses the service to manage daily entries and persistent storage.

The Logbook functionality has been implemented and manually checked.

## 5.5 FocusService

**Source:** `src/mochi/services/focus_service.py`

Responsible for Focus session data and persistence.

It supports the Focus workspace and records session information in the database.

The Focus service is separate from the floating timer presentation.

## 5.6 MusicService

**Source:** `src/mochi/services/music_service.py`

Responsible for the local music library.

Current responsibilities include:

- Supported audio-format handling.
- Local file import.
- Folder import.
- Metadata extraction using Mutagen.
- Duplicate detection.
- Track listing.
- Searching.
- Removing library records.
- Favourite status.
- Playlist creation and management.
- Adding and removing tracks from playlists.
- Playlist ordering.

Removing a track from the Widget library should remove its library record, not delete the user's original audio file.

The complete Music Library interface has not yet been implemented.

---

# 6. Focus and Pomodoro System

## 6.1 Focus workspace

**Source:** `src/mochi/workspace/pages/focus_page.py`

The Focus page provides the user interface for starting and managing focus sessions.

Current functionality includes:

- Starting a session.
- Pausing a session.
- Resuming a session.
- Resetting a session.
- Completing a session.
- Displaying session state.
- Recording session information through FocusService.

The session duration can be configured.

The current implementation uses Focus as the session type rather than exposing a separate session-mode selection.

## 6.2 Floating timer

**Source:** `src/mochi/companion/pomodoro.py`

The floating timer provides an independent timer overlay.

It is designed to remain accessible when the main workspace is minimised or hidden.

The controller and overlay coordinate timer state and visual updates.

Current manually checked behaviour includes:

- Timer start.
- Pause and resume.
- Reset.
- Starting again after reset.
- Completion handling.
- Completion sound playback.

## 6.3 Focus sounds

**Assets:** `assets/sounds/`

The project includes four offline sound choices:

- `default.wav`
- `chime.wav`
- `alert.wav`
- `gentle.wav`

Settings allow selection and preview of the available sounds.

These sounds are bundled local assets, so playback does not require an online service.

---

# 7. Daily Logbook

**Files:**
- `src/mochi/services/logbook_service.py`
- `src/mochi/workspace/pages/logbook_page.py`

The Daily Logbook is a productivity section for recording daily entries.

Its service handles persistent data operations, while the page handles presentation and interaction.

The feature has been implemented and manually checked.

Future improvements should preserve existing entries and avoid unnecessary changes to the underlying data model.

---

# 8. Desktop Widgets

## 8.1 DesktopWidgetsWindow

**Source:** `src/mochi/widgets/desktop_widgets.py`

This is the management interface for the floating desktop widgets.

It coordinates the creation, visibility, and shutdown of the widget windows.

Current integrated components:

- ClockWidget
- SystemMonitorWidget
- CalendarWidget
- MusicMiniPlayerWidget

The window displays component status and provides controls to show or hide the individual widgets.

The Desktop Widgets interface and its card styling are still prototypes.

## 8.2 Digital Clock

**Source:** `src/mochi/widgets/clock_widget.py`

The Digital Clock is an independent floating window.

Current behaviour includes:

- Live time display.
- Date display.
- Periodic updates.
- Dragging.
- Hiding and showing.
- Independent visibility from the widget-management window.

## 8.3 System Monitor

**Source:** `src/mochi/widgets/system_monitor.py`

Uses `psutil` to display:

- CPU usage.
- RAM utilisation.
- Battery percentage.
- Battery charging information.

The monitor updates periodically.

A fallback is provided when battery information is unavailable.

## 8.4 Calendar Widget

**Source:** `src/mochi/widgets/calendar_widget.py`

The floating Calendar Widget uses the shared CalendarService.

Its current functionality includes:

- Monthly navigation.
- Date selection.
- Event listing.
- Event counts.
- Adding events.
- Editing events.
- Deleting events.
- Refreshing calendar data.
- Hiding and showing the widget.

It communicates changes through signals so that the workspace calendar can refresh.

The Calendar Widget is functional but requires further visual and interaction refinement.

---

# 9. Music System

The Music System is intended to become a complete local music experience rather than only a small playback control.

Its current implementation provides the foundation for local library management and playback.

## 9.1 MusicService

**Source:** `src/mochi/services/music_service.py`

Handles local music metadata and library operations.

Supported extensions currently include:

- MP3
- WAV
- FLAC
- M4A
- AAC
- OGG
- OPUS
- AIFF
- AIF
- APE
- WV
- TTA
- DSF
- DFF

Actual playback compatibility depends on the installed Qt Multimedia backend and available codecs. A format being accepted for metadata extraction does not guarantee playback on every Windows installation.

Mutagen is used for audio metadata extraction.

## 9.2 MusicPlaybackController

**Source:** `src/mochi/services/music_player.py`

Uses Qt Multimedia components:

- `QMediaPlayer`
- `QAudioOutput`

The controller provides:

- Track queue management.
- Current track selection.
- Play.
- Pause.
- Stop.
- Toggle playback.
- Next track.
- Previous track.
- Seek.
- Volume.
- Mute.
- Shuffle.
- Repeat modes: off, all, and one.
- Playback-state signals.
- Track and position signals.
- Playback error signals.

The controller is instantiated and integrated through the application lifecycle.

## 9.3 Music Mini-player

**Source:** `src/mochi/widgets/music_mini_player.py`

The floating mini-player provides:

- Track title.
- Artist.
- Progress slider.
- Elapsed and total time.
- Previous.
- Play/pause.
- Next.
- Volume control.
- Music Library button.
- Dragging.
- Hiding and showing.

The mini-player is integrated into Desktop Widgets.

The Music Library button currently provides an interface entry point, but the complete Music Library window is not yet implemented.

## 9.4 Music System roadmap

The following functionality remains incomplete:

1. Full Music Library browsing interface.
2. Track, artist, and album browsing.
3. Complete playlist and favourite workflows through the UI.
4. Persistent playback queue.
5. Playback-position restoration.
6. Windows media-session metadata detection.
7. WASAPI loopback capture.
8. Audio fingerprint generation and local catalogue matching.
9. Evaluation of optional free online recognition services.

## 9.5 External music recognition limitations

The intended recognition approach is:

1. Read Windows media-session metadata where available.
2. If metadata is unavailable, investigate system-audio capture through WASAPI loopback.
3. Compare captured audio fingerprints against the user's own local library.
4. Investigate an optional free online recognition service only if a genuinely no-cost solution is available.

Audio fingerprinting does not identify arbitrary unknown music by itself. It requires a reference catalogue or recognition database.

If no match is available, Widget must report that the song could not be identified.

### Financial constraints

The project must not introduce:

- Mandatory paid APIs.
- Paid recognition subscriptions.
- Paid service dependencies.
- Hidden ongoing charges.
- Unapproved usage-based billing.

If a feature cannot be implemented under these constraints, explain the limitation instead of silently introducing a paid service.

---

# 10. Mochi Companion

**Source:** `src/mochi/companion/`

Mochi is a separate floating virtual pet.

Its intended purpose is to provide a lightweight desktop companion experience.

### Non-negotiable design rule

Mochi itself must never use AI.

Any future AI helper must be a separate, optional application component. It must not be required for the pet, productivity tools, or core application.

The companion's visual behaviour, animations, customisation, and interaction model may be improved later.

Preserve its independence from the main workspace.

---

# 11. Settings and Appearance

**Source:** `src/mochi/workspace/pages/settings_page.py`

The Settings page currently includes application settings and Focus sound selection/preview.

Appearance is an area for future development.

The intended design direction is expressive minimalism:

- Warm neutrals.
- Forest green.
- Charcoal.
- Navy.
- Muted teal.
- Dusty pink.
- Brown.
- Restrained gold.
- Rounded modular surfaces.
- Clear light/dark contrast.

Future work may include wallpaper-aware styling and more comprehensive customisation.

Do not assume that the current prototype styling is final.

---

# 12. Calendar Dialog Regression

**Source:** `src/mochi/workspace/pages/calendar_page.py`

A previous Windows crash was caused by assigning event data to:

`self.event`

This collided with the inherited Qt `QObject.event()` method.

The event data is now stored as:

`self.event_item`

The dialog also uses the intended parent relationship.

Regression coverage is included in:

`tests/test_calendar_dialog.py`

**Do not reintroduce `self.event` as an instance data attribute in Qt objects.**

---

# 13. Dependencies and Environment

## 13.1 Current dependencies

The project uses:

| Dependency | Purpose |
|---|---|
| `PySide6==6.12.0` | Desktop interface and Qt functionality |
| `Pillow` | Image processing |
| `pytest` | Automated testing |
| `psutil` | System information |
| `mutagen==1.48.1` | Audio metadata |

Qt Multimedia is provided through the installed PySide6 distribution.

Python requirement: **Python 3.11 or newer**.

## 13.2 Virtual environment

The development environment uses:

```powershell
.\.venv\Scripts\python.exe
```

Prefer this executable for project commands to avoid accidentally using another Python installation.

## 13.3 Launch command

From the project root:

```powershell
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe .\app.py
```

## 13.4 Test command

```powershell
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe -m pytest tests\ -q
```

## 13.5 Dependency verification

```powershell
.\.venv\Scripts\python.exe -m pip check
```

---

# 14. Testing

The project uses pytest.

The test suite includes coverage for:

- Calendar service.
- Calendar dialog.
- Calendar Widget.
- Database schema.
- Focus service.
- Logbook service.
- Music service.
- Notes service.
- Task service.

### Latest recorded verification

| Check | Result |
|---|---|
| Full automated test suite | 76 passed |
| Test duration | 5.05 seconds |
| Dependency check | No broken requirements found |

These results are the latest recorded baseline as of 7 November 2026.

### Manual verification reported

The user has manually checked:

- Launcher startup and component launching.
- Dashboard access.
- Desktop Widgets access.
- Mochi Companion access.
- Focus timer controls and completion.
- Focus sound playback.
- Daily Logbook operation.
- Digital Clock.
- System Monitor.
- Calendar event flow.
- Music mini-player visibility and basic integration.
- Desktop Widget card button labels.

Manual checks are not a substitute for regression testing after code changes.

### Development testing rules

After modifying application code:

1. Run the relevant targeted tests.
2. Run the full test suite.
3. Check application startup when integration code changes.
4. Manually verify affected GUI behaviour where practical.
5. Check `pip check` after dependency changes.
6. Record meaningful test results in the handoff documentation.

---

# 15. Git and Repository Management

**Repository:** `Vanshverma-56/Mochi-Desktop`
**Primary branch:** `main`

The project uses Git for version control.

### Git hygiene

Do not commit:

- `.venv/`
- Python cache files.
- Local SQLite database files.
- Environment secrets.
- Temporary `.bak` files.
- Temporary `.backup` files.
- Local test audio files.
- One-off development scripts.
- Generated temporary files.

Keep actual application assets such as the Focus sound files under version control.

Use meaningful commits grouped by feature or logical change.

Before pushing:

1. Inspect `git status`.
2. Inspect the staged diff.
3. Run tests.
4. Confirm temporary files are excluded.
5. Push the intended commits to `origin/main`.

Never overwrite existing project work or reset user changes without explicit permission.

---

# 16. Known Limitations and Deferred Work

The following are known development areas, not necessarily bugs.

| Area | Remaining work |
|---|---|
| Launcher | Visual redesign and interaction refinement |
| Dashboard | Comprehensive visual and usability improvements |
| Calendar Widget | UI polish and additional refinement |
| Desktop Widgets | More customisation and sizing options |
| Music | Full library UI and persistent playback |
| Music recognition | Media sessions, WASAPI, fingerprint matching, optional free service investigation |
| Settings | More complete appearance controls |
| Mochi | More animations and companion interactions |
| Application | Broader integration and lifecycle testing |
| Distribution | Packaging and installer work |

Do not treat these as completed features.

---

# 17. Recommended Development Workflow

When starting a new task:

1. Read this handbook.
2. Read `MOCHI_PROJECT_GUIDE_AND_HANDOFF.md`.
3. Inspect the relevant existing source files.
4. Understand the current implementation before modifying it.
5. Preserve existing working behaviour.
6. Make focused changes.
7. Add or update tests.
8. Run the full test suite.
9. Manually verify relevant GUI behaviour.
10. Update README, CHANGELOG, and handoff documentation when project status changes.
11. Commit changes in meaningful groups when authorised.

Avoid unnecessary refactoring while implementing a feature.

Prefer understandable, maintainable code over overly complicated abstractions.

---

# 18. Final Project Rules

These requirements apply to future development:

1. The desktop application is named **Widget**.
2. The floating pet is named **Mochi**.
3. The GitHub repository remains **Mochi-Desktop**.
4. Mochi is strictly non-AI.
5. Core functionality should remain offline-first.
6. Do not introduce mandatory paid APIs, subscriptions, or hidden costs.
7. Do not delete or modify users' original music files when managing library records.
8. Preserve existing working functionality.
9. Keep services, UI, and database responsibilities separated.
10. Distinguish completed features from planned features.
11. Treat the current UI as a prototype until comprehensive refinement is completed.
12. Keep technical documentation current as architecture changes.

---

**End of Technical Handbook**

**Last documented baseline:** 7 November 2026
**Automated tests:** 76 passed
**Dependency health:** Clean
**Development status:** Active