# Changelog

All notable changes to Mochi are documented here.

## [Unreleased]

### Fixed

- Resolved a crash when opening the Calendar Add Event and Edit Event dialogs.
- Fixed the Qt event-handler name collision caused by storing an event record in `self.event`; the attribute is now named `self.event_item`.
- Updated Calendar dialogs to receive the Calendar page as their parent.

### Tests

- Added `tests/test_calendar_dialog.py` with regression coverage for dialog construction, parent handling, title validation, time validation and successful submission.
- Latest full automated test run: **31 passed in 1.34s**.
- The Calendar Add Event flow was manually launched and confirmed working in the original Windows application.

### Documentation

- Updated the README, technical handbook and development handoff to reflect the current implementation and verification status.

---

\## \[0.1.0] - Initial Development



\### Added

\- Initial Python desktop application structure.

\- PySide6 application foundation.

\- Floating desktop companion window.

\- SQLite database connection and schema initialisation.

\- Database tables for tasks, calendar events, notes, logbook entries, focus sessions and preferences.

\- Task management service with create, retrieve, update, completion and deletion operations.

\- Task management interface with priorities, categories, descriptions and due dates.

\- Task search and filtering.

\- Due-date grouping and priority-based sorting.

\- Completion undo interaction.

\- Initial dashboard implementation.

\- Automated database and task-service tests.



\### In Progress

\- Workspace navigation improvements.

\- Dashboard redesign.

\- Functional calendar, notes, logbook and focus modules.

\- Settings and appearance customisation.

\- Independent desktop widgets.
