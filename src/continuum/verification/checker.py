"""ClaimChecker: technically enforces the anti-hallucination principle.

See ARCHITECTURE.md, section 6. Claims without a valid provenance
tag AND without a matching piece of evidence in the MemoryStore are hard-
rejected (an exception), not merely flagged with a warning — see
CLAUDE.md, principle 1.
"""

from __future__ import annotations

from dataclasses import dataclass

from continuum.memory.store import MemoryStore
from continuum.verification.evidence import Claim, Evidence


class InvalidClaimError(Exception):
    """Raised when a claim has no valid evidence."""


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
                f"Claim rejected ({result.reason}): '{claim.text}'"
            )
        return result

    def _check(self, claim: Claim) -> VerificationResult:
        if claim.evidence_kind == Evidence.EXPERIMENTAL:
            record = self._store.get(claim.source_ref)
            if record is None:
                return VerificationResult(claim, False, "EXPERIMENTAL claim without a findable evidence record")
            if not record.validated:
                return VerificationResult(
                    claim, False, "EXPERIMENTAL claim references an unvalidated record (see consolidation.py)"
                )
            return VerificationResult(claim, True, "substantiated by a validated experiment record")

        if claim.evidence_kind == Evidence.PREDICTED:
            if claim.confidence >= 0.999:
                return VerificationResult(
                    claim, False, "PREDICTED claim with confidence ~1.0 is suspiciously overconfident"
                )
            return VerificationResult(claim, True, "a model prediction with calibrated uncertainty")

        if claim.evidence_kind == Evidence.LITERATURE:
            if not claim.source_ref.strip():
                return VerificationResult(claim, False, "LITERATURE claim without a source reference")
            return VerificationResult(claim, True, "a literature citation with a source reference")

        return VerificationResult(claim, False, "unknown evidence category")
