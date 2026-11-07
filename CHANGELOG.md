# Changelog

All notable changes to **Widget** are documented in this file.

The project is under active development. This changelog distinguishes implemented functionality from planned work.

## [Unreleased]

### Added

- Application launcher for Dashboard, Desktop Widgets, and Mochi Companion.
- Independent floating Digital Clock widget with live time and date.
- Independent System Monitor displaying CPU usage, RAM usage, and battery status.
- Floating Calendar Widget connected to the existing Calendar service.
- Focus service for managing and recording focus sessions.
- Focus workspace interface with session controls.
- Floating Pomodoro timer overlay with start, pause, resume, reset, and completion handling.
- Offline Focus sound assets and sound-selection settings.
- Daily Logbook service and workspace interface.
- Music database structures for tracks, playlists, and playlist-track relationships.
- Local music metadata and library-management service using Mutagen.
- Music playback controller using Qt Multimedia.
- Floating Music mini-player integrated into Desktop Widgets.
- Automated tests for Focus, Logbook, Music, Calendar Widget, and database changes.

### Changed

- Integrated the application launcher into the application lifecycle.
- Added coordinated lifecycle management for Dashboard, Desktop Widgets, and Mochi Companion.
- Integrated Clock, System Monitor, Calendar Widget, and Music mini-player into Desktop Widgets.
- Expanded the SQLite database schema to support music-library data.
- Updated project dependencies to include Mutagen.
- Updated `requirements.txt` to match the project dependencies.
- Extended `.gitignore` to exclude temporary backup files.
- Updated the project README to reflect the current implementation and development direction.

### Fixed

- Fixed the Calendar event dialog crash caused by using `self.event`, which collided with Qt's `QObject.event()` method. The event data now uses `self.event_item`.
- Corrected Music mini-player volume conversion between its 0–100 slider and the playback controller's 0–1 volume value.
- Fixed the visibility of toggle-button labels in the Desktop Widgets interface.

### Verification

- Latest full automated test run: **76 passed** in 5.05 seconds.
- Latest dependency check: **No broken requirements found**.
- Manual checks have confirmed the launcher, Focus timer, Daily Logbook, Digital Clock, System Monitor, Calendar flow, and Music mini-player foundation.
- These checks do not imply that every planned feature or every interface state has been exhaustively