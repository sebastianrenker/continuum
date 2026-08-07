# ROADMAP.md

Phasenplan aus dem Konzeptpapier (Kapitel 8), mit Go/No-Go-Kriterien. Dieses
Repository deckt **Phase 0** ab.

## Phase 0 — Proof of Concept (Monate 1–3, reine Software)

**Ziel:** Gedächtnissystem + Geschwindigkeit-1-Lernen + Weltmodell +
Sicherheits-/Verifikationsschicht + Evaluierungs-Harness, alles lauffähig
auf simulierten Materialdaten. Keine Hardware, kein GPU-Training nötig.

**Go/No-Go-Kriterium für Phase 1:**
- [ ] `eval.harness.run_full_eval()` läuft fehlerfrei durch und liefert
      plausible (nicht notwendigerweise perfekte) Werte auf allen sechs Metriken.
- [ ] `scripts/run_demo_loop.py` durchläuft den vollständigen 11-Schritte-Zyklus
      (Schritt 6/7 gemockt) mindestens 20 Mal ohne Absturz und mit sinkendem
      Vorhersagefehler des Weltmodells über die Zeit.
- [ ] Kein Claim ohne gültige Herkunftskennzeichnung passiert `ClaimChecker`
      (siehe Tests in `tests/test_verification.py`).
- [ ] Alle Governance-Entscheidungen sind im Audit-Log nachvollziehbar.

## Phase 1 — Laborintegration (Monate 4–9)

Anbindung an ein echtes Self-Driving-Lab-Partnerlabor (z. B. über eine
Robotik-API), ein eng begrenzter Materialtyp. `data/simulated_materials.py`
wird durch eine echte Implementierung von `run_experiment()` ersetzt, ohne
dass sich die Schnittstelle ändert. **Nicht Teil dieses Repositories** —
eigenständiges Nachfolgeprojekt mit Hardware-Partner.

## Phase 2 — Aktives Lernen scharf schalten (Monate 10–18)

`learning/speed2_lora.py` wird von Interface zu echter Implementierung
(PEFT/LoRA-Training, O-LoRA-Orthogonalität, Contextual Experience Replay
aus echten Experimentdaten). Voraussetzung: Phase-0-Metriken stabil,
Phase-1-Datenfluss etabliert.

## Phase 3 — Konsolidierung & Validierung (Monate 19–30)

`learning/speed3_consolidation.py` wird scharf geschaltet (EWC-basierte
Distillation). Externe, unabhängige Prüfung der
Katastrophales-Vergessen-Rate und der Kalibrierungskurve.

## Phase 4 — Domänentransfer (ab Monat 30)

Test der Architekturhypothese: Übertragung des domänen-agnostischen Kerns
(`memory/`, `learning/`, `verification/`, `hypothesis/`) auf eine zweite
Domäne durch Austausch von `data/simulated_materials.py` und
`safety/hazard_screening.py` gegen domänenspezifische Äquivalente (siehe
Konzeptpapier Kapitel 7, Generalisierungstabelle).

---

**Prinzip für jede Phase:** Ein Scheitern an den Go/No-Go-Kriterien ist ein
valides Ergebnis. Nicht mehr Kapital/Aufwand in die nächste Phase stecken,
bevor die aktuelle Phase ihre Kriterien erfüllt — siehe `CLAUDE.md`,
Prinzip 4 (Phasendisziplin).
