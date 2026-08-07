"""Gefahrstoff-Screening vor jeder (simulierten) Synthese.

Siehe ARCHITECTURE.md, Abschnitt 7, und Konzeptpapier Kapitel 5.7. Nutzt ein
bewusst kleines BEISPIEL-Regelwerk (`data/hazard_denylist.json`) — siehe
Warnung in README.md und TASKS.md D5. Dies ist KEIN vollstaendiges
Sicherheitsregelwerk und darf nicht als solches verwendet werden, bevor
Fachleute es geprueft und erweitert haben.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib import resources


@dataclass
class HazardAssessment:
    composition: dict
    is_blocked: bool
    reasons: list[str] = field(default_factory=list)


def _load_denylist() -> dict:
    with resources.files("continuum.data").joinpath("hazard_denylist.json").open("r", encoding="utf-8") as fh:
        return json.load(fh)


def screen(composition: dict) -> HazardAssessment:
    """Prueft eine vorgeschlagene Materialzusammensetzung gegen die Denylist.

    `composition` erwartet mindestens die Keys, die auch
    `data.simulated_materials.SimulatedLab.run_experiment` entgegennimmt,
    plus optional `elements: list[str]` und `compound_name: str`.
    """
    denylist = _load_denylist()
    reasons: list[str] = []

    elements = composition.get("elements", [])
    for element in elements:
        if element in denylist["denied_elements"]:
            reasons.append(f"Element '{element}' steht auf der Denylist")

    compound_name = composition.get("compound_name", "")
    for denied in denylist["denied_compounds"]:
        if denied.lower() in compound_name.lower():
            reasons.append(f"Verbindung '{compound_name}' entspricht gesperrtem Muster '{denied}'")

    dopant_fraction = composition.get("dopant_fraction")
    max_fraction = denylist.get("max_dopant_fraction_without_review")
    if dopant_fraction is not None and max_fraction is not None and dopant_fraction > max_fraction:
        reasons.append(
            f"dopant_fraction={dopant_fraction} ueberschreitet Schwelle "
            f"{max_fraction} ohne manuelle Pruefung"
        )

    return HazardAssessment(composition=composition, is_blocked=bool(reasons), reasons=reasons)
