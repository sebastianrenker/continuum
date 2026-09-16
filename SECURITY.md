# Security model and honest limits

CONTINUUM is a **phase-0 architecture prototype** (see [`README.md`](README.md),
[`ROADMAP.md`](ROADMAP.md)) — not an externally audited production system. All
"experiments" run against a **simulated** objective function, not against real lab
hardware. This document openly describes which protection mechanisms are anchored in
the code, which of them exist in phase 0 only as patterns, and what must mandatorily
happen before any use with real materials.

> The security architecture is deliberately laid out correctly *from the start*, so
> that it does not have to be retrofitted in phase 1 (real hardware) — not because
> anything physical is already at stake in phase 0.

---

## 1. Governance gate and audit log

Every simulated "experiment approval" mandatorily passes through
`src/continuum/safety/governance.py` — including in tests and demos. An approval that
bypasses this gate is, by project rule, not mergeable (see
[`CLAUDE.md`](CLAUDE.md), section 2).

Every write to the store, every consolidation, and every governance decision is logged
via `governance.py::audit_log` — no silent state change. **Honest limit:** the audit
log is a traceability mechanism, not a tamper-protection one. In phase 0 there is no
cryptographic chain and no protection against an attacker with write access to the log
itself.

## 2. Hazardous-material screening — only an example rule set

`src/continuum/safety/hazard_screening.py` contains an **example** rule set to
illustrate the architecture. It is **not** a vetted safety standard and does not cover
real hazardous-material scenarios.

> ⚠️ **Mandatory:** before any use with real materials, this rule set must be reviewed
> and extended by experts (chemistry/lab safety) (see [`TASKS.md`](TASKS.md), D5). Do
> not rely on the shipped rules in any real context.

## 3. Anti-hallucination layer (provenance)

Every statement about a material, a hypothesis, or a model result must be tagged via
`src/continuum/verification/evidence.py` with a provenance category: `EXPERIMENTAL`,
`PREDICTED`, or `LITERATURE`. Code that outputs an unsubstantiated claim as fact is not
mergeable. This is a deliberate architectural lock against emitting hallucinated
"results" — not a substitute for scientific validation of the statements themselves.

## 4. LLM boundary and secrets

- All LLM calls run exclusively through the provider-independent interface
  `src/continuum/llm/client.py::LLMClient`. The default pipeline is fully runnable with
  `MockLLMClient` **without an API key and without network access**.
- If a real LLM provider is deliberately connected, the submitted prompt content leaves
  the machine and is subject to that provider's terms — this is a property of the
  connection, not of the prototype.
- **No** keys, tokens, or credentials belong in commits. Configuration via environment
  variables, not in the repo.

## 5. Known limits (deliberate phase-0 trade-offs)

1. **No real lab hardware.** The robotic execution layer is mocked by
   `src/continuum/data/simulated_materials.py`. Results are simulated, not scientific
   findings.
2. **Hazardous-material rule set is exemplary** (section 2).
3. **Audit log is not tamper-proof** (section 1).
4. **Not externally audited.** Neither code nor architecture has undergone an external
   security or domain review.
5. Real weight-level continual learning (LoRA, consolidation) and hardware connection
   are later phases — laid out as interfaces, not as code (phase discipline, see
   [`ROADMAP.md`](ROADMAP.md)).

## 6. Mandatory before any real deployment

- Domain review and extension of the hazardous-material screening (section 2).
- A tamper-evident, ideally cryptographically chained audit log.
- External security and domain review of the governance and verification logic.
- A real, vetted safety process for the hardware execution layer, before phase 1 even
  begins.

## 7. Reporting vulnerabilities

Please do **not** report security issues publicly as an issue, but privately via GitHub
**Security Advisories** (Repository → Security → "Report a vulnerability") or by email
to the maintainer. Please include a description, the affected commit, reproduction
steps, and impact.
