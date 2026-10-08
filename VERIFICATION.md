# Verification

Verified on 8 October 2026 using Python 3.14.6 and the Codex in-app browser.

## Automated engine checks

`python3 -m unittest -v`: **6 test methods passed**.

- Held-out phrasings for hall tickets, revaluation fees, results, registration deadlines, semester exams, answer-script copies and attendance.
- Empty, unrelated and mostly unknown input triggers fallback.
- An ambiguous multi-topic example triggers fallback.
- Revaluation returns the configured related FAQ IDs.
- Future, tomorrow, today and past countdown states are correct.
- All stored example questions retrieve their intended FAQ; related FAQ and event references resolve.

These examples are a small regression suite. They do not establish an accuracy percentage or prove all unknown or ambiguous queries will be rejected.

## Browser checks

- Local page and calendar loaded through the Python server.
- Semester-exam starter displayed its stored answer, 39-day sample countdown and related questions.
- Clicking the hall-ticket suggestion returned the hall-ticket answer and sample countdown.
- An unrelated weather query displayed fallback suggestions.
- New chat restored the opening screen.
- Enter-key submission returned a revaluation answer on a 390px-wide phone viewport.
- Desktop opening screen visually inspected at 1365 × 950.
- Phone layout inspected at 390 × 844; document width equaled viewport width, with no horizontal overflow.

## Limits of verification

Not tested in every browser, on a physical phone, with a screen reader, or at 200% text enlargement. Network-failure recovery and malformed-request handling are implemented but were not manually exercised. Official college policies and dates have not been verified; supplied content is explicitly a demonstration. This server is for a local assignment demo.
