# Visual Assistant — Development Roadmap

This roadmap defines the staged technical evolution of the Visual Assistant system.
Each phase must be completed and validated before moving to the next.

---

## Phase 0 — Concept & Trust Foundation ✅ (COMPLETED)

Status: DONE

Artifacts:
- README.md
- ARCHITECTURE.md
- SECURITY.md
- ACCESSIBILITY.md
- RISK_ANALYSIS.md
- LICENSE

Goals:
- Define system vision and constraints
- Establish safety-first and privacy-first principles
- Identify unacceptable risk categories
- Ensure accessibility is a core feature, not an add-on

Exit criteria:
- No unresolved high-risk items
- Clear ethical boundaries documented

---

## Phase 1 — Core Logic Prototype (NO HARDWARE)

Status: PLANNED

Scope:
- Abstract decision-making logic
- Context awareness engine (logic only)
- Safety rule evaluation
- Kill-switch logic (logical layer)

No access to:
- Camera
- Microphone
- Network
- GPS (real)

Deliverables:
- /src/core/context_engine.py
- /src/core/safety_engine.py
- /src/core/kill_switch.py

Success criteria:
- Deterministic behavior
- 100% test coverage for safety rules
- No side effects or external dependencies

---

## Phase 2 — Simulation & Testing Environment

Status: PLANNED

Scope:
- Synthetic sensor input simulation
- Context scenario playback
- Failure-mode testing
- Edge-case validation

Deliverables:
- /simulator/mock_inputs.py
- /simulator/scenario_runner.py
- /tests/

Key scenarios:
- Walking on roadway
- Inactivity / sleep detection
- False positive prevention
- Emergency override

Exit criteria:
- No false-negative safety failures
- All critical paths covered by tests

---

## Phase 3 — Accessibility-First Interaction Layer

Status: PLANNED

Scope:
- Voice-only interaction logic (abstracted)
- Haptic feedback logic (abstracted)
- Zero-vision operation mode
- Assistive priority routing

Deliverables:
- /src/accessibility/voice_interface.py
- /src/accessibility/haptic_feedback.py

Constraints:
- Must function without visual output
- Must be interruptible at all times

---

## Phase 4 — Hardware Abstraction Layer (HAL)

Status: FUTURE

Scope:
- Hardware interfaces via abstraction only
- No direct sensor access by apps
- Permission-gated data flow

Deliverables:
- /hal/sensors.py
- /hal/power.py
- /hal/indicators.py

Security requirements:
- Physical LED indicator for camera/mic
- User-controlled hard disable

---

## Phase 5 — On-Device AI Integration

Status: FUTURE

Scope:
- Local inference only
- No cloud dependency by default
- Explainable decision outputs

Constraints:
- AI must NEVER override safety rules
- AI must be fully disableable

Deliverables:
- /ai/context_model.py
- /ai/explainability.py

---

## Phase 6 — Developer SDK (Optional)

Status: OPTIONAL

Scope:
- Third-party applications
- Strict sandboxing
- Safety policy enforcement

Constraints:
- No raw sensor access
- No background execution without user awareness

---

## Final Principle

If any phase introduces:
- Human safety risk
- Loss of user control
- Non-consensual data collection

→ Development MUST STOP.

Trust is not a feature.
Trust is the system.
