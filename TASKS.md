# TASKS.md — Phase-0-Backlog

Konkrete, abarbeitbare Aufgaben in empfohlener Reihenfolge. Dieses
Repository liefert für jede Aufgabe bereits ein Grundgerüst (Interfaces,
teils funktionierender Code, teils `TODO`-Markierungen) — siehe Spalte
„Status im Repo“. Häkchen selbst setzen, wenn Definition-of-Done
(`CLAUDE.md` Abschnitt 5) erfüllt ist.

## Block A — Fundament

- [x] **A1. Projekt-Setup.** `pyproject.toml`, `src`-Layout, `pytest`-Konfiguration.
      *Status: fertig.*
- [x] **A2. LLM-Abstraktion.** `llm/client.py` mit `LLMClient`-Protokoll und
      `MockLLMClient`. *Status: fertig, `AnthropicClient` ist TODO(Phase 1).*
- [x] **A3. Embedding-Funktion.** `memory/embeddings.py` mit deterministischem
      Offline-Hashing-Embedder. *Status: fertig.*

## Block B — Gedächtnissystem

- [x] **B1. Datenmodelle.** `memory/models.py`. *Status: fertig.*
- [x] **B2. `MemoryStore` (SQLite + Cosinus-Suche).** `memory/store.py`.
      *Status: fertig, Test in `tests/test_memory_store.py`.*
- [x] **B3. Working/Episodic/Semantic/Procedural-Wrapper.**
      `memory/working.py`, `episodic.py`, `semantic.py`, `procedural.py`.
      *Status: fertig.*
- [x] **B4. Zwei-Puffer-Konsolidierung.** `memory/consolidation.py`.
      *Status: fertig, Test in `tests/test_consolidation.py`.*
- [ ] **B5. Skalierungstest.** Lade 10.000 synthetische Records, miss
      `search()`-Latenz. Akzeptanzkriterium: < 200 ms p95 auf einer
      Standard-Entwicklungsmaschine (siehe `ARCHITECTURE.md` Abschnitt 1).
      *Status: TODO — noch kein Lasttest vorhanden, nur Funktionstest.*

## Block C — Weltmodell & simuliertes Labor

- [x] **C1. `SimulatedLab`.** `data/simulated_materials.py` mit fester,
      verrauschter Zielfunktion. *Status: fertig.*
- [x] **C2. `SurrogateModel` (Gaussian Process).** `worldmodel/surrogate.py`
      mit `fit`, `predict` (inkl. Unsicherheit), `suggest_next`
      (Expected Improvement). *Status: fertig, Test in
      `tests/test_worldmodel.py`.*
- [ ] **C3. Kalibrierungs-Report über echten Demo-Lauf.** Nach 20+ Runden
      des Demo-Loops prüfen: sinkt der mittlere Vorhersagefehler des
      Surrogatmodells? Ergebnis in `eval/harness.py::calibration_curve`
      einspeisen. *Status: TODO — Funktion existiert, aber noch nicht
      systematisch über viele Runden ausgewertet.*

## Block D — Verifikation & Sicherheit

- [x] **D1. `Claim`/`Evidence`-Datenmodell.** `verification/evidence.py`.
      *Status: fertig.*
- [x] **D2. `ClaimChecker`.** `verification/checker.py`, hartes Scheitern bei
      fehlender Herkunftskennzeichnung. *Status: fertig, Test in
      `tests/test_verification.py`.*
- [x] **D3. Gefahrstoff-Screening (Beispiel-Denylist).**
      `safety/hazard_screening.py` + `data/hazard_denylist.json`.
      *Status: fertig, bewusst kleines Beispielset — siehe Warnhinweis
      unten.*
- [x] **D4. `GovernanceGate` + Audit-Log.** `safety/governance.py`.
      *Status: fertig, Test in `tests/test_governance.py`.*
- [ ] **D5. Denylist durch Fachleute erweitern lassen**, bevor dieses
      Repository auch nur an simulierten Daten mit realistischeren
      Zusammensetzungen getestet wird, die über das Demo-Beispielset
      hinausgehen. *Status: bewusst offen — keine KI-Aufgabe, sondern
      menschliche Fachprüfung. Nicht von Claude Code allein abzuhaken.*

## Block E — Hypothesen-Engine

- [x] **E1. Vier Agenten-Interfaces.** `hypothesis/agents.py`
      (`GenerationAgent`, `ReflectionAgent`, `RankingAgent`,
      `EvolutionAgent`), lauffähig mit `MockLLMClient`. *Status: fertig.*
- [x] **E2. `run_tournament()`-Orchestrierung.** `hypothesis/tournament.py`.
      *Status: fertig, Test in `tests/test_hypothesis.py`.*
- [ ] **E3. Prompt-Feinschliff für echten `LLMClient`.** Die aktuellen
      Prompts sind für `MockLLMClient` ausreichend, aber noch nicht für
      Qualität mit einem echten Sprachmodell optimiert. *Status: TODO(Phase 1)
      — erst relevant, sobald `AnthropicClient` implementiert ist.*

## Block F — Lernsystem

- [x] **F1. Geschwindigkeit 1 (Sofortlernen).** `learning/speed1_context.py`
      — Tool-Call-Funktionen `remember()`, `recall()`, `forget()` auf Basis
      von `MemoryStore`. *Status: fertig, Test in `tests/test_speed1.py`.*
- [ ] **F2. Geschwindigkeit 2 (LoRA-Adapter).** `learning/speed2_lora.py`
      ist ein dokumentiertes Interface mit `NotImplementedError`.
      *Status: bewusst TODO(Phase 2) — siehe `ARCHITECTURE.md` Abschnitt 2.
      Nicht in Phase 0 implementieren, siehe Phasendisziplin in `CLAUDE.md`.*
- [ ] **F3. Geschwindigkeit 3 (Konsolidierung).**
      `learning/speed3_consolidation.py`, ebenfalls Interface.
      *Status: bewusst TODO(Phase 3).*

## Block G — Evaluierung

- [x] **G1. Vier-Ebenen-Metriken + domänenspezifische Metriken.**
      `eval/metrics.py`. *Status: fertig, Test in `tests/test_eval_metrics.py`.*
- [x] **G2. `run_full_eval()`-Harness.** `eval/harness.py`. *Status: fertig.*
- [ ] **G3. Report-Historie über mehrere Demo-Läufe** persistieren
      (`eval_history.jsonl`), damit Trends (Kalibrierung, Vergessensrate)
      über Zeit sichtbar werden statt nur Momentaufnahmen. *Status: TODO.*

## Block H — Integration & Qualität

- [x] **H1. `scripts/run_demo_loop.py`** — kompletter 11-Schritte-Zyklus
      end-to-end. *Status: fertig.*
- [x] **H2. Testsuite grün.** `pytest` läuft ohne Fehler. *Status: fertig
      zum Zeitpunkt der Repo-Erstellung — nach jeder Änderung erneut prüfen.*
- [x] **H3. CI-Workflow** (GitHub Actions: `ruff` + `pytest` + Demo-Smoke-Test
      bei jedem Push/PR). *Status: fertig, siehe `.github/workflows/ci.yml`.*
- [ ] **H4. Typprüfung** mit `mypy` oder `pyright` in CI ergänzen.
      *Status: TODO.*

---

## Nächster konkreter Schritt für eine neue Claude-Code-Session

Wenn du dieses Repo zum ersten Mal öffnest: führe `pytest` aus, lies den
Output von `python scripts/run_demo_loop.py`, und beginne dann mit **B5**
oder **C3** (offene Punkte ohne Abhängigkeit von späteren Phasen). Vermeide
**F2/F3** — die sind absichtlich für später reserviert.
