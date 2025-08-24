import sqlite3
import threading
import os
import time
import json
from typing import List, Dict, Optional, Sequence, Tuple

class ProfileManager:
    """Manage user profiles and per-song highscores.

    Schema:
        profiles(id INTEGER PK, name TEXT UNIQUE)
        highscores(id INTEGER PK, profile_id INTEGER, song_name TEXT, high_score INTEGER, UNIQUE(profile_id, song_name))
    """

    def __init__(self, db_path: str = "profiles.db", songs_dir: str = "Songs"):
        # Resolve relative DB path into project 'data' directory so file is visible & persistent
        if not os.path.isabs(db_path):
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            data_dir = os.path.join(project_root, 'data')
            try:
                os.makedirs(data_dir, exist_ok=True)
            except OSError:
                # Fallback: keep relative path if directory cannot be created
                data_dir = os.path.abspath(project_root)
            db_path = os.path.join(data_dir, db_path)
        self.db_path = db_path
        self.songs_dir = songs_dir
        self._lock = threading.Lock()
        self._init_db()

    # --------------- Internal helpers ---------------
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
        except Exception:
            pass
        return conn

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
            # Stores per-play timing delay lists for last N plays (trimmed in code)
            # delays_json is a JSON array of [note_time, delay] pairs sorted by note_time
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS session_delays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    song_name TEXT NOT NULL,
                    play_time INTEGER NOT NULL,
                    delays_json TEXT NOT NULL,
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

    # --------------- Session delays (last 10 plays) ---------------
    def store_session_delays(self, profile_id: int, song_name: str, delays: Sequence[Tuple[float, float]], keep: int = 10):
        """Persist a single play's combined timing delays.

        delays: iterable of (note_time, delay) sorted by note_time
        keep: number of most recent plays to retain per (profile_id, song_name)
        """
        if profile_id is None or not song_name:
            return
        # Serialize as list of [time, delay] for JSON consistency
        try:
            serialized = json.dumps([[float(t), float(d)] for t, d in delays])
        except Exception:
            # Fallback: don't store if serialization fails
            return
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO session_delays(profile_id, song_name, play_time, delays_json) VALUES (?,?,?,?)",
                (int(profile_id), song_name, int(time.time()), serialized)
            )
            # Delete older rows beyond 'keep' most recent
            cur.execute(
                """
                DELETE FROM session_delays WHERE id IN (
                    SELECT id FROM session_delays
                    WHERE profile_id = ? AND song_name = ?
                    ORDER BY play_time DESC
                    LIMIT -1 OFFSET ?
                )
                """,
                (int(profile_id), song_name, keep)
            )
            conn.commit()

    def get_recent_session_delays(self, profile_id: int, song_name: str, limit: int = 10) -> List[List[Tuple[float, float]]]:
        if profile_id is None or not song_name:
            return []
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT delays_json FROM session_delays WHERE profile_id=? AND song_name=? ORDER BY play_time DESC LIMIT ?",
                (int(profile_id), song_name, int(limit))
            )
            rows = cur.fetchall()
        sessions: List[List[Tuple[float, float]]] = []
        for (delays_json,) in rows:
            try:
                arr = json.loads(delays_json)
                # Ensure structure list of [time, delay]
                cleaned = []
                for pair in arr:
                    if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                        cleaned.append( (float(pair[0]), float(pair[1])) )
                sessions.append(cleaned)
            except Exception:
                continue
        return sessions

    def get_average_delays(self, profile_id: int, song_name: str, limit: int = 10) -> List[Tuple[float, float]]:
        """Compute average (time, delay) for each note index across the most recent sessions.

        Note times are averaged only among sessions containing that index; same for delays.
        Returns list of (avg_time, avg_delay) sorted by index.
        """
        sessions = self.get_recent_session_delays(profile_id, song_name, limit=limit)
        if not sessions:
            return []
        max_len = max(len(s) for s in sessions)
        averages: List[Tuple[float, float]] = []
        for i in range(max_len):
            time_sum = 0.0
            delay_sum = 0.0
            count = 0
            for sess in sessions:
                if i < len(sess):
                    t, d = sess[i]
                    time_sum += t
                    delay_sum += d
                    count += 1
            if count > 0:
                averages.append( (time_sum / count, delay_sum / count) )
        return averages
