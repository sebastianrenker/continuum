"""SQLite-basierter MemoryStore mit Cosinus-Aehnlichkeitssuche.

Siehe ARCHITECTURE.md, Abschnitt 1. Diese Klasse ist die gemeinsame
Persistenzschicht fuer alle vier Gedaechtnisebenen (working/episodic/
semantic/procedural) — die duennen Wrapper in working.py/episodic.py/
semantic.py/procedural.py rufen ausschliesslich `MemoryStore`-Methoden auf.

Design-Entscheidung Phase 0: SQLite statt echter Vektor-DB, weil das
Akzeptanzkriterium (10.000 Records, < 200ms Suche) damit ohne zusaetzliche
Infrastruktur erreichbar ist. Ersatz durch eine echte Vektor-DB (z. B.
Chroma/Qdrant) in einer spaeteren Phase aendert diese Schnittstelle nicht.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from continuum.memory.embeddings import EmbedFn, cosine_similarity, default_embedder
from continuum.memory.models import MemoryKind, MemoryRecord

_SCHEMA = """
CREATE TABLE IF NOT EXISTS memory_records (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    kind TEXT NOT NULL,
    source TEXT NOT NULL,
    importance REAL NOT NULL,
    tags TEXT NOT NULL,
    embedding TEXT NOT NULL,
    timestamp REAL NOT NULL,
    validated INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_kind ON memory_records(kind);
CREATE INDEX IF NOT EXISTS idx_validated ON memory_records(validated);
"""


class MemoryStore:
    """CRUD + semantische Suche ueber alle Gedaechtnis-Records.

    Nutzung:
        store = MemoryStore(":memory:")   # oder ein Dateipfad fuer Persistenz
        store.write(record)
        hits = store.search("Ionenleitfaehigkeit", k=5)
    """

    def __init__(self, path: str | Path = ":memory:", embed_fn: EmbedFn | None = None) -> None:
        self._conn = sqlite3.connect(str(path))
        self._conn.executescript(_SCHEMA)
        self._conn.commit()
        self._embed_fn = embed_fn or default_embedder()

    def write(self, record: MemoryRecord) -> MemoryRecord:
        if record.embedding is None:
            record.embedding = self._embed_fn(record.text)
        self._conn.execute(
            "INSERT OR REPLACE INTO memory_records "
            "(id, text, kind, source, importance, tags, embedding, timestamp, validated) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                record.id,
                record.text,
                record.kind.value,
                record.source,
                record.importance,
                json.dumps(list(record.tags)),
                json.dumps(record.embedding),
                record.timestamp,
                int(record.validated),
            ),
        )
        self._conn.commit()
        return record

    def get(self, record_id: str) -> MemoryRecord | None:
        row = self._conn.execute(
            "SELECT * FROM memory_records WHERE id = ?", (record_id,)
        ).fetchone()
        return _row_to_record(row) if row else None

    def delete(self, record_id: str) -> None:
        self._conn.execute("DELETE FROM memory_records WHERE id = ?", (record_id,))
        self._conn.commit()

    def count(self, kind: MemoryKind | None = None, validated_only: bool = False) -> int:
        query = "SELECT COUNT(*) FROM memory_records WHERE 1=1"
        params: list = []
        if kind is not None:
            query += " AND kind = ?"
            params.append(kind.value)
        if validated_only:
            query += " AND validated = 1"
        return self._conn.execute(query, params).fetchone()[0]

    def search(
        self,
        query: str,
        k: int = 5,
        kind: MemoryKind | None = None,
        validated_only: bool = False,
    ) -> list[tuple[MemoryRecord, float]]:
        """Cosinus-Aehnlichkeitssuche. Gibt (Record, Score) absteigend sortiert zurueck.

        Phase-0-Implementierung: Brute-Force ueber alle passenden Records.
        Ausreichend fuer das Akzeptanzkriterium aus ARCHITECTURE.md
        (10.000 Records, < 200ms) — bei deutlich groesserem Datenvolumen
        waere ein approximativer Nearest-Neighbor-Index (z. B. HNSW) noetig.
        """
        query_vec = self._embed_fn(query)
        sql = "SELECT * FROM memory_records WHERE 1=1"
        params: list = []
        if kind is not None:
            sql += " AND kind = ?"
            params.append(kind.value)
        if validated_only:
            sql += " AND validated = 1"
        rows = self._conn.execute(sql, params).fetchall()
        scored = [(_row_to_record(row), 0.0) for row in rows]
        scored = [
            (rec, cosine_similarity(query_vec, rec.embedding or []))
            for rec, _ in scored
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:k]

    def mark_validated(self, record_id: str) -> None:
        self._conn.execute(
            "UPDATE memory_records SET validated = 1 WHERE id = ?", (record_id,)
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


def _row_to_record(row: tuple) -> MemoryRecord:
    (id_, text, kind, source, importance, tags, embedding, timestamp, validated) = row
    return MemoryRecord(
        id=id_,
        text=text,
        kind=MemoryKind(kind),
        source=source,
        importance=importance,
        tags=tuple(json.loads(tags)),
        embedding=json.loads(embedding),
        timestamp=timestamp,
        validated=bool(validated),
    )
