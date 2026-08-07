import pytest

from continuum.memory.models import MemoryKind, MemoryRecord
from continuum.memory.store import MemoryStore
from continuum.verification.checker import ClaimChecker, InvalidClaimError
from continuum.verification.evidence import Claim, Evidence


def test_experimental_claim_needs_validated_record():
    store = MemoryStore(":memory:")
    record = MemoryRecord(text="gemessen: 5 mS/cm", kind=MemoryKind.EPISODIC, validated=False)
    store.write(record)
    checker = ClaimChecker(store)

    claim = Claim(text="Material X hat 5 mS/cm", evidence_kind=Evidence.EXPERIMENTAL,
                   confidence=0.95, source_ref=record.id)

    with pytest.raises(InvalidClaimError):
        checker.verify(claim)

    store.mark_validated(record.id)
    result = checker.verify(claim)
    assert result.is_valid


def test_predicted_claim_rejects_overconfidence():
    store = MemoryStore(":memory:")
    checker = ClaimChecker(store)
    claim = Claim(text="Vorhersage", evidence_kind=Evidence.PREDICTED, confidence=0.999, source_ref="run-1")

    with pytest.raises(InvalidClaimError):
        checker.verify(claim)


def test_literature_claim_needs_source():
    with pytest.raises(ValueError):
        Claim(text="laut Literatur", evidence_kind=Evidence.LITERATURE, confidence=0.8, source_ref="")


def test_claim_without_valid_evidence_can_be_checked_without_raising():
    store = MemoryStore(":memory:")
    checker = ClaimChecker(store)
    claim = Claim(text="unbelegt", evidence_kind=Evidence.EXPERIMENTAL, confidence=0.9, source_ref="does-not-exist")

    result = checker.verify(claim, raise_on_invalid=False)
    assert not result.is_valid
