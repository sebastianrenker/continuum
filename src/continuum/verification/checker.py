"""ClaimChecker: setzt das Anti-Halluzinations-Prinzip technisch durch.

Siehe ARCHITECTURE.md, Abschnitt 6. Claims ohne gueltige Herkunfts-
kennzeichnung UND ohne passenden Beleg im MemoryStore werden hart
abgelehnt (Exception), nicht nur mit einer Warnung versehen — siehe
CLAUDE.md, Prinzip 1.
"""

from __future__ import annotations

from dataclasses import dataclass

from continuum.memory.store import MemoryStore
from continuum.verification.evidence import Claim, Evidence


class InvalidClaimError(Exception):
    """Wird geworfen, wenn ein Claim keinen gueltigen Beleg hat."""


@dataclass
class VerificationResult:
    claim: Claim
    is_valid: bool
    reason: str


class ClaimChecker:
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def verify(self, claim: Claim, *, raise_on_invalid: bool = True) -> VerificationResult:
        result = self._check(claim)
        if raise_on_invalid and not result.is_valid:
            raise InvalidClaimError(
                f"Claim abgelehnt ({result.reason}): '{claim.text}'"
            )
        return result

    def _check(self, claim: Claim) -> VerificationResult:
        if claim.evidence_kind == Evidence.EXPERIMENTAL:
            record = self._store.get(claim.source_ref)
            if record is None:
                return VerificationResult(claim, False, "EXPERIMENTAL-Claim ohne auffindbaren Beleg-Record")
            if not record.validated:
                return VerificationResult(
                    claim, False, "EXPERIMENTAL-Claim verweist auf unvalidierten Record (siehe consolidation.py)"
                )
            return VerificationResult(claim, True, "belegt durch validierten Experiment-Record")

        if claim.evidence_kind == Evidence.PREDICTED:
            if claim.confidence >= 0.999:
                return VerificationResult(
                    claim, False, "PREDICTED-Claim mit Konfidenz ~1.0 ist verdaechtig ueberzuversichtlich"
                )
            return VerificationResult(claim, True, "Modellvorhersage mit kalibrierter Unsicherheit")

        if claim.evidence_kind == Evidence.LITERATURE:
            if not claim.source_ref.strip():
                return VerificationResult(claim, False, "LITERATURE-Claim ohne Quellenangabe")
            return VerificationResult(claim, True, "Literaturzitat mit Quellenangabe")

        return VerificationResult(claim, False, "unbekannte Evidence-Kategorie")
