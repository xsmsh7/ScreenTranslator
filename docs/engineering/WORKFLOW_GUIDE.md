# ScreenTranslator Engineering Workflow

This document defines the advanced software engineering practices adopted to ensure stability, maintainability, and quality as the project scales.

## 1. The Development Loop (Test-First Agent Loop)

Instead of the fragile `Code -> Error -> Fix` loop, we adopt a robust `Plan -> Test -> Implement -> Verify` cycle.

### Phase 1: Planning (RFC)
**Trigger:** Any new feature > 50 lines of code or involving complex logic (e.g., UI Overlay, Async Translation).
- Agent creates a mini-RFC using `docs/engineering/templates/RFC_TEMPLATE.md`.
- **Key Output:** Identified Risks and clear Acceptance Criteria.
- **User Action:** Approve or refine the RFC.

### Phase 2: Test Design (The Safety Net)
**Trigger:** RFC Approved.
- Before modifying core logic, creating a reproduction script or a dedicated test case.
- **For UI/Overlay:** Create "Headless" tests (mocking OS inputs/outputs) to verify logic without needing to stare at the screen.
- **For Logic:** Write unit tests for edge cases (e.g., empty strings, network timeouts).
- **Goal:** The test should FAIL first (Red), verifying the tests validity.

### Phase 3: Implementation (Green)
- Write the code to pass the tests.
- Refactor code to meet structural standards (SOLID principles).

### Phase 4: Verification & Records (ADR)
- Run the tests.
- If a significant architectural trade-off was made (e.g., "Two-pass Rendering"), record it in `docs/adr/`.
- Final Manual Verification against RFC Acceptance Criteria.

---

## 2. Decision Records (ADR)
We use Architecture Decision Records (ADR) to capture "Why we did what we did".

- **Location:** `docs/adr/YYYY-MM-DD-title.md`
- **When to write:** Whenever a decision has a trade-off (e.g., Performance vs. Readability, Library A vs. Library B).

## 3. Directory Structure
```
docs/
  adr/           # History of decisions
  engineering/   # Process guides
    templates/   # RFC/ADR templates
tests/           # (New) Automated test suite
```
