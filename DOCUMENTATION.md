# ScamLens: Project Documentation

*Understand suspicious messages before acting on them.*

---

## 1. What is ScamLens?

ScamLens is a web app that checks a message (SMS, email, chat) for common scam signs and tells the user, in simple language:

- **How risky** the message looks (Low / Medium / High, with a 0-100 score)
- **Why**: the exact phrases that triggered a warning, highlighted in the original text
- **What to do now**: safe next steps
- **Its limits**: it only reads the text and cannot confirm who really sent it

It also has a **batch mode**: upload a CSV with many messages and get a risk score for every row.

### Design principles
1. **Explainable first.** Rules are visible and show their evidence. No black box.
2. **AI is optional.** The AI only rewrites the explanation. The score and highlights come from rules, so the demo works with no internet.
3. **Modular.** Each stage can be replaced without touching the others.

---

## 2. How it works

```
 Input text ──► detector.py ──► findings + score ──► explainer.py ──► app.py
 (or CSV)       (rules)         (evidence, level)    (AI or template)  (screen)
                    │
                    └──► batch.py (same detector, applied to every CSV row)
```

### Step by step
1. The user pastes a message (or uploads a CSV) in `app.py`.
2. `detector.analyze(text)` checks the text against every rule in `RULES` using regular expressions (case-insensitive).
3. For each rule that matches, it records the rule name, severity (1-3), a "why it matters" sentence, and every matching phrase with its position.
4. A score is computed (see 4.1) and mapped to a level.
5. `explainer.explain()` turns the findings into 3 plain sentences. It tries Groq; if that fails for any reason it uses a template.
6. `app.py` shows the score, explanation, highlighted text, expandable evidence per rule, and the "Do this now" panel.

---

## 3. Project structure

| File | Purpose |
|---|---|
| `app.py` | Streamlit interface: two tabs (Single message, Batch CSV) |
| `detector.py` | The `RULES` list and the `analyze(text)` function |
| `explainer.py` | AI explanation via Groq, with automatic template fallback |
| `batch.py` | `analyze_dataframe(df, column)` runs the detector on every CSV row |
| `test_cases.py` | `SAMPLES` (used by the app dropdown) and a pytest test |
| `sample_messages.csv` | Example file for the Batch tab |
| `check_ai.py` | Checks your Groq key and lists models available to it |
| `requirements.txt` | Python libraries |
| `.env.example` | Template for your secret key file |
| `.gitignore` | Keeps `.env`, `.venv`, caches out of Git |
| `TEAM_SETUP.md` | GitHub and teammate onboarding |
| `DOCUMENTATION.md` | This file |

### Tech stack
Python 3.12, Streamlit (UI), pandas (CSV handling), Groq API (optional AI), pytest (tests), Git + GitHub (collaboration).
`scikit-learn` is installed for a possible v3 anomaly/ML step but is **not used yet**.

---

## 4. Key components in detail

### 4.1 `detector.py`
Each rule looks like this:
```python
{
    "name": "Request for sensitive data",
    "patterns": [r"\botp\b", r"password", ...],   # regex patterns
    "severity": 3,                                # 1 (weak) to 3 (strong)
    "why": "Real banks never ask for OTPs...",    # shown to the user
}
```
Current rules: urgency or threats, request for sensitive data, payment pressure, suspicious link, too-good-to-be-true offer, impersonation of an authority.

**Scoring:**
- `raw` = sum of severities of the rules that fired
- `max` = sum of severities of all rules (13 currently)
- `score = min(100, round(100 * raw / max * 1.6))`
- Level: **High** if score >= 60, **Medium** if >= 30, otherwise **Low**

`analyze()` returns:
```python
{"score": 74, "level": "High",
 "findings": [{"rule": "...", "severity": 3, "why": "...",
               "evidence": [{"text": "OTP", "start": 52, "end": 55}]}]}
```
This structure is the contract between all other files. If you keep it, everything else keeps working.

### 4.2 `explainer.py`
- Reads `GROQ_API_KEY` from `.env`.
- Tries models in order: your `LLM_MODEL` (if set), then `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `llama-3.3-70b-versatile`.
- The prompt tells the model to use only the detected signs and to avoid claiming certainty.
- On any failure (no key, no internet, retired model), it returns a template sentence.
- The UI shows **"by AI"** or **"by template"** so you always know which was used.

### 4.3 `app.py`
- **Single message tab:** sample dropdown, text box, Analyze button, results.
- **Batch tab:** upload CSV, pick the text column, get totals, a bar chart by risk level, a table, and a results download.
- `highlight()` merges overlapping matches and escapes HTML before marking text, so pasted content can't break the page.

### 4.4 `batch.py`
Adds `risk_score`, `risk_level` and `signs` columns to the uploaded table.

---

## 5. Setup (new teammate)

Full detail is in `TEAM_SETUP.md`. The short version:

```powershell
git clone https://github.com/<owner>/ScamLens.git
cd ScamLens
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # then paste your Groq key into .env
streamlit run app.py
```
Check everything with:
```powershell
pytest
python check_ai.py
```

---

## 6. How to work on it

### Add or change a rule
Edit `RULES` in `detector.py`. Add a dictionary with `name`, `patterns`, `severity`, `why`. Save, and Streamlit reloads automatically.

### Add a test case
Add an item to `SAMPLES` in `test_cases.py` with `name`, `text`, `expected` ("High", "Medium" or "Low"), then run `pytest`. If the detector gets it wrong, fix the rules.

### Change the AI behaviour
Edit the `prompt` in `explainer.py`.

### Change the look
Edit `app.py` only (titles, layout, columns, texts).

### Git routine
`git pull` > edit > `git add .` > `git commit -m "message"` > `git push`. Pull before every push.

### Who owns what (suggested)
| Person | Files |
|---|---|
| 1: Detection and AI | `detector.py`, `explainer.py` |
| 2: Interface | `app.py` |
| 3: Testing and research | `test_cases.py`, `sample_messages.csv` |
| 4: Integration and pitch | Git, `README.md`, docs, demo |

---

## 7. Adapting it to the hackathon problem statement

The pipeline is generic: **input > rules or AI > score and evidence > explanation > dashboard.**

| If the problem is about... | Change |
|---|---|
| Other risky text (fake news, harassment, fake reviews) | Rewrite `RULES`, the "Do this now" text and sample messages |
| Table data (students, patients, transactions) | Use the Batch tab; write rules that check column values instead of regex on text |
| Prioritising or ranking items | Reuse the score and sort the table by it |
| Explaining or simplifying content | Lean on `explainer.py`, change the prompt |
| Something else | Keep the layout, tabs, charts and download; replace the logic in `detector.py` |

Keep the `analyze()` output structure the same and the UI keeps working.

---

## 8. Known limitations (say these honestly in your pitch)

- Rules are keyword-based, so they miss new scam wording and can flag genuine messages. For example, a real bank message warning "never share your OTP" contains the word OTP.
- English only. Messages in other languages or in mixed scripts are not detected.
- Text only. It does not check links against blocklists, verify senders, or inspect images and voice calls.
- The score is a simple heuristic, not a probability.
- The AI explanation can only explain what the rules found, and can occasionally be imperfect.

### Possible next steps
- Add Tamil and Hindi patterns.
- Train a scikit-learn classifier on a public, licensed dataset and compare with the rules.
- Check URLs (domain age, lookalike domains).
- Add a browser extension or WhatsApp bot front end.
- Reduce false positives with "context" rules (for example, ignore OTP when preceded by "do not share").

---

## 9. Troubleshooting

| Problem | Fix |
|---|---|
| `python` not found | Use full path to Python 3.12 or fix PATH; see `TEAM_SETUP.md` |
| `ModuleNotFoundError` | Activate `.venv`, run `pip install -r requirements.txt` |
| App shows "by template" | `.env` missing, wrong folder, or no internet; run `python check_ai.py` |
| `SyntaxError` after editing | Check indentation and unclosed brackets, or restore the file with `git checkout <file>` |
| Push rejected | `git pull` first, then push |
| Port already in use | `streamlit run app.py --server.port 8502` |
| Blank page or odd cache | Press `C` then "Clear cache" in the app, or restart Streamlit |
| Teammate's version differs | Everyone should be on Python 3.12 and the same `requirements.txt` |
