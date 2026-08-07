# CLAUDE.md — Arbeitsanweisung für Claude Code

Dieses Dokument ist die verbindliche Betriebsanleitung für jede KI-Coding-Session
(Claude Code oder vergleichbar), die an diesem Repository arbeitet. Lies es
**vollständig**, bevor du Code schreibst oder änderst.

## 1. Was dieses Projekt ist

CONTINUUM ist der Software-Prototyp eines kontinuierlich lernenden autonomen
Forschungssystems. Die vollständige technische Begründung steht in
`docs/CONTINUUM_Konzeptpapier.docx` und in verdichteter Form in
`ARCHITECTURE.md`. Kernidee in einem Satz: ein System, das aus echten
Experimentergebnissen lernt, ohne bereits Gelerntes zu verlieren, und das
niemals eine unbelegte Behauptung als Fakt ausgibt.

Dieses Repository befindet sich in **Phase 0** der Roadmap (siehe
`ROADMAP.md`): reiner Software-Aufbau auf simulierten Daten, **keine
Roboter-Hardware, keine echten Laborexperimente**. Alles, was in der
Architektur als „robotische Ausführungsschicht“ beschrieben ist, wird in
Phase 0 durch `src/continuum/data/simulated_materials.py` gemockt.

## 2. Nicht verhandelbare Prinzipien

Diese Regeln gelten für **jede** Änderung an diesem Repository, unabhängig
davon, wie klein die Aufgabe erscheint:

1. **Keine unbelegte Behauptung.** Jede Funktion, die eine Aussage über ein
   Material, eine Hypothese oder ein Modellergebnis erzeugt, muss diese
   Aussage mit einer der drei Herkunftskategorien aus `verification/evidence.py`
   markieren (`EXPERIMENTAL`, `PREDICTED`, `LITERATURE`). Code, der das nicht
   tut, ist nicht mergefähig.
2. **Sicherheits-Gates dürfen nicht umgangen werden**, auch nicht in Tests
   oder Demos. `safety/governance.py` muss für jede simulierte
   „Experimentfreigabe“ durchlaufen werden, auch wenn in Phase 0 nichts
   Physisches passiert. Das Muster muss von Anfang an korrekt sitzen, damit
   es in Phase 1 (echte Hardware) nicht nachgerüstet werden muss.
3. **Alles ist auditierbar.** Jeder Schreibzugriff auf den Speicher, jede
   Konsolidierung, jede Governance-Entscheidung wird geloggt
   (`safety/governance.py::audit_log`). Kein stiller State-Change.
4. **Phasendisziplin.** Baue nichts aus Phase 2/3 (echtes LoRA-Training mit
   GPU, echte Robotik-Anbindung), bevor die Akzeptanzkriterien der
   vorherigen Phase in `TASKS.md` erfüllt und getestet sind. Wenn eine
   Aufgabe danach aussieht, als gehöre sie zu einer späteren Phase, sag das
   explizit statt sie einfach mitzuimplementieren.
5. **Lange Kontextfenster sind kein Gedächtnis.** Verwende niemals rohen
   Prompt-Kontext als Ersatz für die in `memory/` implementierten Speicher.
   Das ist eine der zentralen Erkenntnisse aus dem Konzeptpapier (Quelle [2]
   im Whitepaper) und wird hier bewusst architektonisch erzwungen.

## 3. Wie du arbeitest

1. **Vor jeder neuen Komponente:** lies den zugehörigen Abschnitt in
   `ARCHITECTURE.md`. Die Modulstruktur unter `src/continuum/` folgt exakt
   der Kapitelstruktur des Konzepts (5.1–5.7).
2. **Interface vor Implementierung:** Jedes Modul hat bereits ein Interface
   (Funktions-/Klassensignatur mit Docstring und Typannotationen). Wenn ein
   Docstring `TODO(Phase X): ...` enthält, ist das absichtlich offen für
   dich — implementiere es gemäß der referenzierten Architektur, nicht
   irgendeine plausibel klingende Alternative.
3. **Tests zuerst oder zumindest zeitgleich.** Jedes neue oder geänderte
   Modul braucht einen Test in `tests/`. `pytest` muss grün sein, bevor eine
   Aufgabe als erledigt gilt.
4. **TASKS.md ist die Quelle der Wahrheit für „was als Nächstes“.**
   Arbeite die Liste in Reihenfolge ab, hake erledigte Punkte ab und ergänze
   neue Punkte, wenn du beim Implementieren Lücken findest, statt sie
   stillschweigend zu lösen oder zu ignorieren.
5. **Mocks bleiben austauschbar.** LLM-Aufrufe laufen ausschließlich über
   `llm/client.py::LLMClient` (Interface). Bau nichts, das direkt an einen
   bestimmten Anbieter (OpenAI, Anthropic, …) gekoppelt ist — die
   Mock-Implementierung `MockLLMClient` muss jederzeit ausreichen, damit die
   gesamte Pipeline ohne API-Key lauffähig bleibt.
6. **Sprache:** Docstrings und Kommentare auf Deutsch (konsistent mit dem
   Konzeptpapier), Bezeichner (Funktionen, Variablen, Klassen) auf Englisch
   (Standardkonvention).

## 4. Setup & Befehle

```bash
cd continuum
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest                      # alle Tests
python scripts/run_demo_loop.py   # End-to-End-Demo auf simulierten Daten
```

## 5. Definition of Done pro Aufgabe

Eine Aufgabe aus `TASKS.md` gilt erst als erledigt, wenn:

- [ ] die Implementierung dem Interface/Docstring aus dem jeweiligen Modul entspricht,
- [ ] ein Test existiert und `pytest` grün ist,
- [ ] keine der Regeln aus Abschnitt 2 verletzt wird,
- [ ] `TASKS.md` aktualisiert wurde (Häkchen gesetzt, ggf. Folgeaufgaben ergänzt).

## 6. Wo was steht

| Datei | Zweck |
|---|---|
| `ARCHITECTURE.md` | Verdichtete technische Spezifikation (Quelle der Wahrheit für Design-Entscheidungen) |
| `ROADMAP.md` | Phasenplan mit Go/No-Go-Kriterien |
| `TASKS.md` | Konkreter, abarbeitbarer Aufgaben-Backlog für Phase 0 |
| `docs/CONTINUUM_Konzeptpapier.docx` | Vollständiges Konzeptpapier mit Quellenbelegen |
| `src/continuum/` | Der eigentliche Code, nach Architektur-Kapiteln strukturiert |

Wenn ARCHITECTURE.md und Code je auseinanderlaufen, hat ARCHITECTURE.md
Vorrang — melde den Widerspruch statt ihn stillschweigend im Code zu lösen.
