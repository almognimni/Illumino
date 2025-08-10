import sqlite3
import threading
import os
from typing import List, Dict, Optional

class ProfileManager:
    """Manage user profiles and per-song highscores.

    Schema:
        profiles(id INTEGER PK, name TEXT UNIQUE)
        highscores(id INTEGER PK, profile_id INTEGER, song_name TEXT, high_score INTEGER, UNIQUE(profile_id, song_name))
    """

    def __init__(self, db_path: str = "profiles.db", songs_dir: str = "Songs"):
        self.db_path = db_path
        self.songs_dir = songs_dir
        self._lock = threading.Lock()
        self._init_db()

    # --------------- Internal helpers ---------------
    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS highscores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    song_name TEXT NOT NULL,
                    high_score INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(profile_id, song_name),
                    FOREIGN KEY(profile_id) REFERENCES profiles(id) ON DELETE CASCADE
                )
                """
            )
            conn.commit()

    def _list_song_files(self) -> List[str]:
        try:
            files = os.listdir(self.songs_dir)
        except FileNotFoundError:
            return []
        return [f for f in files if f.lower().endswith('.mid') and '_#' not in f]

    # --------------- Profile operations ---------------
    def create_profile(self, name: str) -> int:
        name = name.strip()
        if not name:
            raise ValueError("Profile name cannot be empty")
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT OR IGNORE INTO profiles(name) VALUES(?)", (name,))
            conn.commit()
            cur.execute("SELECT id FROM profiles WHERE name=?", (name,))
            row = cur.fetchone()
            profile_id = row[0]
        # Ensure highscores rows exist
        self.ensure_song_entries(profile_id)
        return profile_id

    def get_profiles(self) -> List[Dict]:
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM profiles ORDER BY name COLLATE NOCASE ASC")
            rows = cur.fetchall()
        return [{"id": r[0], "name": r[1]} for r in rows]

    def get_profile_id(self, name: str) -> Optional[int]:
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM profiles WHERE name=?", (name,))
            row = cur.fetchone()
            return row[0] if row else None

    def get_or_create_profile(self, name: str) -> int:
        pid = self.get_profile_id(name)
        if pid is not None:
            return pid
        return self.create_profile(name)

    # --------------- Highscore operations ---------------
    def ensure_song_entries(self, profile_id: int):
        songs = self._list_song_files()
        if not songs:
            return
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            for song in songs:
                cur.execute(
                    "INSERT OR IGNORE INTO highscores(profile_id, song_name, high_score) VALUES(?,?,0)",
                    (profile_id, song)
                )
            conn.commit()

    def get_highscores(self, profile_id: int) -> Dict[str, int]:
        # Populate missing songs with 0
        self.ensure_song_entries(profile_id)
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT song_name, high_score FROM highscores WHERE profile_id=?", (profile_id,))
            rows = cur.fetchall()
        return {r[0]: r[1] for r in rows}

    def update_highscore(self, profile_id: int, song_name: str, new_score: int) -> bool:
        if new_score < 0:
            return False
        song_name = song_name.strip()
        if not song_name:
            return False
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            # Make sure row exists
            cur.execute(
                "INSERT OR IGNORE INTO highscores(profile_id, song_name, high_score) VALUES(?,?,0)",
                (profile_id, song_name)
            )
            # Only update if higher
            cur.execute(
                "UPDATE highscores SET high_score=? WHERE profile_id=? AND song_name=? AND high_score < ?",
                (new_score, profile_id, song_name, new_score)
            )
            changed = cur.rowcount > 0
            conn.commit()
        return changed

    def delete_profile(self, profile_id: int):
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM profiles WHERE id=?", (profile_id,))
            conn.commit()
