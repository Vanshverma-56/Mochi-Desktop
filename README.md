# Widget

**Widget** is a Windows desktop productivity application with a separate floating virtual pet companion named **Mochi**.

The project combines a productivity workspace, independent desktop widgets, and a lightweight companion experience. Its core functionality is designed to work locally, without requiring AI services or paid APIs.

**GitHub repository:** `Vanshverma-56/Mochi-Desktop`

---

## 1. Project Vision

Widget aims to bring everyday productivity tools and a virtual desktop companion together in one customisable Windows application.

The main principles are:

- **Offline-first:** Core features should work locally.
- **Non-AI companion:** Mochi is a traditional virtual pet, not an AI assistant.
- **Modular architecture:** Dashboard, desktop widgets, and Mochi Companion are separate components.
- **Local data:** User information and application data are stored locally.
- **No mandatory costs:** No paid APIs, subscriptions, paid service dependencies, or hidden ongoing costs.
- **Expressive minimalism:** A warm, polished, customisable interface rather than a generic productivity dashboard.

The application is actively being developed. Functional foundations come first; comprehensive UI refinement and visual polish will follow.

## 2. Current Implementation Status

### Implemented features

| Component | Functionality |
|---|---|
| Application Launcher | Launch Dashboard, Desktop Widgets, Mochi Companion, or all components; exit Widget |
| Dashboard | Main productivity workspace and navigation |
| Tasks | Local task-management service and interface |
| Calendar | Calendar events, event dialogs, and calendar service |
| Notes | Local notes-management service and interface |
| Daily Logbook | Daily entries backed by a dedicated service |
| Focus | Focus sessions, Pomodoro-style timer, pause/resume/reset, and completion handling |
| Focus Sounds | Offline sound options and sound-selection settings |
| Mochi Companion | Separate floating virtual pet window |
| Digital Clock | Independent floating clock displaying time and date |
| System Monitor | Live CPU, RAM, and battery information |
| Calendar Widget | Independent floating calendar connected to the calendar service |
| Music Service | Local music metadata extraction and library-management foundation |
| Music Playback | Local audio playback controller using Qt Multimedia |
| Music Mini-player | Floating mini-player integrated into Desktop Widgets |
| Database | SQLite storage for application data, preferences, and music-library structures |

### Planned or incomplete features

The following are future development tasks and should not be considered complete:

- Full Music Library browsing and management interface.
- More complete playlist and favourite workflows through the UI.
- Persistent playback queue and playback-position restoration.
- Windows media-session detection for music playing in other applications.
- WASAPI loopback audio capture.
- Local audio fingerprint matching against the user's music library.
- Investigation of optional, genuinely free online song-recognition services.
- More extensive desktop-widget resizing, positioning, and customisation.
- Expanded appearance settings and wallpaper-aware styling.
- Additional Mochi animations and behaviours.
- Comprehensive UI consistency, accessibility, and interaction improvements.

## 3. Application Components

Widget currently has three main independently managed components.

### Dashboard

The main productivity workspace.

Sections include:

- Dashboard
- Calendar
- Tasks
- Notes
- Daily Logbook
- Focus
- Settings / Appearance

### Desktop Widgets

A separate floating widget environment containing:

- Digital Clock
- System Monitor
- Calendar Widget
- Music Mini-player

These widgets are designed to remain separate from the main workspace.

### Mochi Companion

Mochi is the floating virtual pet companion.

Mochi is intentionally non-AI. Future AI functionality, if ever introduced, must remain a separate optional helper and must not turn the pet itself into an AI assistant.

### Application Launcher

The launcher is the central starting point for the application.

It provides access to:

- Dashboard
- Desktop Widgets
- Mochi Companion
- Launch All
- Exit Widget

The current launcher is a functional prototype and may be redesigned later.

Widget does not currently require automatic Windows startup.

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Application language |
| PySide6 | Desktop interface and Qt functionality |
| SQLite | Local database |
| Pillow | Image handling |
| psutil | CPU, memory, and battery information |
| Mutagen | Audio metadata extraction |
| Qt Multimedia | Audio playback |
| pytest | Automated testing |

## 5. Project Structure

The project follows a modular structure.

```text
Widget/
│
├── app.py
├── assets/
│   └── sounds/
│
├── src/
│   └── mochi/
│       ├── appearance/
│       ├── companion/
│       ├── core/
│       ├── database/
│       ├── integrations/
│       ├── services/
│       ├── widgets/
│       └── workspace/
│           └── pages/
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

### Main module responsibilities

- `core/` — application lifecycle and launcher.
- `database/` — SQLite connection and schema.
- `services/` — application logic and data operations.
- `workspace/` — main productivity window and pages.
- `widgets/` — independent floating desktop widgets.
- `companion/` — Mochi companion and Focus timer overlay.
- `appearance/` — appearance-related functionality.
- `integrations/` — external and Windows-specific integrations.
- `tests/` — automated test suite.

## 6. Development Environment

The project is developed on Windows using:

- Python 3.11.9
- PySide6 6.12.0
- Git
- Visual Studio Code
- PowerShell

### Clone the repository

```powershell
git clone https://github.com/Vanshverma-56/Mochi-Desktop.git
cd Mochi-Desktop
```

### Create a virtual environment

```powershell
py -3.11 -m venv .venv
```

### Install dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Launch Widget

From the project root:

```powershell
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe .\app.py
```

### Run automated tests

```powershell
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe -m pytest tests\ -q
```

**Latest verified test result:** 76 passed.

**Latest dependency check:** No broken requirements found.

These results reflect the latest recorded verification run, not a guarantee that every future change has been tested.

## 7. Database and Data Storage

Widget uses SQLite for local application data.

The database schema currently includes structures for:

- Tasks
- Calendar events
- Notes
- Logbook entries
- Focus sessions
- Preferences
- Music tracks
- Music playlists
- Playlist-track relationships

Music imports reference the user's existing local audio files. Widget should not delete or modify original audio files when removing a track from its library.

## 8. Music System Direction

The Music System is intended to become a unified local music experience.

Its planned capabilities include:

1. Importing supported local audio files.
2. Searching tracks, artists, and albums.
3. Playing, pausing, seeking, and changing volume.
4. Previous/next track controls.
5. Shuffle and repeat.
6. Favourites and playlists.
7. Persistent music-library data.
8. A compact floating mini-player and expanded music interface.
9. Detection of music playing in other Windows applications.

For external music recognition, the intended order is:

1. Check Windows media-session metadata.
2. If metadata is unavailable, investigate WASAPI loopback audio capture.
3. Compare audio fingerprints against the user's local music library.
4. Investigate an optional free online recognition service only if a genuinely no-cost solution is feasible.

An audio fingerprint alone cannot identify arbitrary unknown songs without a reference catalogue. Widget must report when it cannot identify a song rather than inventing a result.

**Financial constraint:** The Music System must not introduce mandatory paid APIs, subscriptions, or hidden costs.

## 9. Design Direction

The intended design is expressive minimalism.

Visual direction includes:

- Warm neutrals.
- Forest green.
- Charcoal and navy.
- Muted teal.
- Dusty pink.
- Brown.
- Restrained gold accents.
- Rounded modular cards.
- Clear contrast between light and dark surfaces.
- Independent widget appearances.
- Optional wallpaper-aware styling.

The current interface is a functional prototype. Existing working functionality should be preserved while the design is gradually refined.

## 10. Development Principles

Future development should follow these rules:

- Keep modules focused and understandable.
- Separate business logic from UI code.
- Use services for database operations.
- Preserve existing working features.
- Add tests for new service and database functionality.
- Avoid unnecessary refactoring.
- Keep the application offline-first.
- Do not introduce paid APIs or hidden costs.
- Keep Mochi non-AI.
- Clearly distinguish implemented features from planned features.
- Update the handbook and handoff guide when architecture or project status changes.

## 11. Project Documentation

| Document | Purpose |
|---|---|
| `README.md` | Overview, current features, setup, and development principles |
| `CHANGELOG.md` | Development history and notable changes |
| `MOCHI_PROJECT_HANDBOOK.md` | Technical architecture and implementation reference |
| `MOCHI_PROJECT_GUIDE_AND_HANDOFF.md` | Project context, current status, and continuation instructions |

---

**Project status:** Active development.

**Application name:** Widget.

**Virtual companion:** Mochi.

**Repository:** Mochi-Desktop.