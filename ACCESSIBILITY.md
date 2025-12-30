# Accessibility as Correctness

Principles:
- Predictable, deterministic UI state machine.
- Keyboard-only navigation and controlled focus order.
- Reduced motion mode and text scaling.
- Clear, descriptive error messages block state transitions until resolved.

Status:
- State machine formalized in `voteguard/core/state_machine.py` for integration.
- Existing PyQt UI remains functional; future work will bind transitions to the formal state machine and enforce focus management.

Validation:
- Tests should assert state transition correctness and simulate key-only navigation flows.
