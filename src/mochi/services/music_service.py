
from datetime import datetime
from pathlib import Path
import sqlite3

from mutagen import File as MutagenFile

from mochi.database.connection import Database


class MusicService:
    """Manages the local music library, favourites and playlists."""

    SUPPORTED_EXTENSIONS = {
        ".mp3",
        ".wav",
        ".flac",
        ".m4a",
        ".aac",
        ".ogg",
        ".opus",
        ".aiff",
        ".aif",
        ".ape",
        ".wv",
        ".tta",
        ".dsf",
        ".dff",
    }

    def __init__(self, database: Database):
        self.database = database

    @staticmethod
    def _tag_value(tags, *keys, default=""):
        """Return the first available metadata value."""
        if not tags:
            return default

        for key in keys:
            values = tags.get(key)

            if values:
                value = values[0] if isinstance(
                    values, (list, tuple)
                ) else values

                if value is not None:
                    return str(value).strip()

        return default

    @staticmethod
    def _parse_integer(value):
        """Extract an integer from values such as '3/12'."""
        if not value:
            return None

        try:
            return int(str(value).split("/")[0].strip())
        except (TypeError, ValueError):
            return None

    def _extract_metadata(self, file_path):
        """Read metadata from a supported local audio file."""
        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(
                f"Audio file not found: {path}"
            )

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported audio format: {path.suffix}"
            )

        try:
            audio = MutagenFile(str(path), easy=True)
        except Exception as exc:
            raise ValueError(
                f"Could not read audio metadata: {exc}"
            ) from exc

        if audio is None:
            raise ValueError(
                "The file is not a supported or readable audio file."
            )

        tags = audio.tags or {}

        title = self._tag_value(
            tags, "title", default=path.stem
        )

        artist = self._tag_value(
            tags, "artist", "albumartist",
            default="Unknown Artist"
        )

        album = self._tag_value(
            tags, "album", default="Unknown Album"
        )

        genre = self._tag_value(
            tags, "genre", default=""
        )

        track_number = self._parse_integer(
            self._tag_value(tags, "tracknumber")
        )

        year = self._parse_integer(
            self._tag_value(
                tags, "date", "originaldate", "year"
            )
        )

        duration = 0.0

        if audio.info:
            duration = float(
                getattr(audio.info, "length", 0) or 0
            )

        return {
            "file_path": str(path.resolve()),
            "title": title or path.stem,
            "artist": artist or "Unknown Artist",
            "album": album or "Unknown Album",
            "duration_seconds": duration,
            "genre": genre,
            "track_number": track_number,
            "year": year,
            "artwork_path": None,
            "file_size": path.stat().st_size,
        }

    def add_track(self, file_path):
        """Import one audio file into the music library."""
        metadata = self._extract_metadata(file_path)
        connection = self.database.connect()

        existing = connection.execute(
            "SELECT * FROM music_tracks WHERE file_path = ?",
            (metadata["file_path"],),
        ).fetchone()

        if existing:
            return dict(existing)

        metadata["date_added"] = datetime.now().isoformat(
            timespec="seconds"
        )

        columns = ", ".join(metadata.keys())
        placeholders = ", ".join(
            ["?"] * len(metadata)
        )

        cursor = connection.execute(
            f"""
            INSERT INTO music_tracks ({columns})
            VALUES ({placeholders})
            """,
            tuple(metadata.values()),
        )

        connection.commit()

        return self.get_track(cursor.lastrowid)

    def import_folder(self, folder_path, recursive=True):
        """Import supported audio files from a folder."""

        folder = Path(folder_path)

        if not folder.is_dir():
            raise NotADirectoryError(
                f"Music folder not found: {folder}"
            )

        imported = []
        skipped = []

        files = (
            folder.rglob("*")
            if recursive
            else folder.iterdir()
        )

        for path in files:
            if not path.is_file():
                continue

            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            try:
                track = self.add_track(path)
                imported.append(track)
            except (ValueError, OSError) as exc:
                skipped.append({
                    "file_path": str(path),
                    "reason": str(exc),
                })

        return {
            "imported": imported,
            "skipped": skipped,
        }

    def get_track(self, track_id):
        connection = self.database.connect()

        row = connection.execute(
            "SELECT * FROM music_tracks WHERE id = ?",
            (track_id,),
        ).fetchone()

        return dict(row) if row else None

    def get_all_tracks(self):
        connection = self.database.connect()

        rows = connection.execute(
            """
            SELECT * FROM music_tracks
            ORDER BY title COLLATE NOCASE ASC
            """
        ).fetchall()

        return [dict(row) for row in rows]

    def search_tracks(self, query):
        connection = self.database.connect()
        query = (query or "").strip()

        if not query:
            return self.get_all_tracks()

        pattern = f"%{query}%"

        rows = connection.execute(
            """
            SELECT * FROM music_tracks
            WHERE title LIKE ?
               OR artist LIKE ?
               OR album LIKE ?
               OR genre LIKE ?
            ORDER BY title COLLATE NOCASE ASC
            """,
            (pattern, pattern, pattern, pattern),
        ).fetchall()

        return [dict(row) for row in rows]

    def remove_track(self, track_id):
        """Remove a library entry without deleting its audio file."""
        connection = self.database.connect()

        cursor = connection.execute(
            "DELETE FROM music_tracks WHERE id = ?",
            (track_id,),
        )

        connection.commit()

        return cursor.rowcount > 0

    def set_favorite(self, track_id, favorite=True):
        connection = self.database.connect()

        cursor = connection.execute(
            """
            UPDATE music_tracks
            SET is_favorite = ?
            WHERE id = ?
            """,
            (int(favorite), track_id),
        )

        connection.commit()

        return cursor.rowcount > 0

    def get_favorites(self):
        connection = self.database.connect()

        rows = connection.execute(
            """
            SELECT * FROM music_tracks
            WHERE is_favorite = 1
            ORDER BY title COLLATE NOCASE ASC
            """
        ).fetchall()

        return [dict(row) for row in rows]

    def create_playlist(self, name, description=""):
        name = (name or "").strip()

        if not name:
            raise ValueError("Playlist name cannot be empty.")

        now = datetime.now().isoformat(timespec="seconds")
        connection = self.database.connect()

        try:
            cursor = connection.execute(
                """
                INSERT INTO music_playlists (
                    name, description, created_at, updated_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (name, description, now, now),
            )

            connection.commit()

        except sqlite3.IntegrityError as exc:
            connection.rollback()
            raise ValueError(
                "A playlist with this name already exists."
            ) from exc

        return self.get_playlist(cursor.lastrowid)

    def get_playlist(self, playlist_id):
        connection = self.database.connect()

        row = connection.execute(
            "SELECT * FROM music_playlists WHERE id = ?",
            (playlist_id,),
        ).fetchone()

        return dict(row) if row else None

    def get_all_playlists(self):
        connection = self.database.connect()

        rows = connection.execute(
            """
            SELECT p.*,
                COUNT(pt.id) AS track_count
            FROM music_playlists p
            LEFT JOIN music_playlist_tracks pt
                ON p.id = pt.playlist_id
            GROUP BY p.id
            ORDER BY p.name COLLATE NOCASE ASC
            """
        ).fetchall()

        return [dict(row) for row in rows]

    def rename_playlist(self, playlist_id, name):
        name = (name or "").strip()

        if not name:
            raise ValueError("Playlist name cannot be empty.")

        connection = self.database.connect()

        try:
            cursor = connection.execute(
                """
                UPDATE music_playlists
                SET name = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    name,
                    datetime.now().isoformat(timespec="seconds"),
                    playlist_id,
                ),
            )

            connection.commit()

        except sqlite3.IntegrityError as exc:
            connection.rollback()
            raise ValueError(
                "A playlist with this name already exists."
            ) from exc

        return cursor.rowcount > 0

    def delete_playlist(self, playlist_id):
        connection = self.database.connect()

        cursor = connection.execute(
            "DELETE FROM music_playlists WHERE id = ?",
            (playlist_id,),
        )

        connection.commit()

        return cursor.rowcount > 0

    def add_to_playlist(self, playlist_id, track_id):
        connection = self.database.connect()

        playlist = connection.execute(
            "SELECT id FROM music_playlists WHERE id = ?",
            (playlist_id,),
        ).fetchone()

        track = connection.execute(
            "SELECT id FROM music_tracks WHERE id = ?",
            (track_id,),
        ).fetchone()

        if not playlist:
            raise ValueError("Playlist does not exist.")

        if not track:
            raise ValueError("Track does not exist.")

        position = connection.execute(
            """
            SELECT COALESCE(MAX(position), -1) + 1
            FROM music_playlist_tracks
            WHERE playlist_id = ?
            """,
            (playlist_id,),
        ).fetchone()[0]

        try:
            connection.execute(
                """
                INSERT INTO music_playlist_tracks (
                    playlist_id, track_id, position, added_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    playlist_id,
                    track_id,
                    position,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )

            connection.execute(
                """
                UPDATE music_playlists
                SET updated_at = ?
                WHERE id = ?
                """,
                (
                    datetime.now().isoformat(timespec="seconds"),
                    playlist_id,
                ),
            )

            connection.commit()

        except sqlite3.IntegrityError as exc:
            connection.rollback()
            raise ValueError(
                "This song is already in the playlist."
            ) from exc

        return True

    def remove_from_playlist(self, playlist_id, track_id):
        connection = self.database.connect()

        cursor = connection.execute(
            """
            DELETE FROM music_playlist_tracks
            WHERE playlist_id = ? AND track_id = ?
            """,
            (playlist_id, track_id),
        )

        connection.commit()

        return cursor.rowcount > 0

    def get_playlist_tracks(self, playlist_id):
        connection = self.database.connect()

        rows = connection.execute(
            """
            SELECT t.*, pt.position, pt.added_at
            FROM music_playlist_tracks pt
            JOIN music_tracks t ON t.id = pt.track_id
            WHERE pt.playlist_id = ?
            ORDER BY pt.position ASC, pt.id ASC
            """,
            (playlist_id,),
        ).fetchall()

        return [dict(row) for row in rows]
