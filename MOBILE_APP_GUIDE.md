# ScamLens Mobile App Guide (React + Capacitor + Backend)

How to turn ScamLens into an Android app, what is realistic in a hackathon, and the order to build it.

---

## 1. Reality check (read this first)

- **There is no API key or SDK that fetches a user's messages.** On Android, reading the SMS inbox needs the `READ_SMS` permission and native code. In Capacitor that means a community plugin or a small custom plugin. Check each plugin's repo for support of your Capacitor version before relying on it.
- **iOS does not allow reading SMS at all.** The mobile demo would be Android only.
- **Google Play restricts SMS permissions heavily.** Fine for a sideloaded APK at a hackathon. In the pitch, say "user-initiated" checking, not "automatic scanning".
- **Never put the Groq key inside the app.** An APK can be unpacked and the key extracted. The key lives only on the backend server.
- **Setup is the big time sink.** Android Studio, JDK, Android SDK and USB debugging can take 1-2 hours for a first-timer, with a real chance of environment problems.

---

## 2. Architecture

```
React app (Capacitor, Android)
   |  gets text from: paste / clipboard / share-to-app / SMS inbox
   v
Backend (Node + Express, or FastAPI)
   |-- rule engine (multilingual)
   |-- Groq API (key stays here)
   ^
   +-- returns: score, level, evidence spans, explanation, next steps
```

### Backend choice

| Option | Pros | Cons |
|---|---|---|
| **FastAPI wrapping the existing Python code** (recommended) | Reuses `detector.py` and `explainer.py` and the tests; no duplicate logic | Team needs a little FastAPI |
| **Node + Express with rules ported to JS** | One language (JS) across the whole stack | About an hour to port regex rules; two code bases to keep in sync |

---

## 3. Build order (finish each step before the next)

### Step 1: Backend API (about 1 hour)
- One endpoint: `POST /analyze` with body `{ "text": "...", "language": "en" }`.
- Response: `{ score, level, findings[], explanation, nextSteps }`, where each finding has `rule`, `severity`, `why`, and `evidence` (with `start` and `end` positions).
- Enable CORS so the app can call it.
- Test with Postman or the browser before touching the app.
- For the demo, run it on your laptop and connect over your phone hotspot. Deploy only if time allows.

### Step 2: React web UI (about 1.5 hours)
- Scaffold: `npm create vite@latest` (React template).
- One screen: text box, Analyze button, risk meter, highlighted text, explanation, and a "Do this now" card.
- Highlighting: split the text at the evidence `start` and `end` positions and wrap matches in `<mark>`.
- Mobile first: single column, large buttons, viewport meta tag.
- Test in Chrome's phone view before wrapping it.

### Step 3: Wrap with Capacitor (1-2 hours)
```
npm install @capacitor/core @capacitor/cli @capacitor/android
npx cap init
npm run build
npx cap add android
npx cap sync
npx cap open android
```
- Run from Android Studio onto a real phone (USB debugging) or an emulator.
- Inside the app, `localhost` is the phone itself. Use your laptop's hotspot IP for the backend URL (for example `http://192.168.x.x:8000`), and allow cleartext HTTP for development.

### Step 4: Getting messages in (in order of reliability)

| Method | How | Reliability |
|---|---|---|
| **Paste / clipboard** | `@capacitor/clipboard` (official) with a "Paste message" button | High. Do this first |
| **Share to ScamLens** | The user long-presses a message, taps Share, picks ScamLens. Needs an Android intent filter, usually via a community "send intent" plugin | Medium. Most credible real-world flow, no SMS permission needed |
| **SMS inbox reading** | Request `READ_SMS` at runtime, list recent messages with a "Check" button on each | Low. Stretch goal only. May need a custom Java or Kotlin plugin |

### Step 5: Polish
App name and icon, loading state, offline message, language selector, and an error screen when the backend cannot be reached.

---

## 4. Feasibility and recommended plan

A first-time team doing backend, React, Capacitor and SMS access alongside the idea document, PPT and poster is high risk. The Android setup alone can swallow an afternoon, and none of it improves detection quality, which is what judges score.

Recommended split:
1. **Two people** keep building the Streamlit version (multilingual detection). This is the guaranteed demo.
2. **One or two people** build the mobile version in the order above, with a time limit. If the APK is not running on a phone by the halfway point, drop it.
3. In the pitch, call the mobile app "working" only if it runs on a phone. Otherwise present it as: "Next step: Android app with Share to ScamLens".

---

## 5. Privacy talking points

Judges may ask about sending SMS to a cloud AI. Suggested answers:
- Rules run first, and the user chooses which message to send.
- Nothing is stored.
- The API key stays on the server, never in the app.
- Future work: on-device processing for sensitive messages.

---

## 6. Checklist

- [ ] Backend `/analyze` returns correct results for English, Hindi and Tamil samples
- [ ] React screen works in Chrome's phone view
- [ ] APK runs on a real phone over the hotspot
- [ ] Paste / clipboard flow works
- [ ] (Optional) Share-to-app flow works
- [ ] Backup: the Streamlit version still works on the second laptop
- [ ] Groq key is only on the backend, and `.env` is not committed

---

## 7. Open decision

Backend: **FastAPI reusing Python code** (recommended) or **Node with ported rules**. Decide this first, then start Step 1.
