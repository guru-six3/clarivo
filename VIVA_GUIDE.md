# Clarivo: viva and code walkthrough

## A short introduction

“My project is a College FAQ Chatbot for examination queries. It preprocesses the student's question, represents it using TF-IDF and compares it with example questions using cosine similarity. It returns a stored answer only if the match passes confidence checks. I added related-question suggestions and countdowns for configured examination dates. It runs locally and does not require a paid AI service.”

## Understand the flow

```text
Student question
  -> lowercasing and tokenization
  -> stop-word removal
  -> TF-IDF vector
  -> cosine similarity with stored question vectors
  -> best score for each FAQ topic
  -> threshold, coverage and ambiguity checks
  -> stored answer or fallback
  -> related questions and optional countdown
```

## `chatbot.py`, in source order

Read the source beside this guide. Each block below explains the statements in the same order.

1. `math` supplies logarithm and square root. `re` extracts words. `Counter` counts token occurrences. `date` parses and subtracts dates.
2. `STOP_WORDS` is a set of common grammatical words. A set makes membership checks simple and fast. We keep useful exam vocabulary such as `fee`, `registration` and `results`.
3. `tokenize(text)` lowercases the input. `re.findall` extracts sequences of English letters or digits. The list comprehension excludes stop words. For example, `When do semester exams start?` becomes `['semester', 'exams', 'start']`.
4. `countdown(event, today)` converts an ISO date to a Python date, subtracts today's date and reads the integer `.days`. It selects a human-readable status, then returns the original event fields plus `days` and `status`. Negative days mean the event has passed. Passing `today` explicitly makes edge cases testable.
5. `FAQBot.__init__` stores the configuration. `self.faqs` maps FAQ IDs to entries so related questions can be looked up directly.
6. `self.documents` creates an `(FAQ ID, tokens)` pair for each example question. Multiple documents can belong to one FAQ.
7. `frequency` counts how many documents contain each word. `set(words)` prevents a repeated word in one question from increasing document frequency twice.
8. `count` is the total number of question documents. `self.idf` computes a smoothed inverse document frequency for every known word.
9. `self.vectors` precomputes the vector for every example question. This work happens once at startup, not for every request.
10. `vector(words)` first counts known tokens. Unknown tokens do not have an IDF weight. It multiplies each count by its IDF weight, then computes the Euclidean vector length.
11. Dividing each weight by that length creates a unit-length vector. Empty input returns an empty dictionary and avoids division by zero. Dictionaries store only nonzero weights, so no matrix library is needed.
12. `answer(question, today)` allows a test date; otherwise it uses today's date. The server supplies the college-local date. It tokenizes the query and creates its normalized vector.
13. The loop calculates a dot product with each example vector. A missing token contributes zero through `vector.get(word, 0)`.
14. `scores[owner]` keeps the highest example-question score for each FAQ. This prevents several paraphrases of one FAQ from being mistaken for competing topics.
15. `ranked` sorts topics by descending score. `owner` and `score` identify the best topic. `runner_up` is the second topic's score.
16. `coverage` measures the fraction of meaningful query tokens found in the vocabulary. This stops text like `exam banana spaceship purple` from being accepted merely because `exam` matches.
17. `accepted` requires a score of at least `0.32`, coverage of at least `0.5` and a topic-score margin of at least `0.10`. These are configurable demo heuristics. They reduce errors without guaranteeing correctness.
18. A rejected match returns `matched: False`, a fallback answer, three starter suggestions and no event. `score` is a similarity value, not an accuracy percentage.
19. An accepted match looks up the FAQ and its optional event. It returns the stored answer, curated related questions and a countdown if an event is linked. The answer is never fabricated by a generator.

## The maths, with a small example

We use raw count as term frequency:

```text
TF(word, document) = number of occurrences of that word
IDF(word) = ln((1 + N) / (1 + DF(word))) + 1
weight(word) = TF(word, document) * IDF(word)
normalized weight = weight / sqrt(sum of squared weights)
cosine similarity = dot product of the normalized vectors
```

`N` is the number of example questions. `DF` counts example questions containing the word. Smoothing avoids dividing by zero and keeps IDF positive.

If normalized vectors are `[0.6, 0.8]` and `[0.8, 0.6]`, their cosine similarity is `0.6*0.8 + 0.8*0.6 = 0.96`. Identical vectors have similarity `1`; vectors sharing no weighted words have similarity `0`. Nonnegative TF-IDF values make this project's scores range from `0` to `1`.

## `server.py`, in source order

- Imports handle JSON, dates, HTTP, paths and timezone conversion. The engine is imported from `chatbot.py`.
- `ROOT` uses the source file's location, so data paths do not depend on the terminal's current folder.
- `DATA` reads the JSON once. `BOT` builds the vectors once. Restart after editing FAQ data.
- `today()` converts the current time to the configured college timezone and extracts its calendar date.
- `Handler` extends Python's standard static-file handler. Its initializer serves only the `static` directory, keeping the Python source and FAQ JSON outside the static web root.
- `send_json` encodes a response, sets status and headers, sends the byte length, then writes the body. `no-store` prevents stale API responses from being reused.
- `do_GET` serves the calendar endpoint, or delegates ordinary static-file requests to the parent handler.
- `do_POST` accepts only `/api/chat`. It bounds the body size, parses JSON, and requires a nonempty string of at most 500 characters. Bad requests receive HTTP 400; unknown POST paths receive 404.
- Valid input goes to `BOT.answer` with the college-local date. `send_json` returns its result.
- The main guard runs only when this file is started directly. `argparse` supports an optional port. `ThreadingHTTPServer` serves the local browser and handles separate requests without adding an application framework.

## Browser files

`index.html` defines the header, sample calendar, live message log, suggested starting questions and form. Labels and semantic elements support keyboard and assistive-technology use.

`styles.css` defines shared colors, the calendar/chat layout, the orbit motif and responsive breakpoints. It also honors reduced-motion settings.

`app.js` runs in the browser:

1. Select page elements and preserve a copy of the welcome screen.
2. Create display elements with `textContent`, so typed text is treated as text rather than executable HTML.
3. Format ISO dates for display, using noon to avoid UTC-midnight date shifts.
4. `ask` prevents duplicate submissions, shows the student's question and a loading state, then sends JSON to `/api/chat`.
5. Read the response and display the answer, optional countdown and related-question buttons.
6. If the request fails or times out after ten seconds, restore the question for retry. Reenable controls in `finally`.
7. Form submission calls `ask`; delegated button clicks call it with a complete suggested question. New chat restores the welcome screen.
8. `loadCalendar` gets server-calculated countdowns, sorts dates and renders each event. A one-minute interval refreshes the calendar.

## Likely viva questions

**Why TF-IDF?** It is simple to inspect and works well for a small, controlled FAQ corpus. Rare topic words carry more weight.

**Why cosine similarity?** It compares vector direction, reducing the effect of question length. Normalized vectors simplify its calculation to a dot product.

**Is this machine learning?** It is a statistical NLP retrieval approach. It fits vocabulary and IDF weights from the example corpus. It is not a trained neural network or supervised intent classifier.

**Are suggestions AI-generated?** No. Each FAQ stores related FAQ IDs. Retrieval chooses the topic; its relationship list chooses relevant follow-up questions.

**Why a fallback?** Returning the nearest answer for every input would confidently answer unrelated questions. Confidence checks allow the system to admit uncertainty.

**Is a score of 0.8 an 80% chance of being correct?** No. It is a cosine-similarity score, not a calibrated probability.

**What happens after an exam date?** The countdown becomes negative and displays how many days ago the event occurred.

**Can it answer `How much is that?` after a revaluation answer?** It does not resolve pronouns or remember conversational context. The suggestion button sends a full question instead.

**What are the limitations?** Vocabulary overlap is not semantic understanding. Typos, unseen synonyms, negation and multiple topics can cause failures. Answers and dates must be maintained manually using official sources.

**How would you improve it?** Collect real student paraphrases, create a separate labelled evaluation set, measure retrieval and fallback quality, and then consider stemming or more robust semantic retrieval if justified.
