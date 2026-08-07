"""Datenmodelle des Gedaechtnissystems. Siehe ARCHITECTURE.md, Abschnitt 1."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum


class MemoryKind(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


@dataclass
class MemoryRecord:
    """Ein einzelner Eintrag im MemoryStore, unabhaengig von der Schicht."""

    text: str
    kind: MemoryKind
    source: str = "unknown"
    importance: float = 0.5
    tags: tuple[str, ...] = field(default_factory=tuple)
    embedding: list[float] | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    validated: bool = False  # siehe consolidation.py: erst nach Validierung im Langzeitspeicher


@dataclass
class EpisodicEvent:
    """Ein zeitgestempeltes, konkretes Experimentereignis."""

    description: str
    parameters: dict
    outcome: dict
    timestamp: float = field(default_factory=time.time)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class SemanticFact:
    """Aus mehreren Episoden abstrahiertes Wissen."""

    statement: str
    confidence: float
    supporting_episode_ids: tuple[str, ...]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ProceduralSkill:
    """Ein wiederverwendbares, aufrufbares Laborprotokoll."""

    name: str
    description: str
    callable_ref: str  # voll qualifizierter Python-Pfad, z. B. "continuum.data.protocols.synthesize"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
