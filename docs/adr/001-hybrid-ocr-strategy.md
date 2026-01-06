# ADR 001: Hybrid OCR Strategy

## Metadata
- **Status:** Accepted
- **Date:** 2026-01-06
- **Context:** RFC 001

## 1. Context (The Force)
- Users want high accuracy and "native" feel (Windows OCR).
- Users also encounter "text cutoff" issues with Tesseract default settings.
- We need a solution that works immediately but paves the way for a better engine.
- `winsdk` installation on Python 3.14 (Beta) involves compilation, which is slow/risky.

## 2. Decision
We implement a **Hybrid Strategy** in `OCRService`:
1.  **Primary:** Attempt to use `WindowsOCR` (via `winsdk`).
2.  **Fallback:** Use `Tesseract` with optimized config (`--psm 3`) if Windows OCR is unavailable.

## 3. Consequences
- **Positive:**
    - Immediate fix for "Text Cutoff" bug (via Tesseract PSM 3).
    - Future-proof: As soon as `winsdk` is installed/compiled, the app automatically upgrades to Windows Native OCR without code changes.
    - Robustness: If Windows OCR fails at runtime, we fallback to Tesseract.
- **Negative:**
    - Complexity: `OCRService` now manages two codepaths.
    - Dependency: Added `winsdk` which is heavy to build on some systems.
