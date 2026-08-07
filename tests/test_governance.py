import tempfile
from pathlib import Path

from continuum.safety.governance import GovernanceGate
from continuum.safety.hazard_screening import screen


def test_auto_approves_below_threshold():
    with tempfile.TemporaryDirectory() as tmp:
        gate = GovernanceGate(audit_log_path=Path(tmp) / "audit.log", cost_threshold=10.0)
        decision = gate.request_approval("exp-1", estimated_cost=5.0, hazard_blocked=False)
        assert decision.approved
        assert decision.auto_approved


def test_blocks_hazardous_regardless_of_override():
    with tempfile.TemporaryDirectory() as tmp:
        gate = GovernanceGate(audit_log_path=Path(tmp) / "audit.log", cost_threshold=10.0)
        decision = gate.request_approval("exp-2", estimated_cost=1.0, hazard_blocked=True, human_override=True)
        assert not decision.approved


def test_requires_override_above_threshold():
    with tempfile.TemporaryDirectory() as tmp:
        gate = GovernanceGate(audit_log_path=Path(tmp) / "audit.log", cost_threshold=10.0)
        denied = gate.request_approval("exp-3", estimated_cost=50.0, hazard_blocked=False)
        assert not denied.approved

        approved = gate.request_approval("exp-4", estimated_cost=50.0, hazard_blocked=False, human_override=True)
        assert approved.approved


def test_audit_log_is_written():
    with tempfile.TemporaryDirectory() as tmp:
        log_path = Path(tmp) / "audit.log"
        gate = GovernanceGate(audit_log_path=log_path, cost_threshold=10.0)
        gate.request_approval("exp-5", estimated_cost=1.0, hazard_blocked=False)
        events = gate.read_audit_log()
        assert len(events) == 1
        assert events[0]["event"] == "approval_decision"


def test_hazard_screening_blocks_denied_element():
    result = screen({"elements": ["Pu"], "dopant_fraction": 0.1})
    assert result.is_blocked


def test_hazard_screening_allows_safe_composition():
    result = screen({"elements": ["Li", "La", "Zr", "O"], "dopant_fraction": 0.1})
    assert not result.is_blocked
