
import wave

import pytest

from mochi.database.connection import Database
from mochi.database.schema import initialise_database
from mochi.services.music_service import MusicService


@pytest.fixture
def music_service(tmp_path):
    db = Database()
    db.database_path = tmp_path / "test_music.db"

    initialise_database(db)

    service = MusicService(db)

    yield service

    db.close()


@pytest.fixture
def sample_wav(tmp_path):
    path = tmp_path / "sample_song.wav"

    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(44100)
        audio.writeframes(b"\x00\x00" * 44100)

    return path


def test_import_audio_file(music_service, sample_wav):
    track = music_service.add_track(sample_wav)

    assert track["title"] == "sample_song"
    assert track["artist"] == "Unknown Artist"
    assert track["album"] == "Unknown Album"
    assert track["duration_seconds"] == pytest.approx(1.0)
    assert track["is_favorite"] == 0


def test_import_same_file_twice_does_not_duplicate(
    music_service, sample_wav
):
    first = music_service.add_track(sample_wav)
    second = music_service.add_track(sample_wav)

    assert first["id"] == second["id"]
    assert len(music_service.get_all_tracks()) == 1


def test_reject_missing_file(music_service, tmp_path):
    with pytest.raises(FileNotFoundError):
        music_service.add_track(tmp_path / "missing.wav")


def test_reject_unsupported_file(music_service, tmp_path):
    path = tmp_path / "document.txt"
    path.write_text("Not an audio file.")

    with pytest.raises(ValueError):
        music_service.add_track(path)


def test_import_folder(music_service, sample_wav, tmp_path):
    result = music_service.import_folder(tmp_path)

    assert len(result["imported"]) == 1
    assert result["skipped"] == []


def test_search_tracks(music_service, sample_wav):
    track = music_service.add_track(sample_wav)

    results = music_service.search_tracks("sample_song")

    assert len(results) == 1
    assert results[0]["id"] == track["id"]


def test_empty_search_returns_all_tracks(
    music_service, sample_wav
):
    music_service.add_track(sample_wav)

    assert len(music_service.search_tracks("  ")) == 1


def test_favorites(music_service, sample_wav):
    track = music_service.add_track(sample_wav)

    assert music_service.set_favorite(track["id"])
    assert len(music_service.get_favorites()) == 1

    assert music_service.set_favorite(
        track["id"], False
    )
    assert music_service.get_favorites() == []


def test_remove_track_does_not_delete_audio_file(
    music_service, sample_wav
):
    track = music_service.add_track(sample_wav)

    assert music_service.remove_track(track["id"])
    assert music_service.get_track(track["id"]) is None
    assert sample_wav.exists()


def test_create_playlist(music_service):
    playlist = music_service.create_playlist(
        "Study Music", "Songs for focused work."
    )

    assert playlist["name"] == "Study Music"
    assert playlist["description"] == "Songs for focused work."


def test_playlist_rejects_empty_name(music_service):
    with pytest.raises(ValueError):
        music_service.create_playlist("   ")


def test_playlist_rejects_duplicate_name(music_service):
    music_service.create_playlist("Favorites")

    with pytest.raises(ValueError):
        music_service.create_playlist("Favorites")


def test_add_and_remove_playlist_tracks(
    music_service, sample_wav
):
    track = music_service.add_track(sample_wav)
    playlist = music_service.create_playlist("My Playlist")

    assert music_service.add_to_playlist(
        playlist["id"], track["id"]
    )

    tracks = music_service.get_playlist_tracks(
        playlist["id"]
    )

    assert len(tracks) == 1
    assert tracks[0]["id"] == track["id"]

    assert music_service.remove_from_playlist(
        playlist["id"], track["id"]
    )

    assert music_service.get_playlist_tracks(
        playlist["id"]
    ) == []


def test_playlist_rejects_duplicate_track(
    music_service, sample_wav
):
    track = music_service.add_track(sample_wav)
    playlist = music_service.create_playlist("Study")

    music_service.add_to_playlist(
        playlist["id"], track["id"]
    )

    with pytest.raises(ValueError):
        music_service.add_to_playlist(
            playlist["id"], track["id"]
        )


def test_delete_playlist(music_service):
    playlist = music_service.create_playlist("Temporary")

    assert music_service.delete_playlist(playlist["id"])
    assert music_service.get_playlist(playlist["id"]) is None
