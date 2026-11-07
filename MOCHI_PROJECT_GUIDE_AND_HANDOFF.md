# Widget — Project Guide and Development Handoff

**Purpose:** Continuity document for future development sessions
**Application:** Widget
**Virtual companion:** Mochi
**GitHub repository:** `Vanshverma-56/Mochi-Desktop`
**Primary branch:** `main`
**Platform:** Windows
**Last updated:** 7 November 2026

---

# 1. Read This First

Widget is a Windows desktop productivity application with a separate floating virtual pet companion named Mochi.

The project has three main components:

1. Dashboard — the main productivity workspace.
2. Desktop Widgets — independent floating desktop tools.
3. Mochi Companion — the separate floating pet.

The project is actively being developed. The current UI is a functional prototype, not the final visual design.

**The immediate development philosophy is to implement the planned functionality first, then undertake comprehensive UI, interaction, and design refinement.**

Before changing anything, read:

- `README.md` — project overview and setup.
- `MOCHI_PROJECT_HANDBOOK.md` — technical architecture and implementation details.
- This document — current status and continuation instructions.
- `CHANGELOG.md` — development history.

Do not assume that older project notes or previous AI-generated suggestions describe the current implementation accurately. Inspect the actual source code before making changes.

# 2. Naming and Product Identity

Use these names consistently:

| Name | Meaning |
|---|---|
| Widget | Overall desktop application and project |
| Mochi | Floating virtual pet companion |
| Mochi-Desktop | Existing GitHub repository name |

Repository:

`https://github.com/Vanshverma-56/Mochi-Desktop`

Do not rename the GitHub repository unnecessarily.

# 3. Non-Negotiable Project Requirements

These requirements must be respected throughout development.

## 3.1 Mochi must remain non-AI

Mochi is a traditional virtual pet companion.

Do not integrate an AI model into the pet itself.

If an AI helper is considered in the future, it must be a separate, optional component and must not be necessary for the core application.

## 3.2 No paid services or hidden costs

The project must not introduce:

- Paid API keys.
- Usage-based paid APIs.
- Mandatory subscriptions.
- Paid fallback services.
- Hidden ongoing charges.
- Features that silently require a paid service.

The user does not want recurring costs.

If a proposed feature cannot be delivered under these constraints, explain the limitation and obtain approval before introducing an alternative with costs.

## 3.3 Offline-first functionality

Core productivity functionality should work locally.

Use SQLite and local services where appropriate.

Optional online functionality must never make the core application dependent on an external service.

## 3.4 Preserve existing functionality

Do not break working components while implementing new ones.

Avoid broad refactoring when a focused change will solve the problem.

Inspect existing implementations and tests before editing.

## 3.5 UI refinement comes after functional implementation

The current interface is not final.

Do not spend development time treating every prototype design decision as permanent.

First complete the agreed functional foundations. Then undertake a dedicated refinement phase.

# 4. Current Application Structure

Widget currently has three independently managed components.

## 4.1 Dashboard

The productivity workspace contains:

- Dashboard
- Calendar
- Tasks
- Notes
- Daily Logbook
- Focus
- Settings / Appearance

The Dashboard is the home page inside Widget. It does not replace the Windows desktop.

## 4.2 Desktop Widgets

The floating desktop-widget environment currently includes:

- Digital Clock.
- System Monitor.
- Calendar Widget.
- Music Mini-player.

The widgets are designed to operate independently of the main workspace.

## 4.3 Mochi Companion

Mochi is a separate floating pet window.

It is intended to be draggable and independently accessible.

Its appearance and behaviour can be improved later without turning it into an AI assistant.

## 4.4 Launcher

The launcher provides access to:

- Dashboard.
- Desktop Widgets.
- Mochi Companion.
- Launch All.
- Exit Widget.

The current launcher is a functional prototype.

The user has manually confirmed that it opens and launches the three main components.

The launcher should remain available as the central control point while Widget is running.

The X/close behaviour and explicit Exit Widget behaviour are intentionally different. Do not casually change the application lifecycle without testing all components.

# 5. Current Implementation Status

## 5.1 Implemented and manually checked

| Feature | Status |
|---|---|
| Application launcher | Functional prototype; manually checked |
| Dashboard | Implemented |
| Tasks | Implemented |
| Calendar workspace | Implemented |
| Notes | Implemented |
| Daily Logbook | Implemented and manually checked |
| Focus service | Implemented |
| Focus workspace | Implemented |
| Floating Pomodoro timer | Implemented and manually checked |
| Focus sounds | Implemented and manually checked |
| Settings sound selection | Implemented |
| Mochi Companion | Existing floating companion foundation |
| Digital Clock | Implemented and manually checked |
| System Monitor | Implemented and manually checked |
| Calendar Widget | Implemented; further refinement remains |
| Music metadata/library service | Implemented foundation |
| Music playback controller | Implemented and smoke-tested |
| Music mini-player | Implemented foundation and manually checked |
| SQLite music tables | Implemented |

## 5.2 Important manual checks already performed

The user has confirmed the following behaviour:

### Launcher

- Launcher opens.
- Dashboard can be launched.
- Desktop Widgets can be launched.
- Mochi Companion can be launched.
- The launcher provides the initial working control interface.

### Focus

A short one-minute session was tested.

- Start works.
- Pause works.
- Resume works.
- Reset works.
- The floating timer remains accessible when the workspace is minimised.
- The timer can be started again after reset.
- Completion handling works.
- Completion sound plays.

### Daily Logbook

The user manually confirmed that the Logbook works correctly.

### Clock and System Monitor

Both widgets were tested together.

- They work independently.
- They update their information.
- They can be dragged.
- They can be hidden and shown.

### Calendar

The Calendar event flow has been manually checked.

The separate floating Calendar Widget is implemented but still requires further UI refinement.

### Music mini-player

The user confirmed that the Music Player window appears and closes correctly, while the existing widgets continue to work.

A local test WAV file was used to verify playback through the playback controller.

The temporary test audio file must not be included in Git.

These manual checks are useful evidence of functionality, but they do not replace automated regression tests.

# 6. Latest Automated Test Baseline

As of 7 November 2026:

76 passed in 5.05s

Dependency verification:

`No broken requirements found.`

Commands used:

```powershell
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe -m pytest tests\ -q

.\.venv\Scripts\python.exe -m pip check
```

The baseline is 76 passing tests.

Always rerun the full suite after code changes. Update this document and the changelog if the verified result changes.

# 7. Development Environment

The user's development environment:

| Tool | Version / Details |
|---|---|
| Operating system | Windows |
| Python | 3.11.9 |
| PySide6 | 6.12.0 |
| Git | 2.56.0.windows.2 |
| Visual Studio Code | 1.143.0 |
| Shell | Windows PowerShell |
| Project folder | `C:\Users\VANSH\OneDrive\Documents\Projects\Widget` |

The project uses a virtual environment.

Always prefer:

```powershell
.\.venv\Scripts\python.exe
```

for Python commands.

## Launch Widget

From the project root:

```powershell
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe .\app.py
```

## Run the test suite

```powershell
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe -m pytest tests\ -q
```

## Check dependencies

```powershell
.\.venv\Scripts\python.exe -m pip check
```

# 8. Important Source Files

Inspect these files before modifying the associated features.

| File | Responsibility |
|---|---|
| `src/mochi/core/application.py` | Central application controller and lifecycle |
| `src/mochi/core/launcher.py` | Application launcher |
| `src/mochi/database/connection.py` | SQLite connection |
| `src/mochi/database/schema.py` | Database schema |
| `src/mochi/services/task_service.py` | Task operations |
| `src/mochi/services/calendar_service.py` | Calendar operations |
| `src/mochi/services/note_service.py` | Notes operations |
| `src/mochi/services/logbook_service.py` | Daily Logbook operations |
| `src/mochi/services/focus_service.py` | Focus session operations |
| `src/mochi/services/music_service.py` | Music library and metadata |
| `src/mochi/services/music_player.py` | Music playback controller |
| `src/mochi/companion/pomodoro.py` | Floating Focus timer |
| `src/mochi/widgets/desktop_widgets.py` | Desktop Widgets management window |
| `src/mochi/widgets/clock_widget.py` | Floating Digital Clock |
| `src/mochi/widgets/system_monitor.py` | Floating System Monitor |
| `src/mochi/widgets/calendar_widget.py` | Floating Calendar Widget |
| `src/mochi/widgets/music_mini_player.py` | Floating Music mini-player |
| `src/mochi/workspace/main_window.py` | Main productivity workspace |
| `src/mochi/workspace/pages/focus_page.py` | Focus interface |
| `src/mochi/workspace/pages/logbook_page.py` | Daily Logbook interface |
| `src/mochi/workspace/pages/settings_page.py` | Settings interface |

The full source tree and responsibilities are described in `MOCHI_PROJECT_HANDBOOK.md`.

# 9. Focus System — Current Behaviour

Focus functionality consists of three main pieces:

1. FocusService.
2. Focus workspace page.
3. Floating timer controller and overlay.

The Focus page manages session interaction, while the service handles persistent session information.

The floating timer provides access when the main workspace is minimised.

Offline sound assets are stored in:

`assets/sounds/`

Current assets:

- `default.wav`
- `chime.wav`
- `alert.wav`
- `gentle.wav`

Settings include sound selection and preview.

Preserve the current working start, pause, resume, reset, and completion behaviour.

# 10. Music System — Important Development Plan

The Music System is a significant feature and should be developed as a unified system.

The user does not want merely a basic player that depends on external music services.

The intended system combines:

1. A local music library.
2. Local audio playback.
3. Playlists and favourites.
4. A compact floating mini-player.
5. An expanded music interface.
6. Detection of music playing elsewhere on the laptop.

## 10.1 Already implemented

### MusicService

File:

`src/mochi/services/music_service.py`

Current capabilities include:

- Importing local audio files.
- Folder import.
- Metadata extraction with Mutagen.
- Duplicate detection.
- Track listing.
- Search.
- Favourite status.
- Playlist creation.
- Playlist management.
- Adding and removing playlist tracks.
- Playlist ordering.
- Removing a library record without deleting the original audio file.

Supported extensions currently include MP3, WAV, FLAC, M4A, AAC, OGG, OPUS, AIFF, AIF, APE, WV, TTA, DSF, and DFF.

Metadata support does not guarantee playback compatibility for every codec on every Windows installation.

### MusicPlaybackController

File:

`src/mochi/services/music_player.py`

Uses:

- `QMediaPlayer`
- `QAudioOutput`

Implemented controls include:

- Play.
- Pause.
- Stop.
- Previous.
- Next.
- Seek.
- Volume.
- Mute.
- Shuffle.
- Repeat off/all/one.
- Queue management.
- Playback-state signals.
- Track and position signals.
- Playback-error signals.

### MusicMiniPlayerWidget

File:

`src/mochi/widgets/music_mini_player.py`

The mini-player provides:

- Track title.
- Artist.
- Progress slider.
- Time display.
- Previous.
- Play/pause.
- Next.
- Volume.
- Music Library entry point.
- Dragging and hiding.

The Music Library button is an entry point for future integration. The complete Music Library window is not yet implemented.

## 10.2 Next Music System tasks

Follow this order unless the user changes priorities.

### Task 1 — Build the full Music Library interface

Create a dedicated music interface that can expand beyond the compact mini-player.

It should eventually support:

- Browse all imported tracks.
- Search songs.
- Browse artists.
- Browse albums.
- Show track information.
- Add tracks and folders.
- Manage favourites.
- Create playlists.
- Edit playlists.
- Remove tracks from the Widget library.
- Play selected tracks.
- Connect to the existing playback controller.

Do not recreate the music service or playback controller unnecessarily. Inspect and reuse the existing implementations.

### Task 2 — Connect mini-player and full library

The mini-player's Music Library action should open the full music interface.

Ensure both interfaces use the same playback controller and current playback state.

### Task 3 — Persist playback state

Investigate and implement:

- Current track.
- Queue.
- Queue order.
- Playback position.
- Volume.
- Shuffle.
- Repeat mode.

Ensure that restoring playback does not unexpectedly start audio without an appropriate user action.

### Task 4 — Windows media-session detection

Investigate Windows media-session metadata so Widget can detect information from music playing in other applications.

Desired information:

- Track title.
- Artist.
- Album, when available.
- Playback state.
- Artwork, when available.

This should be investigated as a Windows integration, not as a requirement for a paid API.

### Task 5 — WASAPI loopback capture

If media-session metadata is unavailable, investigate capturing system audio through Windows WASAPI loopback.

This is a fallback for extracting audio information, not a way to bypass streaming restrictions or DRM.

### Task 6 — Local audio fingerprint matching

Generate fingerprints and compare captured audio against the user's local music catalogue.

Remember that a local fingerprint comparison can only match songs represented in the reference catalogue.

It cannot identify every unknown song automatically.

### Task 7 — Investigate optional free recognition

Only investigate external recognition if a genuinely free and sustainable solution is feasible.

Do not introduce paid APIs, subscriptions, hidden charges, or mandatory online recognition.

If no suitable free service exists, keep this feature optional or explain that it cannot be implemented under the current financial constraints.

## 10.3 Music System privacy and file handling

- Do not upload local music without explicit user approval.
- Do not delete original music files when removing library entries.
- Do not redistribute copyrighted music.
- Do not claim to bypass DRM or streaming subscriptions.
- Be honest when song recognition fails.

# 11. Desktop Widgets — Current State

The Desktop Widgets window manages four floating components.

## Digital Clock

`src/mochi/widgets/clock_widget.py`

- Live time and date.
- Periodic updates.
- Dragging.
- Hide/show.

## System Monitor

`src/mochi/widgets/system_monitor.py`

- CPU usage.
- RAM usage.
- Battery percentage.
- Charging status.
- Battery-unavailable fallback.
- Periodic updates.

## Calendar Widget

`src/mochi/widgets/calendar_widget.py`

- Monthly navigation.
- Date selection.
- Event listing and counts.
- Add/edit/delete.
- Shared CalendarService.
- Refresh signalling.

## Music mini-player

`src/mochi/widgets/music_mini_player.py`

- Playback controls.
- Progress.
- Volume.
- Current track information.
- Music Library entry point.

The widget-management window and individual widgets are functional foundations. Visual redesign, more customisation, and further interaction refinement remain planned.

# 12. Important Previous Bugs and Fixes

## 12.1 Calendar Qt event collision

A Windows crash occurred because the Calendar dialog assigned an event object to:

`self.event`

This collided with Qt's inherited `QObject.event()` method.

The corrected attribute is:

`self.event_item`

Do not reintroduce this collision.

Regression coverage exists in:

`tests/test_calendar_dialog.py`

## 12.2 Music mini-player volume conversion

The mini-player slider uses a 0–100 range, while the playback controller uses a 0–1 volume value.

The conversion must be retained.

## 12.3 Desktop Widgets toggle-button labels

The widget-card toggle-button labels previously rendered blank.

The styling was corrected and the user confirmed the labels now work.

Avoid changing the relevant styling without checking the actual Windows rendering.

# 13. Database and Dependencies

The database currently includes:

- `tasks`
- `calendar_events`
- `notes`
- `logbook_entries`
- `focus_sessions`
- `preferences`
- `music_tracks`
- `music_playlists`
- `music_playlist_tracks`

Inspect `schema.py` and `connection.py` before changing the schema.

Check existing database compatibility when adding columns or tables.

Current dependencies:

```text
PySide6==6.12.0
Pillow
pytest
psutil
mutagen==1.48.1
```

The dependency definitions are maintained in:

- `pyproject.toml`
- `requirements.txt`

Keep them synchronised.

# 14. Testing Requirements

Before considering a feature complete:

1. Add tests for new service behaviour.
2. Add database tests for schema changes.
3. Run relevant targeted tests.
4. Run the full test suite.
5. Check dependencies after dependency changes.
6. Launch the application when integration code changes.
7. Manually verify affected GUI behaviour where practical.
8. Update the documentation.

Latest baseline:

- 76 automated tests passed.
- Dependency check clean.

Do not report tests as passing unless they were actually run.

Do not claim GUI verification merely because a module imports or tests pass.

# 15. Git and Commit History

Repository:

`Vanshverma-56/Mochi-Desktop`

Branch:

`main`

The latest known committed and pushed baseline before the current uncommitted feature work was:

`bf891b2 Update project documentation and handoff`

Previous relevant commit:

`e609e52 Fix Calendar dialog Qt event collision`

Other earlier commits established the Calendar, Notes, and Dashboard foundations.

The current feature work has not yet been committed or pushed.

The user has authorised:

- Updating project documentation.
- Preparing the work for GitHub.
- Pushing the current completed work.
- Splitting the work into as many meaningful commits as reasonably possible.

The user specifically prefers granular, feature-focused commits rather than one large commit.

**Do not create meaningless one-file commits just to inflate the count.**

Potential logical commit groups include:

1. Focus service and tests.
2. Floating Focus timer and Focus page.
3. Daily Logbook service and interface.
4. Settings and sound configuration.
5. Application launcher and lifecycle integration.
6. Desktop Clock and System Monitor.
7. Calendar Widget.
8. Music database and MusicService.
9. Music playback controller.
10. Music mini-player and Desktop Widgets integration.
11. Tests and bundled Focus sound assets.
12. Dependency and repository housekeeping.
13. README and changelog.
14. Technical handbook and handoff guide.

Adjust these groups after reviewing actual file dependencies and diffs.

## 15.1 Exclude temporary files

Do not commit these development artefacts:

- `create_focus_sounds.py`
- `finish_documentation_review.py`
- `fix_readme.py`
- `patch_focus_page.py`
- `patch_main_window.py`
- `repair_project_docs.py`
- `update_readme.py`
- `README.md.backup`
- `desktop_widgets.py.backup`
- `calendar_page.py.backup`
- `test_music.wav`
- Other temporary backups or local test files.

Do not delete these files automatically. The task is to exclude them from Git, not to remove them from the user's computer.

The `.gitignore` already excludes `.bak`, `*_backup.py`, and `.backup` files.

The Focus WAV assets under `assets/sounds/` are actual application assets and should be committed.

## 15.2 Commit and push procedure

Before committing:

1. Inspect `git status --short`.
2. Inspect tracked modifications.
3. Inspect new source files.
4. Verify temporary files are excluded.
5. Review `.gitignore`.
6. Review documentation.
7. Run the full test suite.
8. Check `pip check`.

Then stage and commit logical feature groups.

After each commit, inspect the result.

When all intended commits are ready, push to:

`origin main`

Do not reset, force-push, or overwrite remote history.

# 16. Recommended Next Development Priorities

The user wants planned functional development completed before comprehensive UI refinement.

The next major development priority is the Music System.

Recommended sequence:

1. Inspect the current MusicService, MusicPlaybackController, and mini-player.
2. Implement the complete Music Library interface.
3. Connect the mini-player to the full music interface.
4. Complete playlist and favourite workflows through the UI.
5. Implement playback-state persistence.
6. Investigate Windows media-session metadata.
7. Investigate WASAPI loopback capture.
8. Implement local fingerprint matching where feasible.
9. Investigate optional free recognition only if it satisfies the no-cost requirement.
10. Revisit other unfinished functional requirements.
11. Begin comprehensive UI and design refinement.

Do not assume every item is equally urgent. Confirm the next concrete task with the user if priorities change.

# 17. Instructions for Future AI Developers

When continuing this project:

- Use beginner-friendly explanations.
- Give precise Windows PowerShell commands.
- Work step by step and wait for output when a command needs verification.
- Prefer grouped commands when they are safe and easy to understand.
- When replacing a file, give the complete replacement content together with the instruction to replace it.
- Do not tell the user to clear a file and then make them wait for the replacement in a separate message.
- Avoid enormous nested PowerShell here-strings when a simpler VS Code editing workflow is suitable.
- Do not ask the user to repeat details already documented here.
- Inspect actual code before proposing modifications.
- Preserve working functionality.
- Avoid unrelated refactoring.
- Do not claim to have modified local files yourself.
- Do not claim a command succeeded without seeing its output.
- Do not commit or push without explicit authorisation.
- When authorised, use meaningful feature-focused commits.
- Keep this handoff document and the technical handbook updated as the project evolves.

The user prefers practical implementation over excessive planning and unnecessary theoretical explanations.

# 18. Final Project Snapshot

| Item | Current state |
|---|---|
| Application name | Widget |
| Companion name | Mochi |
| Repository | Mochi-Desktop |
| Platform | Windows |
| Language | Python 3.11.9 |
| UI | PySide6 |
| Database | SQLite |
| Architecture | Modular |
| Launcher | Implemented |
| Productivity workspace | Implemented foundation |
| Focus | Implemented |
| Logbook | Implemented |
| Floating Clock | Implemented |
| System Monitor | Implemented |
| Calendar Widget | Implemented foundation |
| Music System | Playback and library foundation implemented |
| Full Music Library UI | Pending |
| External music recognition | Pending investigation |
| Comprehensive UI refinement | Deferred |
| Latest automated tests | 76 passed |
| Dependency health | Clean |
| Current feature changes | Not yet committed or pushed |

---

**End of Project Guide and Handoff**

**Last updated:** 7 November 2026
**Next major development area:** Complete the Music System's library interface and remaining functional foundations.