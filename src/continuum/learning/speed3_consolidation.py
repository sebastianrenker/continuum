"""Speed 3 — consolidation (distillation + EWC, quarterly).

See ARCHITECTURE.md, section 2, and the concept paper chapter 5.3 + 9.

STATUS: deliberately NOT implemented in phase 0 — see CLAUDE.md,
principle 4, and TASKS.md, block F3. The intended technique:

- Elastic Weight Consolidation (EWC): a Fisher information matrix to
  identify critical parameters, a quadratic penalty against
  large changes to them (empirically: forgetting rate ~12.6% -> ~6.85%,
  see the concept paper source [3] — NOT a complete solution, see
  risk chapter 9 of the concept paper)
- A Titans-like "surprise" gate: information is preferentially committed
  when it deviates strongly from previous model predictions

A prerequisite for the implementation: several completed
speed-2 training cycles (phase 2) AND a reference task set to measure
the forgetting rate (see eval.metrics.forgetting_rate).
"""

from __future__ import annotations


class Speed3Consolidator:
    """The interface for the quarterly core-model consolidation."""

    def __init__(self, base_model_ref: str) -> None:
        self._base_model_ref = base_model_ref

    def consolidate(self, adapter_refs: list[str]) -> None:
        raise NotImplementedError(
            "Speed3Consolidator.consolidate is intended for phase 3. "
            "See ARCHITECTURE.md section 2 and TASKS.md block F3. "
            "Do not implement in phase 0 (CLAUDE.md, phase discipline)."
        )

    def rollback(self, checkpoint_id: str) -> None:
        """Must ALWAYS be available from phase 3 — see the concept paper
        chapter 5.7 ("rollback capability") and CLAUDE.md, principle 2/3."""
        raise NotImplementedError(
            "Speed3Consolidator.rollback is intended for phase 3."
        )
