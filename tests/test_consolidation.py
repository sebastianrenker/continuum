from continuum.memory.consolidation import Consolidator
from continuum.memory.models import MemoryKind, MemoryRecord
from continuum.memory.store import MemoryStore


def test_promotes_high_importance_record():
    store = MemoryStore(":memory:")
    record = MemoryRecord(text="wichtiger Fund", kind=MemoryKind.EPISODIC, importance=0.9, validated=False)
    store.write(record)

    report = Consolidator(store).run_consolidation_pass()

    assert record.id in report.promoted
    assert store.get(record.id).validated is True


def test_rejects_low_importance_record():
    store = MemoryStore(":memory:")
    record = MemoryRecord(text="belangloses Detail", kind=MemoryKind.EPISODIC, importance=0.05, validated=False)
    store.write(record)

    report = Consolidator(store).run_consolidation_pass()

    assert record.id in report.rejected_low_importance
    assert store.get(record.id).validated is False


def test_rejects_near_duplicate():
    store = MemoryStore(":memory:")
    original = MemoryRecord(
        text="Ionenleitfaehigkeit von Material X betraegt 5 mS/cm",
        kind=MemoryKind.EPISODIC,
        importance=0.8,
        validated=True,
    )
    store.write(original)

    duplicate = MemoryRecord(
        text="Ionenleitfaehigkeit von Material X betraegt 5 mS/cm",
        kind=MemoryKind.EPISODIC,
        importance=0.8,
        validated=False,
    )
    store.write(duplicate)

    report = Consolidator(store).run_consolidation_pass()

    assert duplicate.id in report.rejected_duplicates
