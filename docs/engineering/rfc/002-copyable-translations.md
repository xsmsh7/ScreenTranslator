# RFC 002: Copyable Translation Text

## Metadata
- **Status:** Proposed
- **Date:** 2026-01-06
- **Author:** Antigravity

## 1. Problem Description (Why)
Currently, translated text is only rendered visually as pixels on an image overlay. Users cannot select or copy the translated text for use in other applications (e.g., pasting into documents, search engines, or note-taking apps).

**User Request:** "翻譯的字要能夠複製" (Translation text should be copyable)

## 2. Proposed Solution (How)

### UI Changes: `ResultWindow`
Add a new `QTextEdit` widget to display translated text in plain text format:
- **Widget Type:** `QTextEdit` (read-only, but selectable)
- **Position:** Below the visual overlay display
- **Content:** Final translated text (one line per original text line, or concatenated)

### Backend Changes: `AppController`
Modify the `update_ui_signal` to carry both:
1. Original text (already exists)
2. **Translated text** (new)
3. Visual overlay image (already exists)

Current signature:
```python
update_ui_signal = pyqtSignal(str, object)  # (original_text, image)
```

Proposed signature:
```python
update_ui_signal = pyqtSignal(str, str, object)  # (original_text, translated_text, image)
```

## 3. Implementation Steps (Plan)
1. Update `ResultWindow.update_display()` to accept 3 parameters
2. Add `translated_text_display` QTextEdit widget to UI
3. Modify `AppController.process_image_threaded()` to emit translated text
4. Test with multi-line translations

## 4. Alternatives Considered
- **Option A: Copy button**: Add a "Copy Translation" button that copies to clipboard.
  - *Pros*: Explicit action, familiar UX
  - *Cons*: Extra click required; less flexible than free-text selection
- **Option B: Text-only display** (Selected): QTextEdit with selectable text.
  - *Pros*: Standard behavior, users can select partial text
  - *Cons*: None significant

## 5. Risks & Countermeasures
- **Risk**: Signal signature change breaks existing code.
  - **Mitigation**: Update all `emit()` and `connect()` calls atomically in same commit.

## 6. Verification & Acceptance Criteria
- [ ] **Manual Test**: Select Chinese translated text → Right-click Copy → Paste into Notepad → Verify characters intact
- [ ] **Edge Case**: Multi-line translation displays correctly with line breaks
