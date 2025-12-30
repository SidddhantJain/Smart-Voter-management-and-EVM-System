from voteguard.core.state_machine import State, can_transition, assert_transition
import pytest

def test_valid_transitions():
    assert can_transition(State.AADHAAR_ENTRY, State.BIOMETRIC_CAPTURE)
    assert can_transition(State.BIOMETRIC_CAPTURE, State.BALLOT_SELECTION)
    assert can_transition(State.BALLOT_SELECTION, State.SECURE_STORAGE)
    assert can_transition(State.SECURE_STORAGE, State.RECEIPT)
    assert can_transition(State.RECEIPT, State.RESET)
    assert can_transition(State.RESET, State.AADHAAR_ENTRY)


def test_invalid_transition_raises():
    with pytest.raises(ValueError):
        assert_transition(State.AADHAAR_ENTRY, State.SECURE_STORAGE)
