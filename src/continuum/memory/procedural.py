"""Prozedurales Gedaechtnis: Registry aufrufbarer Laborprotokolle.

Siehe ARCHITECTURE.md, Abschnitt 1. Skills sind hier als Python-Callables
mit Metadaten registriert, nicht nur als Textbeschreibung — der Unterschied
zwischen "das System weiss, dass es X tun koennte" und "das System kann X
tatsaechlich ausfuehren" (vgl. Konzeptpapier, Memory-Literatur-Quelle [2]).
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
            raise KeyError(f"Kein registriertes Skill '{name}' im prozeduralen Gedaechtnis.")
        return entry.fn(*args, **kwargs)

    def list_skills(self) -> list[ProceduralSkill]:
        return [entry.skill for entry in self._skills.values()]
