# Lambert Review: Script Builder Repeat Prompt Fix

**Date:** 2026-04-19
**Commit:** ac71c83 (`Fix script builder repeat prompt`)
**Author:** Bishop (Backend Dev)
**Reviewer:** Lambert (Tester)
**Verdict:** ✅ APPROVED

## What Changed

- Repeat cue ("Let's hear that again." / "Сега ще го повторим.") now appears only between the first and second read-throughs, not after the second.
- Closing line changed from "That's the end of this episode. Thanks for listening." to "That's the end of this story. Thanks for listening!"
- Test expectation updated to match new output structure.

## Evidence Supporting Approval

1. **Both unit tests pass** — bilingual script structure and mismatched-sentence rejection.
2. **Full suite green** — all 78 tests pass with no regressions.
3. **Manual trace confirmed** — repeat cue appears exactly once, sentence pairs appear exactly twice, blank-line spacing is consistent.
4. **Single-sentence edge case** — works correctly (cue still appears between reads).

## Minor Observations (Not Blockers)

- **Empty-sentences edge case** produces double blank lines where pairs would normally go. Pre-existing design gap, not introduced by this fix.
- **Script wording drifts from spec template** in `decisions.md` (e.g. "Good job! See you soon!" vs "That's the end of this story. Thanks for listening!"). The team may want to reconcile the template or retire it. Not a blocker for this fix.
- **No test for zero-sentence articles.** Low risk but worth adding later.
