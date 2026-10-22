# ScamLens Mobile: Team Plan

*Understand suspicious messages, in your own language, before acting on them.*

Read this top to bottom once, then work from Section 6 (Build order).

---

## 1. What we are building

An **Android app** where a user pastes or shares a suspicious message and gets:
- a **risk level** (Low, Medium, High) with a score
- the **exact warning phrases highlighted** in the message
- a **plain-language explanation** in English, Hindi or Tamil
- a **"Do this now"** card with safe next steps

The Streamlit web app we already built stays as our **guaranteed demo**. The mobile app is the "real product" layer on top of the same detection engine.

### Golden rule
**The mobile app is time-boxed.** If an APK is not running on a real phone by the halfway point of the hackathon, we stop and present the Streamlit app, and describe the mobile app as the next step. Detection quality and multilingual support are what judges score, so they come first.

---

## 2. Reality checks (everyone should know these)

1. **No API or SDK key fetches a user's messages.** Reading the SMS inbox needs the Android `READ_SMS` permission and native code, which in Capacitor means a community plugin or a custom plugin.
2. **iOS does not allow apps to read SMS.** Our demo is Android only.
3. **Google Play restricts SMS permissions.** A sideloaded APK is fine for a hackathon, but in the pitch we say **"user-initiated checking"**, not "automatic SMS scanning".
4. **The Groq API key must never be inside the app.** An APK can be unpacked and the key stolen. The key lives only on the backend server.
5. **Setup is the biggest time sink** (Android Studio, JDK, Android SDK, USB debugging). Start this on day one, in parallel.

---

## 3. Tech stack and purpose

| Layer | Technology | Purpose |
|---|---|---|
| Mobile UI | **React** (with Vite) | Screens: input, results, language selector |
| Styling | **HTML, CSS** (mobile-first, optionally Tailwind) | Large, readable, single-column layout for phones |
| Mobile wrapper | **Capacitor** (Android) | Packages the React web app as an installable Android app and gives access to native features |
| Clipboard | `@capacitor/clipboard` (official) | "Paste message" button |
| Share-to-app | Community "send intent" or share-target plugin for Capacitor (check its repo for Capacitor version support before using) | Lets users share a message from their messaging app into ScamLens |
| SMS inbox reading (stretch only) | Community SMS plugin or a custom native plugin | List recent messages to check. Needs `READ_SMS` permission |
| Backend API | **FastAPI (Python)**, reusing `detector.py`, `explainer.py`, `batch.py` | One `/analyze` endpoint; keeps all logic and the Groq key off the phone |
| Alternative backend | Node.js + Express with rules ported to JavaScript | Only if the team is much stronger in Node (costs about an hour and duplicates the rules) |
| Detection | Python `re` rules (English, Hindi, Tamil, romanised) | Transparent evidence, works offline |
| AI | **Groq LLM API** | Multilingual explanations, and a second detector for scams the rules miss |
| URL checks (optional) | `tldextract`, `rapidfuzz` | Flag lookalike and suspicious domains |
| Log analysis (stretch) | pandas, scikit-learn `IsolationForest` | Security log tab on the web app |
| Config and secrets | python-dotenv (`.env` on backend) | API key storage |
| Testing | pytest (backend), phone testing (app) | Catch false positives and regressions |
| Collaboration | Git and GitHub | One repo, routine in `GIT_WORKFLOW.md` |
| Presentation | PowerPoint (4-5 slides), Canva (poster) | Evaluation rounds |

---

## 4. App architecture

```
┌──────────────────────────────┐
│  Android phone               │
│  React UI in Capacitor       │
│  Input: paste / share / SMS  │
└──────────────┬───────────────┘
               │ HTTPS or HTTP (hotspot IP in dev)
               ▼
┌──────────────────────────────┐
│  FastAPI backend             │
│  1. Rule engine (re)         │
│  2. Language detection       │
│  3. URL checks (optional)    │
│  4. Groq LLM (key lives here)│
└──────────────┬───────────────┘
               ▼
   score, evidence spans, explanation, next steps
```

### Repo layout (monorepo)

```
ScamLens/
├── app.py, detector.py, explainer.py, batch.py ...   (existing Streamlit app + engine)
├── api.py
└── mobile/
    ├── src/ (App.jsx, components/)
    ├── capacitor.config.json
    └── android/
```

### API contract (agree on this first, so frontend and backend work in parallel)

`POST /analyze`

Request:
```json
{ "text": "Your account will be blocked. Share OTP.", "language": "en" }
```
Response:
```json
{
  "score": 74,
  "level": "High",
  "explanation": "This message may be a scam because ...",
  "explanation_source": "AI",
  "findings": [
    { "rule": "Request for sensitive data", "severity": 3,
      "why": "Real banks never ask for OTPs...",
      "evidence": [ { "text": "OTP", "start": 34, "end": 37 } ] }
  ],
  "next_steps": ["Do not share the OTP", "Call the official number", "Report at cybercrime.gov.in or 1930"]
}
```
`GET /health` returns `{"status": "ok"}` (used by the app to show "server not reachable").

Note: `detector.analyze()` already returns the score, level and findings in this shape. The API mainly adds the explanation, the next steps and the language.

---

## 5. Features and workflows

### 5.1 Feature list

| Priority | Feature |
|---|---|
| **Must** | Paste a message and analyze |
| **Must** | Risk level and score, highlighted evidence, "Do this now" card |
| **Must** | Multilingual detection (Hindi, Tamil, English, plus romanised) |
| **Must** | Explanation in the chosen language, with template fallback |
| **Must** | Error and offline state ("cannot reach server") |
| **Should** | Share-to-ScamLens from other apps |
| **Should** | Language selector (auto-detect by script, manual override) |
| **Should** | Copy or share the result (to warn family on WhatsApp) |
| **Stretch** | Check recent SMS from the inbox (`READ_SMS`) |
| **Stretch** | URL lookalike check |
| **Stretch** | Security log analysis (stays on the Streamlit web app) |

### 5.2 Workflow A: paste (the main demo path)

1. User copies a suspicious message in their messaging app.
2. Opens ScamLens and taps **Paste** (or types).
3. Taps **Analyze**; a loading indicator shows.
4. App sends `POST /analyze` to the backend.
5. Backend: detects the language, runs the rules, optionally asks the LLM, builds the response.
6. App shows the risk meter, highlighted message, explanation in the chosen language, and "Do this now".
7. User taps **Share result** or **Check another**.

### 5.3 Workflow B: share to ScamLens

1. In the messaging app, the user long-presses a message and chooses **Share**.
2. Selects **ScamLens**.
3. ScamLens opens with the text already filled in and starts analysis automatically (steps 4-7 above).

### 5.4 Workflow C: check SMS inbox (stretch)

1. User taps **Check my messages** and grants the SMS permission.
2. App lists recent messages, each with a **Check** button (user chooses; nothing is sent automatically).
3. Selected message goes through steps 4-7 of Workflow A.

### 5.5 Failure handling
- Backend unreachable: show a friendly message and a retry button.
- Groq fails: backend returns the template explanation with `"explanation_source": "template"`.
- Empty or very long input: validate on the client and the server.

### 5.6 Privacy line for judges
Rules run first; the user chooses which message to send; nothing is stored; the message is sent to the AI service only to generate the explanation. Future work: more on-device processing.

---

## 6. Build order

Each step must **work** before the next one starts. Commit and push after each step.

| # | Step | Owner | Time-box | Done when |
|---|---|---|---|---|
| 0 | **Android setup:** install Android Studio, JDK, enable USB debugging on a test phone | Person 2 (start now, in parallel) | 1-2 h | A blank Capacitor app runs on a phone or emulator |
| 1 | **Multilingual rules** in `detector.py` (Hindi, Tamil, romanised) | Person 1 | 45 min | Hindi, Tamil and Hinglish samples score Medium or High; normal messages stay Low |
| 2 | **`api.py`** (FastAPI): `/analyze` and `/health`, CORS on | Person 1 | 45 min | Opening `http://<laptop-ip>:8000/docs` and calling `/analyze` works |
| 3 | **Language support in `explainer.py`** (prompt takes a language; fixed UI strings in a dictionary) | Person 3 | 45 min | Tamil explanation appears; template fallback also works offline |
| 4 | **React UI**: input, Analyze, risk meter, highlighted text, explanation, "Do this now" (test in Chrome's phone view) | Person 2 | 1.5 h | Full flow works in the browser against the API |
| 5 | **Capacitor wrap** and run on a real phone | Person 2 | 1-2 h | App on the phone gets a result from the laptop backend |
| 6 | **Paste button** (Capacitor Clipboard) and **language selector** | Person 2 | 30 min | Copy in SMS app, paste in ScamLens, analyze |
| 7 | **Share-to-app** (send-intent plugin) | Person 2 | 1 h, optional | Sharing from messages opens ScamLens |
| 8 | Polish: app name and icon, loading and error states, share-result button | Person 2 and 3 | 45 min | Demo path takes under 90 seconds |
| 9 | Idea document, PPT, poster (not the code) | Person 4 | rolling | Submitted on time |
| 10 | Stretch only if everything above is stable: SMS inbox, URL check | whoever is free | n/a | n/a |

### Throughout
- **Person 3** also builds test messages (in all languages), checks false positives with native speakers, and keeps `pytest` green.
- **Person 4** also owns Git hygiene, the demo script, the backup recording and the QR code slide.

---

## 7. Commands cheat sheet

### Backend
```powershell
.venv\Scripts\activate
pip install fastapi uvicorn
pip freeze > requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
Open `http://localhost:8000/docs` to test. `--host 0.0.0.0` lets the phone reach it.

Find your laptop's IP: `ipconfig` (look for the IPv4 address on the hotspot or Wi-Fi). Allow Python through the Windows firewall when asked.

### Frontend and Capacitor
```powershell
cd ScamLens
npm create vite@latest mobile -- --template react
cd mobile
npm install
npm install @capacitor/core @capacitor/clipboard
npm install -D @capacitor/cli
npm install @capacitor/android
npx cap init ScamLens com.team.scamlens --web-dir=dist
npm run build
npx cap add android
npx cap sync
npx cap open android
```
After every code change: `npm run build`, then `npx cap sync`, then run again from Android Studio.

### During development
- Develop the UI in the browser with `npm run dev` (fast), and only rebuild for the phone when needed.
- Put the backend URL in one config constant, so switching between laptop IP and a deployed URL is a one-line change.
- If Android blocks plain HTTP calls to your laptop, set `"server": { "cleartext": true }` in `capacitor.config.json`. If it is still blocked, add `android:usesCleartextTraffic="true"` to the `<application>` tag in `AndroidManifest.xml`.
- Phone and laptop must be on the **same network** (use the phone hotspot, since venue Wi-Fi often isolates devices).

---

## 8. Risks and fallbacks

| Risk | Fallback |
|---|---|
| Android setup problems | Use the browser "mobile view" of the React app, or the Streamlit app opened on a phone via the laptop's network URL |
| Capacitor plugin does not support our version | Skip share-to-app and SMS; paste flow only |
| Venue network blocks phone to laptop | Use phone hotspot; keep a screen recording of the app working |
| Groq limit or failure | Template fallback (already built) |
| Tamil or Hindi text wrong | Native speaker reviews all fixed UI text; do not claim languages we did not test |
| Running out of time | Cut in this order: SMS inbox, URL check, share-to-app, log tab. Never cut multilingual detection or the explanation |

---

## 9. Pitch notes

- Say **"Android app"**, and only claim features that work live.
- Say **"user-initiated checking"** or **"share to ScamLens"**, not "reads your SMS automatically".
- Explain the key safety design: the AI key is on the server, never in the app.
- Future scope: more Indian languages, on-device detection, a WhatsApp or Telegram bot, URL reputation checks, a classifier trained on public multilingual data.
- Show a QR code or a live phone demo, plus the Streamlit app as the backup.

---

## 10. Definition of done (for the demo)

- [ ] Hindi, Tamil, English and romanised scam samples are flagged correctly; normal messages stay Low
- [ ] Explanation appears in the selected language; fallback works with the internet off
- [ ] Phone app (or browser mobile view) shows the full result screen
- [ ] The demo path takes under 90 seconds
- [ ] Backup screen recording and screenshots saved on the second laptop
- [ ] `git tag demo-ready` pushed; project zip on a USB drive
- [ ] Everyone can run and explain the app
