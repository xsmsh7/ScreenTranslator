# RFC 001: OCR Reliability & Engine Strategy

## Metadata
- **Status:** Proposed
- **Date:** 2026-01-06
- **Author:** Antigravity

## 1. Problem Description (Why)
The user reports that when selecting a large area with text, **only the first few blocks are captured**.
- **Root Cause Analysis:** The current Tesseract configuration uses `--psm 6` (Assume a single uniform block of text). When the user selects a complex region (multiple paragraphs, columns, or scattered text), Tesseract aborts after the first cohesive block.
- **User Pain Point:** "Only first few grids captured", "OCR sometimes bad".

## 2. Proposed Solution (How)

### Phase 1: Immediate Fix (Tesseract Config)
- **Change:** Switch `pytesseract` config from `--psm 6` to `--psm 3` (Fully automatic page segmentation, but no OSD) or `--psm 11` (Sparse text).
- **Impact:** Allows capturing multiple disconnected blocks of text in a single screenshot.

### Phase 2: Strategic Engine Upgrade (Windows Native OCR)
The user asked: *"OCR 只能用其他人的?"* (Do we have to use third-party EXEs?).
- **Proposal:** Switch to **Windows.Media.Ocr** (Built-in Windows 10/11 API).
- **Pros:** 
  - No external EXE installation (Tesseract).
  - No huge model download (PaddleOCR).
  - High accuracy for screen text (optimized by Microsoft).
  - Native speed.
- **Cons:** Requires `winrt` Python package; Async API requires bridging.
- **Implementation:** Create an `OCRProvider` interface to support switching engines.

## 3. Implementation Steps (Plan)
1.  **Reproduction Test:** Create a test case with a Multi-Block Image locally.
2.  **Verify Failure:** Confirm PSM 6 misses the second block ("Red" state).
3.  **Fix:** Update `OCRService` to use Auto-Segmentation (PSM 3).
4.  **Verify Fix:** Confirm test passes ("Green" state).
5.  *(Future)*: Draft implementation plan for `WindowsOCRProvider`.

## 4. Risks & Countermeasures
- **Risk:** PSM 3 might include more "noise" (artifacts interpreted as text).
- **Mitigation:** Add confidence filtering (currently missing). Only accept text with variable `conf > 50` (Tesseract data includes confidence).

## 5. Verification & Acceptance Criteria
- [ ] **Automated Test:** `tests/test_ocr_completeness.py` passes with a multi-paragraph image.
- [ ] **Manual Check:** User selects a whole discord chat window and all messages are translated.
