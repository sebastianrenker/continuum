from continuum.memory.models import MemoryKind, MemoryRecord
from continuum.memory.store import MemoryStore


def test_write_and_get():
    store = MemoryStore(":memory:")
    record = MemoryRecord(text="Sulfid-Elektrolyt mit hoher Leitfaehigkeit", kind=MemoryKind.EPISODIC)
    store.write(record)
    fetched = store.get(record.id)
    assert fetched is not None
    assert fetched.text == record.text
    assert fetched.embedding is not None


def test_search_ranks_relevant_higher():
    store = MemoryStore(":memory:")
    relevant = MemoryRecord(text="Ionenleitfaehigkeit steigt mit Dotierung", kind=MemoryKind.SEMANTIC, validated=True)
    irrelevant = MemoryRecord(text="Kaffeemaschine im Labor kaputt", kind=MemoryKind.SEMANTIC, validated=True)
    store.write(relevant)
    store.write(irrelevant)

    results = store.search("Ionenleitfaehigkeit Dotierung", k=2)
    assert results[0][0].id == relevant.id


def test_count_and_delete():
    store = MemoryStore(":memory:")
    record = MemoryRecord(text="temp", kind=MemoryKind.WORKING)
    store.write(record)
    assert store.count() == 1
    store.delete(record.id)
    assert store.count() == 0


def test_validated_only_filter():
    store = MemoryStore(":memory:")
    unvalidated = MemoryRecord(text="frisch", kind=MemoryKind.EPISODIC, validated=False)
    validated = MemoryRecord(text="frisch validiert", kind=MemoryKind.EPISODIC, validated=True)
    store.write(unvalidated)
    store.write(validated)

    results = store.search("frisch", k=10, validated_only=True)
    ids = [r.id for r, _ in results]
    assert validated.id in ids
    assert unvalidated.id not in ids
