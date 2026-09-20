"""Procedural memory: a registry of callable lab protocols.

See ARCHITECTURE.md, section 1. Skills are registered here as Python callables
with metadata, not only as a text description — the difference
between "the system knows that it could do X" and "the system can actually
execute X" (cf. the concept paper, memory literature source [2]).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from continuum.memory.models import ProceduralSkill


@dataclass
class RegisteredSkill:
    skill: ProceduralSkill
    fn: Callable[..., object]


class ProceduralMemory:
    def __init__(self) -> None:
        self._skills: dict[str, RegisteredSkill] = {}

    def register(self, skill: ProceduralSkill, fn: Callable[..., object]) -> None:
        self._skills[skill.name] = RegisteredSkill(skill=skill, fn=fn)

    def get(self, name: str) -> RegisteredSkill | None:
        return self._skills.get(name)

    def invoke(self, name: str, *args, **kwargs) -> object:
        entry = self.get(name)
        if entry is None:
            raise KeyError(f"No registered skill '{name}' in procedural memory.")
        return entry.fn(*args, **kwargs)

    def list_skills(self) -> list[ProceduralSkill]:
        return [entry.skill for entry in self._skills.values()]
