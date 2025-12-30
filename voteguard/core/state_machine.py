from __future__ import annotations
from enum import Enum, auto
from typing import Tuple


class State(Enum):
    AADHAAR_ENTRY = auto()
    BIOMETRIC_CAPTURE = auto()
    BALLOT_SELECTION = auto()
    SECURE_STORAGE = auto()
    RECEIPT = auto()
    RESET = auto()


ALLOWED = {
    State.AADHAAR_ENTRY: {State.BIOMETRIC_CAPTURE},
    State.BIOMETRIC_CAPTURE: {State.BALLOT_SELECTION, State.AADHAAR_ENTRY},
    State.BALLOT_SELECTION: {State.SECURE_STORAGE, State.AADHAAR_ENTRY},
    State.SECURE_STORAGE: {State.RECEIPT},
    State.RECEIPT: {State.RESET},
    State.RESET: {State.AADHAAR_ENTRY},
}


def can_transition(src: State, dst: State) -> bool:
    return dst in ALLOWED.get(src, set())


def assert_transition(src: State, dst: State) -> Tuple[State, State]:
    if not can_transition(src, dst):
        raise ValueError(f"Invalid transition: {src.name} -> {dst.name}")
    return src, dst
