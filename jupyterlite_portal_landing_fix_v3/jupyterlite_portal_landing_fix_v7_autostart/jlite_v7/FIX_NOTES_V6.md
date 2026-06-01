# V6 Quiz UI Fix

This patch fixes the notebook quiz UI problems visible when option text wraps to more than one line.

## Changes

1. Single-answer objective questions (`mcq_single`) still use true radio buttons, but the notebook injects CSS so wrapped option text no longer overlaps the following option.
2. Multiple-answer questions (`mcq_multi`) now use a vertical checkbox group instead of `SelectMultiple`. A listbox was confusing because it required Ctrl/Cmd-click for multiple selection and looked unlike ordinary quiz choices.
3. `Show Results` is disabled until after `Submit`. Its purpose is to fetch and display the graded result, score, correctness status, and explanations after submission.
4. Progress now updates when the learner changes an answer, not only after autosave or submit.
5. After submit, answer widgets are disabled so the displayed result corresponds to a fixed submitted answer set.
