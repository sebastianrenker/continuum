# Mitwirken an CONTINUUM

Danke für dein Interesse. CONTINUUM ist ein Phase-0-Architektur-Prototyp mit
bewusst strenger Disziplin — Beiträge werden an einem hohen Maßstab gemessen.
Lies vor dem ersten Commit die verbindlichen Arbeitsregeln in
[`CLAUDE.md`](CLAUDE.md) und die Design-Wahrheit in [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Grundregeln (nicht verhandelbar)

- **Keine unbelegte Behauptung.** Jede Aussage über Material/Hypothese/Modell wird
  über `verification/evidence.py` mit `EXPERIMENTAL`/`PREDICTED`/`LITERATURE`
  markiert. Ohne Herkunftsnachweis nicht mergefähig.
- **Sicherheits-Gates werden nie umgangen** — auch nicht in Tests oder Demos. Jede
  „Experimentfreigabe" läuft durch `safety/governance.py`.
- **Alles ist auditierbar.** Kein stiller State-Change; Speicher-, Konsolidierungs-
  und Governance-Schritte werden geloggt.
- **Phasendisziplin.** Nichts aus Phase 2/3 (echtes LoRA-Training, Robotik-Anbindung)
  bauen, bevor die Akzeptanzkriterien der Vorphase in [`TASKS.md`](TASKS.md) erfüllt
  sind. Sieht eine Aufgabe nach späterer Phase aus: explizit sagen, nicht mitimplementieren.
- **Mocks bleiben austauschbar.** LLM-Zugriff nur über `llm/client.py::LLMClient`;
  `MockLLMClient` muss die Pipeline jederzeit ohne API-Key lauffähig halten.
- **Keine Geheimnisse** in Commits.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Python ≥ 3.10. Phase-2-Abhängigkeiten (torch/transformers/peft) sind bewusst
optional (`.[phase2]`) und für Phase-0-Arbeit nicht nötig.

## Lokale Prüfungen (müssen grün sein)

```bash
ruff format --check .
ruff check .
pytest
python scripts/run_demo_loop.py     # End-to-End-Demo auf simulierten Daten
```

CI führt bei jedem Pull Request `ruff check`, `pytest` und den Demo-Smoke-Test
(`run_demo_loop.py --rounds 5`) aus; `ruff format --check` ist lokale Konvention.

## Sicherheitsrelevante Änderungen

Alles, was `safety/governance.py`, `safety/hazard_screening.py` oder
`verification/` berührt, muss:

1. einen Test enthalten, der die Grenze gezielt herausfordert (Umgehungsversuch), und
2. jeden bestehenden Sicherheitstest grün lassen.

Schwachstellen bitte **privat** melden — siehe [`SECURITY.md`](SECURITY.md), nicht
als öffentliches Issue/PR.

## Definition of Done

Eine Aufgabe aus [`TASKS.md`](TASKS.md) gilt erst als erledigt, wenn Implementierung
dem Interface/Docstring entspricht, ein Test existiert und `pytest` grün ist, keine
Grundregel verletzt wird und `TASKS.md` aktualisiert ist.

## Stil

- Bezeichner (Funktionen, Variablen, Klassen) auf **Englisch**; Docstrings und
  Kommentare auf **Deutsch** (konsistent mit dem Konzeptpapier).
- Explizite Typannotationen, `ruff` (Zeilenlänge 100, Ziel `py310`).
- Interface vor Implementierung: `TODO(Phase X): ...` in Docstrings ist bewusst offen
  und gemäß der referenzierten Architektur umzusetzen.
