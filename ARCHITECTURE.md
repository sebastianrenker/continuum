# ARCHITECTURE.md — CONTINUUM technische Spezifikation (Engineering-Fassung)

Verdichtete, code-nahe Fassung des Konzeptpapiers (`docs/CONTINUUM_Konzeptpapier.docx`).
Kapitelnummern entsprechen dort den Kapiteln 4–7. Jeder Abschnitt hier nennt
explizit das zugehörige Python-Modul.

## 0. Geschlossener Regelkreis (Referenz für alle Module)

```
1  Literatur-/Gedächtnis-Retrieval      → memory.semantic, memory.episodic
2  Hypothesengenerierung (Tournament)    → hypothesis.tournament
3  Neuheits-/Sicherheitsprüfung          → verification.checker, safety.hazard_screening
4  Menschliche Freigabe (Schwellenwert)  → safety.governance
5  Experimentplanung (Bayes-Optimierung) → worldmodel.surrogate
6  Robotische Ausführung [Phase 0: MOCK] → data.simulated_materials
7  Sensorik/Charakterisierung [MOCK]     → data.simulated_materials
8  Abgleich Vorhersage/Ergebnis          → worldmodel.surrogate, eval.metrics
9  Sofort-Update (Geschwindigkeit 1)     → learning.speed1_context
10 Wöchentliches Adapter-Training (Geschw. 2) → learning.speed2_lora
11 Quartalskonsolidierung (Geschw. 3)    → learning.speed3_consolidation
   → zurück zu Schritt 1
```

`scripts/run_demo_loop.py` implementiert genau diese elf Schritte end-to-end
auf simulierten Daten (Schritt 6/7 gemockt, alle anderen echt).

## 1. Gedächtnissystem (`memory/`)

Vier Schichten, ein gemeinsamer SQLite-Store (`memory/store.py`) als
Persistenzschicht (austauschbar gegen eine echte Vektor-DB in späteren
Phasen — die Schnittstelle `MemoryStore` darf sich dabei nicht ändern).

- **`memory/models.py`** — Datenklassen: `MemoryRecord` (id, text, embedding,
  timestamp, kind, importance, source, tags), `EpisodicEvent`,
  `SemanticFact`, `ProceduralSkill`.
- **`memory/store.py`** — `MemoryStore`: CRUD + `search(query, k)` via
  Cosinus-Ähnlichkeit über Embeddings (Embedding-Funktion ist injizierbar,
  Default: deterministischer Hashing-Embedder für Offline-Betrieb ohne
  API-Key, siehe `memory/embeddings.py`).
- **`memory/working.py`** — Kontext-Fenster-Simulation für die aktuell
  laufende Aufgabe; kapazitätsbegrenzt (LRU).
- **`memory/episodic.py`** — Schreiben/Abrufen konkreter Experimentereignisse.
- **`memory/semantic.py`** — Abstraktion: aggregiert mehrere `EpisodicEvent`
  zu einem `SemanticFact`, wenn ein Muster über einer Konfidenzschwelle
  liegt (regelbasiert in Phase 0, LLM-gestützt ab Phase 2).
- **`memory/procedural.py`** — Registry aufrufbarer Laborprotokolle
  (Python-Callables mit Metadaten), nicht nur Textbeschreibungen.
- **`memory/consolidation.py`** — Zwei-Puffer-Modell: `HotBuffer` (neue,
  unvalidierte Records) → Validierung (Dubletten-Check, Mindestbelege) →
  `promote_to_long_term()`. Keine Aufnahme ins Langzeitgedächtnis ohne
  Validierung.

**Akzeptanzkriterium Phase 0:** `MemoryStore` unterstützt mind. 10.000
Records mit Retrieval-Latenz < 200 ms auf einer lokalen Maschine (kein
verteiltes System nötig).

## 2. Lernsystem — Drei Geschwindigkeiten (`learning/`)

| Modul | Geschwindigkeit | Mechanismus | Phase |
|---|---|---|---|
| `speed1_context.py` | Sekunden–Minuten | Tool-Call-basiertes Schreiben/Lesen im Kern-Gedächtnis (Letta-Stil), kein Gradienten-Update | **0 — jetzt implementieren** |
| `speed2_lora.py` | Täglich–wöchentlich | LoRA-Adapter (PEFT) + Contextual Experience Replay aus `memory.episodic`, O-LoRA-Orthogonalität zwischen Teildomänen | 2 — Interface jetzt, echtes Training später |
| `speed3_consolidation.py` | Quartalsweise | Distillation der Adapter ins Kernmodell, EWC-Regularisierung (Fisher-Information) gegen katastrophales Vergessen | 3 — Interface jetzt, echte Konsolidierung später |

`speed1_context.py` ist die einzige Lernkomponente, die in Phase 0
vollständig funktionsfähig sein muss — sie braucht kein Training, nur den
Memory-Store. `speed2_lora.py` und `speed3_consolidation.py` sind bewusst
als klar dokumentierte Interfaces mit `NotImplementedError` angelegt; die
Docstrings verweisen auf die exakten Techniken (EWC, O-LoRA, CER, Titans),
die in einer späteren Phase eingesetzt werden.

## 3. Hypothesen-Engine (`hypothesis/`)

Multi-Agenten-Turnier nach dem AI-Co-Scientist-Muster:

- `GenerationAgent.propose(context) -> list[Hypothesis]`
- `ReflectionAgent.critique(hypothesis) -> Critique`
- `RankingAgent.rank(hypotheses) -> list[RankedHypothesis]`
- `EvolutionAgent.refine(top_k) -> list[Hypothesis]`

Alle vier Agenten nehmen einen `LLMClient` (siehe `llm/client.py`) im
Konstruktor entgegen. In Phase 0 läuft die gesamte Pipeline mit
`MockLLMClient`, damit `scripts/run_demo_loop.py` ohne API-Key durchläuft.
`tournament.py::run_tournament()` orchestriert die vier Agenten über
konfigurierbar viele Runden.

## 4. Weltmodell (`worldmodel/surrogate.py`)

Kein allgemeines physikalisches Weltmodell (siehe Konzeptpapier Kap. 5.1 —
bewusst *nicht* das ungelöste IntPhys-Problem, sondern eine eng gefasste,
tractable Vorhersageaufgabe). `SurrogateModel`:

- `fit(X, y)` — Gaussian-Process-Regression (scikit-learn) über
  Syntheseparameter → Materialeigenschaft.
- `predict(X) -> (mean, std)` — liefert **immer** eine
  Unsicherheitsschätzung, nie nur einen Punktwert.
- `suggest_next(bounds, n) -> X_next` — Bayes'sche Optimierung
  (Expected-Improvement-Akquisitionsfunktion) für den nächsten
  Experimentvorschlag.

## 5. Robotik-/Sensorik-Mock (`data/simulated_materials.py`)

Ersetzt Kapitel 5.5 in Phase 0. `SimulatedLab.run_experiment(params) ->
ExperimentResult` wertet eine feste, aber verrauschte Zielfunktion aus
(deterministisch mit Seed, aber mit realistischem Messrauschen), damit das
Weltmodell etwas Echtes zu lernen hat, ohne dass Hardware nötig ist. Diese
Klasse ist so geschnitten, dass sie 1:1 durch eine echte Laboranbindung
ersetzt werden kann (`run_experiment` bleibt die Schnittstelle).

## 6. Verifikations-/Anti-Halluzinations-Schicht (`verification/`)

- `evidence.py` — `Evidence` (Enum: `EXPERIMENTAL`, `PREDICTED`,
  `LITERATURE`), `Claim` (text, evidence_kind, confidence, source_ref).
- `checker.py` — `ClaimChecker.verify(claim) -> VerificationResult`: prüft,
  ob ein `Claim` eine gültige Herkunftskennzeichnung *und* einen dazu
  passenden Beleg im `MemoryStore`/Evidence-Graph hat. Claims ohne gültige
  Kennzeichnung werden hart abgelehnt (`raises InvalidClaimError`), nicht
  nur mit einer Warnung versehen — das setzt Prinzip 1 aus `CLAUDE.md`
  technisch durch.

## 7. Sicherheits-/Governance-Schicht (`safety/`)

- `hazard_screening.py` — `screen(composition) -> HazardAssessment`:
  regelbasierter Abgleich gegen eine Denylist gefährlicher Elemente/
  Verbindungen (`data/hazard_denylist.json`, in Phase 0 ein bewusst kleines
  Beispielset, **kein** vollständiges Sicherheitsregelwerk — vor Phase 1
  von Fachleuten zu erweitern).
- `governance.py` — `GovernanceGate.request_approval(experiment) ->
  ApprovalDecision`: erzwingt in Phase 0 immer manuelle/simulierte
  Freigabe für Experimente oberhalb eines Kostenschwellenwerts;
  `audit_log(event)` schreibt jedes Ereignis (Speicher-Schreibvorgang,
  Konsolidierung, Freigabe-Entscheidung) als JSON-Zeile nach
  `audit.log`.

## 8. Evaluierung (`eval/metrics.py`, `eval/harness.py`)

Vier-Ebenen-Stack aus dem Konzeptpapier (Kap. 6), als konkrete Funktionen:

```python
task_effectiveness(records) -> TaskEffectivenessReport   # Ebene 1
memory_quality(store, gold_queries) -> MemoryQualityReport # Ebene 2
efficiency(run_log) -> EfficiencyReport                    # Ebene 3
governance_compliance(audit_log_path) -> GovernanceReport   # Ebene 4
calibration_curve(predictions, outcomes) -> CalibrationReport  # domänenspezifisch
forgetting_rate(pre_scores, post_scores) -> float              # domänenspezifisch
```

`eval/harness.py::run_full_eval()` ruft alle sechs Funktionen auf und
schreibt einen zusammenfassenden Report (JSON + Klartext) — das ist die
Grundlage für die Go/No-Go-Entscheidung am Ende jeder Roadmap-Phase.

## 9. LLM-Abstraktion (`llm/client.py`)

```python
class LLMClient(Protocol):
    def complete(self, prompt: str, **kwargs) -> str: ...
    def embed(self, text: str) -> list[float]: ...

class MockLLMClient:  # deterministisch, kein Netzwerk, für Tests/Demo
    ...

class AnthropicClient:  # TODO(Phase 1): echte Anbindung
    ...
```

Jede Komponente, die LLM-Fähigkeiten braucht, bekommt einen `LLMClient` per
Dependency Injection — niemals direkt instanziiert. Das hält die gesamte
Pipeline testbar und anbieterunabhängig.
