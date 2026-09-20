"""Speed 2 — capability building (LoRA adapters, daily-weekly).

See ARCHITECTURE.md, section 2, and the concept paper chapter 5.3.

STATUS: deliberately NOT implemented in phase 0 — see CLAUDE.md,
principle 4 (phase discipline), and TASKS.md, block F2. This module defines
the interface a later phase-2 implementation must fulfill,
with the concretely intended techniques:

- LoRA adapters (~0.1-1% of the parameter count) via PEFT/transformers
- Contextual Experience Replay (CER): training on summarized,
  real experience sequences from memory.episodic
- Orthogonal Subspace Learning (O-LoRA): new adapters for subdomains
  are trained orthogonally to existing adapter gradient directions,
  to prevent mutual overwriting

Before this module is implemented, the go/no-go criteria from
ROADMAP.md for phase 0 must be met AND a GPU-capable training setup
must be present (see pyproject.toml, the optional dependency "phase2").
"""

from __future__ import annotations

from continuum.memory.store import MemoryStore


class Speed2LoRALearner:
    """The interface for the weekly adapter training.

    TODO(Phase 2): implement with `peft.LoraConfig` + the O-LoRA
    orthogonality constraint. The training data comes from
    `memory.episodic.EpisodicMemory.recall_similar` (the CER pattern: only
    validated, summarized experience sequences, no raw replay
    of whole raw data for privacy reasons — see the concept paper,
    the trade-off table in chapter 5.3).
    """

    def __init__(self, base_model_ref: str, memory_store: MemoryStore) -> None:
        self._base_model_ref = base_model_ref
        self._memory_store = memory_store

    def train_adapter(self, domain_tag: str) -> None:
        raise NotImplementedError(
            "Speed2LoRALearner.train_adapter is intended for phase 2. "
            "See ARCHITECTURE.md section 2 and TASKS.md block F2. "
            "Do not implement in phase 0 (CLAUDE.md, phase discipline)."
        )
