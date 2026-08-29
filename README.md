# CONTINUUM

![CI](https://github.com/sebastianrenker/continuum/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Phase%200%20prototype-orange)

> Architektur-Prototyp eines kontinuierlich lernenden autonomen Forschungssystems — ehrlich als Phase 0 gekennzeichnet.

## Überblick

Software-Prototyp (Phase 0) eines kontinuierlich lernenden autonomen
Forschungssystems, instanziiert am Beispiel autonomer Materialforschung.
Vollständige technische Begründung:
[`docs/CONTINUUM_Konzeptpapier.docx`](docs/CONTINUUM_Konzeptpapier.docx).

> **Ehrlicher Status:** Dies ist ein Konzept- und Architektur-Prototyp, kein
> validiertes wissenschaftliches Ergebnis und kein Produktivsystem. Alle
> "Experimente" laufen in Phase 0 gegen eine simulierte Zielfunktion, nicht
> gegen echte Laborhardware (siehe `ROADMAP.md`). Ziel ist zu zeigen, *wie* eine
> Architektur für echtes kontinuierliches Lernen aussehen könnte — nicht, ein
> fertiges Produkt zu sein.

> **Für Claude Code / andere KI-Coding-Agenten:** Lies zuerst `CLAUDE.md` — dort
> stehen die verbindlichen Arbeitsregeln für dieses Repository.

## Features

**Was funktioniert (ohne API-Key, ohne GPU, ohne Hardware):**

- Vierschichtiges Gedächtnissystem (SQLite-Backend, Zwei-Puffer-Konsolidierung)
- Bayes'sches Weltmodell (Gaussian Process) mit Unsicherheitsschätzung und
  Vorschlagsfunktion für nächste Experimente
- Simuliertes Labor als Platzhalter für echte Robotik
- Verifikationsschicht, die keine unbelegten Behauptungen durchlässt
- Gefahrstoff-Screening und Governance-Gate mit Audit-Log
- Multi-Agenten-Hypothesen-Pipeline (mit Mock-LLM lauffähig)
- Vierschichtiger Evaluierungs-Stack

**Was bewusst noch nicht funktioniert:** echtes kontinuierliches Gewichts-Lernen
(LoRA-Adapter, Konsolidierung) und die Anbindung an echte Laborhardware sind
spätere Phasen (siehe `ROADMAP.md`) — als dokumentierte Interfaces angelegt,
nicht als Code (Prinzip „Phasendisziplin", siehe `CLAUDE.md`).

## Architektur

```
src/continuum/
├── llm/            # Anbieterunabhängige LLM-Schnittstelle + Mock
├── memory/         # Working/Episodic/Semantic/Procedural Memory
├── learning/       # Drei-Geschwindigkeiten-Lernsystem
├── hypothesis/     # Multi-Agenten-Hypothesen-Tournament
├── worldmodel/     # Bayes'sches Surrogatmodell
├── verification/   # Anti-Halluzinations-Schicht
├── safety/         # Gefahrstoff-Screening & Governance
├── eval/           # Vier-Ebenen-Evaluierung
└── data/           # Simuliertes Labor (Phase-0-Platzhalter für Hardware)
```

Vollständige Spezifikation je Modul in `ARCHITECTURE.md`, aktueller Backlog in `TASKS.md`.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

python scripts/run_demo_loop.py     # kompletter Zyklus auf simulierten Daten
```

## Tests

```bash
pytest
```

## Lizenz

MIT — siehe [`LICENSE`](LICENSE). © 2026 Sebastian Renker.

Forschungs-/Konzeptprototyp, kein Produktivsystem. Sicherheitsrelevante
Komponenten (`safety/hazard_screening.py`) enthalten nur ein Beispiel-Regelwerk
und müssen vor jeder Verwendung mit realen Materialien von Fachleuten geprüft und
erweitert werden (siehe `TASKS.md`, D5).
