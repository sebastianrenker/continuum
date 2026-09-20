"""Data models of the memory system. See ARCHITECTURE.md, section 1."""

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
    """A single entry in the MemoryStore, independent of the layer."""

    text: str
    kind: MemoryKind
    source: str = "unknown"
    importance: float = 0.5
    tags: tuple[str, ...] = field(default_factory=tuple)
    embedding: list[float] | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    validated: bool = False  # see consolidation.py: only after validation in long-term storage


@dataclass
class EpisodicEvent:
    """A timestamped, concrete experiment event."""

    description: str
    parameters: dict
    outcome: dict
    timestamp: float = field(default_factory=time.time)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class SemanticFact:
    """Knowledge abstracted from several episodes."""

    statement: str
    confidence: float
    supporting_episode_ids: tuple[str, ...]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ProceduralSkill:
    """A reusable, callable lab protocol."""

    name: str
    description: str
    callable_ref: str  # a fully qualified Python path, e.g. "continuum.data.protocols.synthesize"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
