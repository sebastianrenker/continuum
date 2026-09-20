"""Provenance tagging for every statement of the system.

See ARCHITECTURE.md, section 6, and the concept paper chapter 5.6:
"no unsubstantiated claim". Every statement carries exactly one of the three
categories in `Evidence`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Evidence(str, Enum):
    EXPERIMENTAL = "experimental"  # a direct measurement, with a reference to reproducibility
    PREDICTED = "predicted"        # a model prediction WITH calibrated uncertainty
    LITERATURE = "literature"      # a citation with a source reference


@dataclass
class Claim:
    """A single, verifiable statement of the system."""

    text: str
    evidence_kind: Evidence
    confidence: float  # in [0, 1]; for EXPERIMENTAL usually close to 1.0
    source_ref: str  # a record ID in the MemoryStore, a citation key, or a model run ID

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be in [0, 1], was {self.confidence}")
        if not self.source_ref:
            raise ValueError("source_ref must not be empty — every statement needs evidence.")
