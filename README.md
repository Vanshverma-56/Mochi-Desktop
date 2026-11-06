# Mochi

**Mochi** is a Windows desktop productivity application built with Python and PySide6. It combines a personal productivity workspace with a floating desktop companion.

**Project status:** Active development
**Documentation updated:** 6 November 2026

## Features

### Dashboard
- Productivity overview.
- Analog clock with digital clock toggle.
- Date display.
- Foundation for future dashboard widgets and customisation.

### Calendar
- Calendar month navigation and date selection.
- Create, edit and delete events.
- Custom Mochi-styled event dialogs.
- Input validation and past-date restrictions.
- Fixed a native Windows crash caused by a Qt event-handler name collision.
- Seven Calendar dialog regression tests.
- Add Event flow manually confirmed in the original Windows application.

### Tasks
- Create, view, edit and delete tasks.
- Priorities, descriptions, categories and due dates.
- Search by title, description and category.
- Filter tasks into Upcoming, Pending, Completed and No Due Date.
- Group tasks by due date and sort by priority.
- Mark tasks complete and undo recent completion actions.

### Notes
- Create, view, edit and delete notes.
- Note categories and search.
- SQLite-backed persistence.

### Floating Desktop Companion
- Floating companion window foundation.
- Further interactions and appearance customisation planned.

### Additional Workspace Pages
- **Daily Logbook:** Full workflows pending.
- **Focus:** Timer and session tracking pending.
- **Settings & Appearance:** Persistent settings and customisation pending.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11+ | Application language |
| PySide6 | Desktop GUI |
| SQLite | Local database |
| pytest | Automated testing |
| psutil | System and process information |

## Getting Started

### Requirements
- Windows 10 or Windows 11.
- Python 3.11 or newer.
- Git.

### Installation

Clone the repository:

```powershell
git clone https://github.com/Vanshverma-56/Mochi-Desktop.git
cd Mochi-Desktop
```

Create and activate a virtual environment:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, you can run the project without activating the environment by calling its Python executable directly. For example:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe app.py
.\.venv\Scripts\python.exe -m pytest -q
```
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -e .
pip install pytest
```

Run Mochi:

```powershell
python app.py
```

## Running Tests

Execute the full automated test suite:

```powershell
python -m pytest -q
```

Latest recorded result: **31 passed in 1.34s**, reported on 6 November 2026.

The automated suite includes database, Task, Notes and Calendar tests, including seven Calendar dialog regression tests.

The Calendar Add Event flow was additionally confirmed manually in the original Windows application. This does not establish that every GUI workflow has been manually tested.

## Data Storage

Mochi uses a local SQLite database. Application data is stored in the operating system's application data directory rather than in the source repository.

## Development Roadmap

### Implemented
- [x] Initial application and GUI foundation.
- [x] SQLite database foundation.
- [x] Task service and interface.
- [x] Notes service and interface.
- [x] Floating companion foundation.
- [x] Dashboard and analog clock.
- [x] Collapsible workspace sidebar.
- [x] Calendar event management.
- [x] Custom Calendar dialogs and validation.
- [x] Calendar crash fix and regression tests.

### Planned / In Progress
- [ ] Complete Daily Logbook workflows.
- [ ] Implement Focus timer and session tracking.
- [ ] Complete Settings and Appearance persistence.
- [ ] Further Dashboard improvements.
- [ ] Independent desktop widgets.
- [ ] Companion interactions and customisation.
- [ ] Broader manual GUI verification.

## Project Documentation

| Document | Purpose |
|---|---|
| `MOCHI_PROJECT_HANDBOOK.md` | Technical architecture, implementation details, decisions and testing. |
| `MOCHI_PROJECT_GUIDE_AND_HANDOFF.md` | Development handoff and instructions for continuing the project. |
| `CHANGELOG.md` | Chronological record of notable changes and fixes. |

Keep these documents synchronised as the project evolves.

## Repository

[GitHub - Mochi Desktop](https://github.com/Vanshverma-56/Mochi-Desktop)

## License

No open-source license has currently been specified.