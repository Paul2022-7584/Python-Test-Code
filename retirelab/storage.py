"""SQLite persistence, without an ORM or external database service."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3

from .models import RetirementScenario


class ScenarioStore:
    def __init__(self, path: str | Path = "retirelab.sqlite3") -> None:
        self.path = str(path)
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS scenarios (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL,
                     payload TEXT NOT NULL,
                     created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                   )"""
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def save(self, scenario: RetirementScenario) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO scenarios (name, payload) VALUES (?, ?)",
                (scenario.name, json.dumps(scenario.to_dict(), allow_nan=False)),
            )
            return int(cursor.lastrowid)

    def list(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, name, created_at FROM scenarios ORDER BY id DESC"
            ).fetchall()
            return [dict(row) for row in rows]

    def get(self, scenario_id: int) -> RetirementScenario | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM scenarios WHERE id = ?", (scenario_id,)
            ).fetchone()
        return RetirementScenario.from_dict(json.loads(row["payload"])) if row else None

    def delete(self, scenario_id: int) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM scenarios WHERE id = ?", (scenario_id,))
            return cursor.rowcount > 0
