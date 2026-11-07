
def initialise_database(database):
    """Create the initial database tables."""

    connection = database.connect()

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            priority TEXT NOT NULL DEFAULT 'Medium',
            category TEXT DEFAULT 'General',
            due_date TEXT,
            is_completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            start_datetime TEXT NOT NULL,
            end_datetime TEXT,
            category TEXT DEFAULT 'General',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT DEFAULT '',
            category TEXT DEFAULT 'General',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS logbook_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT NOT NULL,
            title TEXT DEFAULT '',
            content TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS focus_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            duration_minutes INTEGER NOT NULL,
            session_type TEXT DEFAULT 'Pomodoro',
            completed INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS music_tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            artist TEXT DEFAULT 'Unknown Artist',
            album TEXT DEFAULT 'Unknown Album',
            duration_seconds REAL DEFAULT 0,
            genre TEXT DEFAULT '',
            track_number INTEGER,
            year INTEGER,
            artwork_path TEXT,
            file_size INTEGER,
            date_added TEXT NOT NULL,
            is_favorite INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS music_playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS music_playlist_tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id INTEGER NOT NULL,
            track_id INTEGER NOT NULL,
            position INTEGER NOT NULL DEFAULT 0,
            added_at TEXT NOT NULL,
            FOREIGN KEY (playlist_id)
                REFERENCES music_playlists(id)
                ON DELETE CASCADE,
            FOREIGN KEY (track_id)
                REFERENCES music_tracks(id)
                ON DELETE CASCADE,
            UNIQUE (playlist_id, track_id)
        );

        CREATE INDEX IF NOT EXISTS idx_music_tracks_title
            ON music_tracks(title);

        CREATE INDEX IF NOT EXISTS idx_music_tracks_artist
            ON music_tracks(artist);

        CREATE INDEX IF NOT EXISTS idx_music_tracks_album
            ON music_tracks(album);

        CREATE INDEX IF NOT EXISTS idx_music_playlist_tracks_order
            ON music_playlist_tracks(playlist_id, position);
        """
    )

    connection.commit()
