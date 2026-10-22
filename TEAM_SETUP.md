# Team Setup Guide (Windows, PowerShell)

Everything from "I have nothing installed" to "I can push code".
Part A is done ONCE by the repo owner. Part B is done by EVERY teammate.

---

## Part A: Repo owner (once)

### A1. Install Git
Download from https://git-scm.com/download/win, install with default options.
Close and reopen PowerShell, then check:
```powershell
git --version
```

### A2. Tell Git who you are (only once per laptop)
```powershell
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
```

### A3. Create the repository on GitHub
1. Log in at github.com, click **+** (top right) > **New repository**.
2. Name: `ScamLens` (any name is fine, no spaces is easier).
3. Choose **Private**. Do NOT tick "Add README" or ".gitignore" (your folder already has them).
4. Click **Create repository**. Copy the URL shown, like
   `https://github.com/yourname/ScamLens.git`.

### A4. Upload your existing project
In PowerShell, go to your project folder:
```powershell
cd "D:\Programing\Innohack 2026"
git init
git add .
git status
```
Look at the list. You should see `app.py`, `detector.py` etc. You must NOT see `.venv` or `.env`. If you do, your `.gitignore` is wrong: stop and fix it first.

Then:
```powershell
git commit -m "Initial ScamLens starter"
git branch -M main
git remote add origin https://github.com/yourname/ScamLens.git
git push -u origin main
```
A browser window will ask you to log in to GitHub the first time. Approve it.
Refresh the GitHub page: your files should be there.

### A5. Invite teammates
1. On the repo page: **Settings** > **Collaborators** > **Add people**.
2. Type each teammate's GitHub username or email > **Add**.
3. Tell them to check their email (or github.com/notifications) and **accept the invite**.
Without accepting, they cannot push.

---

## Part B: Every teammate (once)

### B1. Create a GitHub account
Sign up at github.com (free). Send your **username** to the repo owner.

### B2. Install the tools
- **Python 3.12** from python.org. On the first screen tick **"Add python.exe to PATH"**.
- **Git** from git-scm.com (default options).
- **VS Code** (optional but recommended) from code.visualstudio.com.
Close and reopen PowerShell afterwards.

### B3. Accept the invite
Open the invitation email from GitHub and click **Accept invitation**.

### B4. Set your Git identity
```powershell
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
```

### B5. Clone the project
Pick a folder (avoid OneDrive-synced folders), then:
```powershell
cd D:\
git clone https://github.com/yourname/ScamLens.git
cd ScamLens
```
A browser window opens to log in the first time. This downloads the full project AND its entire history to your laptop.

### B6. Create your own virtual environment
Libraries are not stored in Git. Everyone builds their own `.venv`:
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
If `python` is not found, use the full path:
`& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv`

If activate says scripts are disabled, run once:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### B7. Create your own `.env`
The key file never goes through Git. Copy the example:
```powershell
copy .env.example .env
```
Open `.env` and replace `paste-your-key-here` with your Groq key (no quotes, no spaces).

### B8. Run it
```powershell
streamlit run app.py
python check_ai.py
pytest
```
If the app opens in your browser, you are ready.

---

## Part C: Daily workflow (everyone, every time)

Golden rule: **pull before you start, push when you finish a piece.**

```powershell
.venv\Scripts\activate
git pull
git checkout -b yourname-feature
git add .
git commit -m "short message about what you did"
git push -u origin yourname-feature
```
Then on GitHub click **Compare & pull request** > **Create pull request** > **Merge pull request**. Everyone else runs:
```powershell
git checkout main
git pull
```

Fast-and-simple alternative (if branches feel like too much): everyone commits to `main`, but always run `git pull` right before `git push`.

### Rules that prevent disasters
- Each person edits mostly their own file(s): Person 1 `detector.py`/`explainer.py`, Person 2 `app.py`, Person 3 `test_cases.py`, Person 4 `README.md` and merging.
- Tell the team before editing someone else's file.
- Commit small and often.
- Never commit `.env`, `.venv`, or API keys.

### If you get a merge conflict
Git marks the file with `<<<<<<<`, `=======`, `>>>>>>>`. Open the file, keep the correct lines, delete the markers, then:
```powershell
git add .
git commit -m "resolve conflict"
```
Ask a teammate before deleting anything you are unsure about.

### If you committed a secret by mistake
Tell the team and **create a new key** in the Groq console (the old one is now unsafe). Deleting the file later does not remove it from history.

---

## Part D: Offline and bad Wi-Fi

Your clone is a full copy, so offline you can still: `git status`, `git log`, `git branch`, `git checkout`, `git commit`, `git diff`.
You need internet only for: `git clone`, `git pull`, `git push`.
Offline, keep committing. When the connection returns: `git pull`, then `git push`.

Before the event:
- Everyone has a working `.venv` that runs the app (do not delete it).
- One person zips the whole project folder and keeps it on a USB drive or phone.
- Optional: download libraries for offline install:
  ```powershell
  pip download -r requirements.txt -d wheels
  pip install --no-index --find-links=wheels -r requirements.txt
  ```
  (Works only for the same Python version and OS.)
- Phone hotspot as backup internet.

---

## Part E: Common errors

| Problem | Fix |
|---|---|
| `git` not recognized | Reinstall Git, reopen PowerShell |
| `Permission denied` / `403` on push | Invite not accepted, or logged in to the wrong GitHub account |
| `Authentication failed` | Sign in again via the browser popup, or create a Personal Access Token (GitHub > Settings > Developer settings) and use it as the password |
| `rejected ... non-fast-forward` | Someone pushed first: run `git pull`, then push again |
| `python` not recognized | See B6 full-path command |
| `ModuleNotFoundError` | Activate `.venv`, then `pip install -r requirements.txt` |
| App says "by template" | Check `.env` is in the same folder as `app.py`, named exactly `.env`; run `python check_ai.py` |
| `.env` or `.venv` shows up in `git status` | They must be in `.gitignore`; run `git rm -r --cached .venv` then commit |
