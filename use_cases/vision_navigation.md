# Use Case — Blind User Street Navigation (Vector Vision)

## Use Case ID
UC-VISION-001

## Module
Vector Vision (MVP)

## User Type
Blind or severely visually impaired user

The user cannot reliably see obstacles and relies primarily on audio feedback and tactile cues.

---

## Environment
Urban outdoor environment:
- Sidewalks
- Curbs
- Poles
- Stairs
- Parked vehicles
- Pedestrian paths

The environment is dynamic and unpredictable.

---

## Problem Description (Simple Explanation)
A blind person walking outside cannot see:
- where the sidewalk ends
- if there is a step down or up
- if an obstacle suddenly appears in front of them

Traditional tools:
- white cane → detects obstacles only after contact
- guide dog → not always available

The user needs **early awareness**, not instructions.

---

## Goal of the Use Case
To provide **early, short, audio warnings** about nearby obstacles.

The system must:
- inform, not command
- support, not control
- assist, not replace human decision-making

---

## Preconditions
- The user is wearing smart glasses
- The system is turned ON
- Audio output is enabled
- The system operates offline

---

## Main Scenario (Step by Step)

1. The user walks forward on a sidewalk.
2. The camera continuously observes the area in front of the user.
3. The system detects a change in ground level ahead (curb).
4. The system estimates that the curb is close enough to be relevant.
5. The system generates a short audio message:
   > “Step down ahead.”
6. The user hears the message.
7. The user decides how to react:
   - slow down
   - stop
   - use a cane to confirm
8. The system remains silent unless a new relevant obstacle appears.

---

## Alternative Scenarios

### A. Obstacle on the Side
- A pole is detected on the right side.
- Audio message:
  > “Obstacle on the right.”

### B. Clear Path
- No relevant obstacles detected.
- The system stays silent.

Silence is considered correct behavior.

---

## Error and Uncertainty Handling

If the system:
- is unsure about detection
- cannot estimate distance reliably
- experiences sensor issues

Then:
- The system does **NOT** speak
- The system does **NOT** guess
- The system fails silently

---

## Ethical and Safety Constraints

The system MUST:
- Never say “go”, “turn”, “stop”, or similar commands
- Never override user decisions
- Never pressure the user to act

The system MUST NOT:
- Navigate for the user
- Decide a path
- Assume user intent

The system provides **information only**.

---

## Human-in-the-Loop Principle

The human:
- makes all movement decisions
- remains fully responsible for actions
- can disable the system instantly

The system is an assistant, not an authority.

---

## Expected Outcome
- The user receives early awareness of obstacles
- The user remains in full control
- The system reduces risk without removing autonomy

---

## Success Criteria
This use case is successful if:
- Audio warnings are timely and minimal
- False alerts are rare
- Silence is preserved when nothing relevant happens
- The user feels supported, not controlled

---

## Why This Use Case Matters
This scenario demonstrates that:
- Useful AI assistance does not require autonomy
- Ethical constraints can be enforced by design
- Accessibility-focused AI can improve safety without surveillance

This use case forms the foundation of the Vector Vision MVP.
