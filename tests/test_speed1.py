from continuum.learning.speed1_context import forget, recall, remember
from continuum.memory.store import MemoryStore


def test_remember_and_recall():
    store = MemoryStore(":memory:")
    remember(store, "Dotierung mit Aluminium erhoeht Leitfaehigkeit")
    results = recall(store, "Aluminium Dotierung", k=1)
    assert len(results) == 1
    assert "Aluminium" in results[0][0].text


def test_forget_removes_record():
    store = MemoryStore(":memory:")
    record = remember(store, "temporaerer Eintrag")
    forget(store, record.id)
    assert store.get(record.id) is None
