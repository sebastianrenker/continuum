# CONTINUUM

![CI](https://github.com/sebastianrenker/continuum/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Phase%200%20prototype-orange)

Software-Prototyp (Phase 0) eines kontinuierlich lernenden autonomen
Forschungssystems, instanziiert am Beispiel autonomer Materialforschung.
Vollständige technische Begründung:
[`docs/CONTINUUM_Konzeptpapier.docx`](docs/CONTINUUM_Konzeptpapier.docx).

> **Ehrlicher Status:** Dies ist ein Konzept- und Architektur-Prototyp, kein
> validiertes wissenschaftliches Ergebnis und kein Produktivsystem. Alle
> "Experimente" laufen in Phase 0 gegen eine simulierte Zielfunktion, nicht
> gegen echte Laborhardware (siehe `ROADMAP.md`). Ziel dieses Repos ist es,
> zu zeigen, *wie* eine Architektur für echtes kontinuierliches Lernen in
> einem KI-Forschungssystem aussehen könnte — nicht, ein fertiges Produkt
> zu sein.

> **Für Claude Code / andere KI-Coding-Agenten:** Lies zuerst `CLAUDE.md`.
> Dort stehen die verbindlichen Arbeitsregeln für dieses Repository.

## Was hier funktioniert (ohne API-Key, ohne GPU, ohne Hardware)

- Ein vierschichtiges Gedächtnissystem mit SQLite-Backend und
  Zwei-Puffer-Konsolidierung
- Ein Bayes'sches Weltmodell (Gaussian Process) mit
  Unsicherheitsschätzung und Vorschlagsfunktion für nächste Experimente
- Ein simuliertes Labor als Platzhalter für echte Robotik
- Eine Verifikationsschicht, die keine unbelegten Behauptungen durchlässt
- Ein Gefahrstoff-Screening und ein Governance-Gate mit Audit-Log
- Eine Multi-Agenten-Hypothesen-Pipeline (mit Mock-LLM lauffähig)
- Ein vierschichtiger Evaluierungs-Stack

## Was hier bewusst noch nicht funktioniert

Echtes kontinuierliches Gewichts-Lernen (LoRA-Adapter, Konsolidierung) und
die Anbindung an echte Laborhardware sind spätere Phasen (siehe
`ROADMAP.md`) und in diesem Repository als dokumentierte Interfaces
angelegt, nicht als funktionierender Code — absichtlich, siehe
`CLAUDE.md`, Prinzip „Phasendisziplin“.

## Schnellstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

pytest                              # Testsuite
python scripts/run_demo_loop.py     # kompletter Zyklus auf simulierten Daten
```

## Projektstruktur

```
src/continuum/
├── llm/            # Anbieterunabhängige LLM-Schnittstelle + Mock
├── memory/         # Working/Episodic/Semantic/Procedural Memory
├── learning/        # Drei-Geschwindigkeiten-Lernsystem
├── hypothesis/      # Multi-Agenten-Hypothesen-Tournament
├── worldmodel/       # Bayes'sches Surrogatmodell
├── verification/     # Anti-Halluzinations-Schicht
├── safety/           # Gefahrstoff-Screening & Governance
├── eval/             # Vier-Ebenen-Evaluierung
└── data/              # Simuliertes Labor (Phase-0-Platzhalter für Hardware)
```

Siehe `ARCHITECTURE.md` für die vollständige Spezifikation je Modul und
`TASKS.md` für den aktuellen Aufgaben-Backlog.

## RENKER-Plattform

Continuum ist die **LEARN**-Säule der Renker-Plattform — Infrastruktur für
vertrauenswürdige, autonome KI-Systeme. Gesamtarchitektur und die anderen
Säulen: [RENKER_PLATFORM.md](RENKER_PLATFORM.md).

```text
RENKER — ACT (Rencora) · LEARN (Continuum) · SECURE (RenkerVault)
                         gemeinsames Fundament: renker-core
```

| Säule | Rolle | Repo |
| --- | --- | --- |
| Rencora | ACT | https://github.com/sebastianrenker/rencora |
| RenkerVault | SECURE | https://github.com/sebastianrenker/renkervault |
| renker-core-authz | öffentlicher Authorization-Core | https://github.com/sebastianrenker/renker-core-authz |

## Lizenz / Status

Forschungs-/Konzeptprototyp, kein Produktivsystem. Sicherheitsrelevante
Komponenten (`safety/hazard_screening.py`) enthalten nur ein Beispiel-
Regelwerk und müssen vor jeder Verwendung mit realen Materialien von
Fachleuten geprüft und erweitert werden (siehe `TASKS.md`, D5).
