# Sicherheitsmodell und ehrliche Grenzen

CONTINUUM ist ein **Phase-0-Architektur-Prototyp** (siehe [`README.md`](README.md),
[`ROADMAP.md`](ROADMAP.md)) — kein extern auditiertes Produktivsystem. Alle
„Experimente" laufen gegen eine **simulierte** Zielfunktion, nicht gegen echte
Laborhardware. Dieses Dokument beschreibt offen, welche Schutzmechanismen im Code
verankert sind, welche davon in Phase 0 nur als Muster existieren, und was vor jeder
Verwendung mit realen Materialien zwingend passieren muss.

> Die Sicherheitsarchitektur ist bewusst *von Anfang an* korrekt angelegt, damit sie
> in Phase 1 (echte Hardware) nicht nachgerüstet werden muss — nicht, weil in Phase 0
> bereits etwas Physisches auf dem Spiel stünde.

---

## 1. Governance-Gate und Audit-Log

Jede simulierte „Experimentfreigabe" läuft verpflichtend durch
`src/continuum/safety/governance.py` — auch in Tests und Demos. Eine Freigabe, die
dieses Gate umgeht, ist per Projektregel nicht mergefähig (siehe
[`CLAUDE.md`](CLAUDE.md), Abschnitt 2).

Jeder Schreibzugriff auf den Speicher, jede Konsolidierung und jede
Governance-Entscheidung wird über `governance.py::audit_log` protokolliert — kein
stiller State-Change. **Ehrliche Grenze:** Das Audit-Log ist ein Nachvollziehbarkeits-,
kein Manipulationsschutz-Mechanismus. In Phase 0 gibt es keine kryptographische
Kette und keinen Schutz gegen einen Angreifer mit Schreibzugriff auf den Log selbst.

## 2. Gefahrstoff-Screening — nur ein Beispiel-Regelwerk

`src/continuum/safety/hazard_screening.py` enthält ein **exemplarisches** Regelwerk
zur Veranschaulichung der Architektur. Es ist **kein** geprüfter Sicherheitsstandard
und deckt reale Gefahrstoffszenarien nicht ab.

> ⚠️ **Zwingend:** Vor jeder Verwendung mit realen Materialien muss dieses Regelwerk
> von Fachleuten (Chemie-/Laborsicherheit) geprüft und erweitert werden (siehe
> [`TASKS.md`](TASKS.md), D5). Verlasse dich in keinem realen Kontext auf die
> mitgelieferten Regeln.

## 3. Anti-Halluzinations-Schicht (Herkunftsnachweis)

Jede Aussage über ein Material, eine Hypothese oder ein Modellergebnis muss über
`src/continuum/verification/evidence.py` mit einer Herkunftskategorie markiert sein:
`EXPERIMENTAL`, `PREDICTED` oder `LITERATURE`. Code, der eine unbelegte Behauptung als
Fakt ausgibt, ist nicht mergefähig. Das ist eine bewusste architektonische Sperre
gegen das Ausgeben halluzinierter „Ergebnisse" — kein Ersatz für wissenschaftliche
Validierung der Aussagen selbst.

## 4. LLM-Grenze und Geheimnisse

- Alle LLM-Aufrufe laufen ausschließlich über die anbieterunabhängige Schnittstelle
  `src/continuum/llm/client.py::LLMClient`. Die Standard-Pipeline ist mit
  `MockLLMClient` **ohne API-Key und ohne Netzwerkzugriff** vollständig lauffähig.
- Wird bewusst ein echter LLM-Anbieter angebunden, verlassen die übermittelten
  Prompt-Inhalte den Rechner und unterliegen den Bedingungen dieses Anbieters — das
  ist eine Eigenschaft der Anbindung, nicht des Prototyps.
- Es gehören **keine** Schlüssel, Tokens oder Zugangsdaten in Commits. Konfiguration
  über Umgebungsvariablen, nicht im Repo.

## 5. Bekannte Grenzen (bewusste Phase-0-Kompromisse)

1. **Keine echte Laborhardware.** Die robotische Ausführungsschicht ist durch
   `src/continuum/data/simulated_materials.py` gemockt. Ergebnisse sind simuliert,
   keine wissenschaftlichen Befunde.
2. **Gefahrstoff-Regelwerk ist exemplarisch** (Abschnitt 2).
3. **Audit-Log ist nicht manipulationssicher** (Abschnitt 1).
4. **Nicht extern auditiert.** Weder Code noch Architektur wurden einer externen
   Sicherheits- oder Fachprüfung unterzogen.
5. Echtes kontinuierliches Gewichts-Lernen (LoRA, Konsolidierung) und
   Hardware-Anbindung sind spätere Phasen — als Interfaces angelegt, nicht als Code
   (Phasendisziplin, siehe [`ROADMAP.md`](ROADMAP.md)).

## 6. Vor einem realen Einsatz zwingend

- Fachliche Prüfung und Erweiterung des Gefahrstoff-Screenings (Abschnitt 2).
- Manipulationssicheres, idealerweise kryptographisch verkettetes Audit-Log.
- Externe Sicherheits- und Fachprüfung der Governance- und Verifikationslogik.
- Ein realer, geprüfter Sicherheitsprozess für die Hardware-Ausführungsschicht,
  bevor Phase 1 überhaupt beginnt.

## 7. Schwachstellen melden

Sicherheitsprobleme bitte **nicht** öffentlich als Issue melden, sondern privat über
GitHub **Security Advisories** (Repository → Security → „Report a vulnerability")
oder per E-Mail an den Maintainer. Bitte Beschreibung, betroffenen Commit,
Reproduktionsschritte und Auswirkung angeben.
