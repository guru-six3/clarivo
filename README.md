# Clarivo

A College FAQ Chatbot focused on **Examinations**, built for an MCA AI practical assignment. Python performs transparent TF-IDF and cosine-similarity retrieval. The browser provides a responsive interface, clickable related questions and date-aware countdowns.

## Run

Install Python 3.10 or newer. No API key, internet connection, package installation or build step is required on systems with timezone data.

1. Open a terminal in the `exam-compass` folder.
2. Run:

```sh
python3 server.py
```

On Windows, use `py server.py` if `python3` is not available. Visit **http://localhost:8000** in your browser. Stop the server with **Ctrl+C**. Open the URL through the server rather than double-clicking `index.html`.

If port 8000 is busy:

```sh
python3 server.py --port 8001
```

Then visit http://localhost:8001. If you receive `ZoneInfoNotFoundError` on a system without timezone data, install it using `python3 -m pip install tzdata` (Windows: `py -m pip install tzdata`). All other code uses the standard library.

## What is included

- Twelve examination FAQ topics with several example phrasings per topic.
- Lowercasing, word tokenization and stop-word removal.
- Smoothed IDF weighting and cosine similarity over normalized sparse vectors.
- Three safeguards: minimum similarity, known-word coverage and a margin between the best two FAQ topics.
- Related-question suggestions from an explicit, editable FAQ relationship list.
- Calendar and answer countdowns for configured events. Handles future dates, tomorrow, today and past dates.
- Keyboard submission, chat reset, a loading state, retry-friendly network errors, accessible control labels, phone layout and reduced-motion support.

## Files

```text
exam-compass/
  chatbot.py          Text preprocessing, vectors, retrieval and countdowns
  server.py           Local HTTP server and two API endpoints
  data/faqs.json      FAQ examples, answers, relationships, dates and thresholds
  static/index.html   Semantic page structure
  static/styles.css   Appearance and responsive layouts
  static/app.js       Browser interactions and API calls
  test_chatbot.py     Retrieval and countdown regression checks
  VIVA_GUIDE.md       Walkthrough, formulas and viva questions
  VERIFICATION.md     What was checked and practical limits
```

## Configure college information

**All shipped dates and FAQ guidance are demonstration content, not verified PSG or other college policies.** Replace the data with official notices before presenting it as a college information service. No fees, attendance percentages or publication dates are invented.

Edit `data/faqs.json`, then restart the server:

- `questions`: example questions for each FAQ. Add natural paraphrases here.
- `answer`: approved information to display.
- `related`: IDs of relevant FAQs. Suggestions are curated relationships, not generated predictions.
- `event`: event key, or `null` for an answer without a countdown.
- `events`: labels and dates in `YYYY-MM-DD` format.
- `timezone`: the college timezone, initially `Asia/Kolkata`.
- `threshold`: minimum cosine similarity, initially `0.32`.
- `ambiguity_margin`: minimum difference between the two best FAQ-topic scores, initially `0.10`.

Thresholds are small-demo heuristics, not calibrated probabilities. Changes to the examples change IDF and scores, so rerun the checks and try new paraphrases after editing. Date calculations use the configured timezone on the server, independent of the browser timezone. The calendar refreshes every minute; existing chat answers retain the countdown shown when they were answered.

## Check and demonstrate

```sh
python3 -m unittest -v
```

Try these questions in order:

1. `When do semester exams start?` to show matching, countdown and related questions.
2. Click the hall-ticket suggestion to show the next answer.
3. `How can I apply for revaluation?` to show another related-question group.
4. `How much money for revaluation?` to demonstrate a paraphrase.
5. `What is the weather today?` to demonstrate fallback.
6. Click **New chat** to return to the starting screen.

## Scope

This is a retrieval chatbot, not a language model. It chooses an existing FAQ answer using word overlap weighted by TF-IDF. It has no conversation memory or pronoun resolution, so a follow-up such as `What about its fee?` may fail; suggested questions are complete questions. It does not learn automatically, verify notices, send notifications, store chats or access student records. Inputs are English. Typos, unseen synonyms, negations and multi-topic questions can be misclassified. Test coverage is a regression check, not a measured real-world accuracy score.

The local server binds to `127.0.0.1` and is intended for a local practical demonstration. It is not a production hosting setup.
