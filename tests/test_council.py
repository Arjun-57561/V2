import pytest
from council.orchestrator import CouncilOrchestrator

def test_orchestrator_init():
    orchestrator = CouncilOrchestrator()
    assert len(orchestrator.agents) == 7

# Add more tests
