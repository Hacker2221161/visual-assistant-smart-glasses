# MVP Definition — Vector Vision

## Version
Vector v0.2 — February 2026

## MVP Focus
**Single user · Single function · Real-world scenario**

This MVP deliberately limits scope to prove feasibility, ethical control, and real accessibility value.

---

## Target User
**Blind or severely visually impaired person**

Characteristics:
- Cannot reliably detect obstacles visually
- Navigates urban environments independently
- Uses audio as primary feedback channel

---

## Core Problem
Urban navigation is dangerous for blind users due to:
- Unexpected obstacles (curbs, poles, stairs)
- Poorly designed infrastructure
- Delayed or absent feedback from existing tools

Traditional tools (white cane, guide dog) do not provide **anticipatory information**.

---

## MVP Goal
Provide **real-time auditory awareness** of immediate obstacles using smart glasses.

The system does NOT navigate or decide — it only **informs**.

---

## Single MVP Function
**Obstacle & Object Awareness**

The system detects:
- Curbs / steps
- Large obstacles (poles, walls, vehicles)
- Open pathways vs blocked paths

And provides:
- Short, non-intrusive voice feedback

Example:
> “Step down ahead.”  
> “Obstacle on the right.”

---

## Minimal Hardware Stack
- Camera (mounted on glasses)
- Processing unit (smartphone / Raspberry Pi / edge device)
- Audio output (bone conduction or earphone)

No cloud dependency required for MVP.

---

## Minimal AI Stack
- Object detection model (edge-capable)
- Depth estimation or heuristic distance estimation
- Rule-based decision layer (no autonomous decision making)

AI role is **perception only**, not control.

---

## Ethics & Safety Constraints (Mandatory)

The system MUST:
- Never issue commands (only informational statements)
- Never override user intent
- Never collect or transmit data by default

The system MUST ALWAYS:
- Prioritize user safety over performance
- Fail silently and safely

The system MUST NOT:
- Navigate on behalf of the user
- Make assumptions about user intent
- Store biometric or visual data

---

## Human-in-the-Loop Principle
The user:
- Makes all movement decisions
- Can disable the system instantly
- Controls feedback frequency

AI is an assistant, not an authority.

---

## Success Criteria
MVP is successful if:
- User receives timely obstacle warnings
- False positives are minimal and non-disruptive
- System operates fully offline
- Ethical constraints are enforced by design

---

## Why This MVP Matters
- Demonstrates real accessibility impact
- Validates ethical AI architecture
- Provides foundation for future modules

This MVP proves that **responsible AI assistance** is achievable without autonomy or surveillance.
