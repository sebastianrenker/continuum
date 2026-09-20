"""Hazardous-material screening before every (simulated) synthesis.

See ARCHITECTURE.md, section 7, and the concept paper chapter 5.7. Uses a
deliberately small EXAMPLE rule set (`data/hazard_denylist.json`) — see the
warning in README.md and TASKS.md D5. This is NOT a complete
safety rule set and must not be used as such before
experts have reviewed and extended it.
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
    """Checks a proposed material composition against the denylist.

    `composition` expects at least the keys that
    `data.simulated_materials.SimulatedLab.run_experiment` also accepts,
    plus optionally `elements: list[str]` and `compound_name: str`.
    """
    denylist = _load_denylist()
    reasons: list[str] = []

    elements = composition.get("elements", [])
    for element in elements:
        if element in denylist["denied_elements"]:
            reasons.append(f"element '{element}' is on the denylist")

    compound_name = composition.get("compound_name", "")
    for denied in denylist["denied_compounds"]:
        if denied.lower() in compound_name.lower():
            reasons.append(f"compound '{compound_name}' matches the blocked pattern '{denied}'")

    dopant_fraction = composition.get("dopant_fraction")
    max_fraction = denylist.get("max_dopant_fraction_without_review")
    if dopant_fraction is not None and max_fraction is not None and dopant_fraction > max_fraction:
        reasons.append(
            f"dopant_fraction={dopant_fraction} exceeds the threshold "
            f"{max_fraction} without a manual review"
        )

    return HazardAssessment(composition=composition, is_blocked=bool(reasons), reasons=reasons)
