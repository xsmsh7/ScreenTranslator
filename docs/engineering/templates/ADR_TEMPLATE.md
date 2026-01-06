# ADR 000: [Short Title of Decision]

## Metadata
- **Status:** [Proposed | Accepted | Deprecated | Superseded]
- **Date:** YYYY-MM-DD
- **Context:** [Relevant RFC or Issue ID]

## 1. Context (The Force)
*Describe the situation and the tension. What technical constraint or business requirement led to this decision?*
- Example: "Text rendering flickers on high-pass backgrounds, causing user eye strain."
- Example: "Tesseract OCR is too slow for real-time video feeds."

## 2. Decision
*State the key architectural decision clearly.*
- Example: "We will implement a two-pass rendering system: Pass 1 draws all background rectangles, Pass 2 draws all text on top."

## 3. Consequences
*What becomes easier? What becomes harder? (Trade-offs)*
- **Positive:** Improved readability; eliminates Z-fighting/overlapping artifacts.
- **Negative:** Rendering loop iterates twice (O(2n) vs O(n)), slight performance penalty.
- **Neutral:** Requires refactoring the `Overlay.draw()` method.
