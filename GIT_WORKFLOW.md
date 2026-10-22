# Git and GitHub Workflow (Hackathon Edition)

For a 24-hour hackathon with four beginners, we **work directly on `main` with a strict routine**. Branches and pull requests are good practice, but they add steps that beginners often get stuck on mid-event. Since each person owns different files, collisions will be rare.

---

## 1. One-time setup (everyone)

```powershell
git config --global pull.rebase true
git config --global core.editor "code --wait"
```
- The first line stops Git from creating messy "merge commits" when you pull.
- The second makes the commit message editor open in VS Code instead of Vim. If you don't use VS Code, skip it and always commit with `-m "message"`.

---

## 2. The routine (after every small working piece)

```powershell
git add .
git commit -m "short note on what you did"
git pull
git push
```
Order matters: **commit, then pull, then push.** Do this every 20-30 minutes, not once at the end.

After a break, or before you start working:
```powershell
git pull
```

---

## 3. Rules

1. **Own your files.**
   | Person | Files |
   |---|---|
   | 1: Detection and AI | `detector.py`, `explainer.py` |
   | 2: Interface | `app.py` |
   | 3: Testing and research | `test_cases.py`, CSV files |
   | 4: Integration and pitch | docs, README, merging |
   Ask in the group chat before editing someone else's file.
2. **Never push code that breaks the app.** Run `streamlit run app.py` before pushing.
3. **Small commits, clear messages**: "add urgency rule", not "changes".
4. **Never commit `.env` or `.venv`.** Check with `git status` before `git add .`.
5. **Announce big changes** in the group chat ("pushed new app.py, please pull").

---

## 4. If `git push` is rejected

Someone pushed before you:
```powershell
git pull
git push
```

---

## 5. If you get a merge conflict

It happens when two people edit the same lines. Git pauses and marks the file:
```
<<<<<<< HEAD
their version
=======
your version
>>>>>>> your commit
```
1. Open the file in VS Code. Click **Accept Current**, **Accept Incoming** or **Accept Both**, or edit manually. Make sure all the `<<<<<<<`, `=======`, `>>>>>>>` markers are gone.
2. Then:
```powershell
git add .
git rebase --continue
git push
```
If it gets confusing: `git rebase --abort` returns you to where you were. Then ask a teammate.

---

## 6. When to use a branch (optional)

Use a branch only for **risky experiments** (for example, a new ML model that might break the app):
```powershell
git checkout -b experiment-ml
git push -u origin experiment-ml
```
If it works:
```powershell
git checkout main
git pull
git merge experiment-ml
git push
```
If it fails, return with `git checkout main` and ignore the branch.

---

## 7. Safety commands

| Situation | Command |
|---|---|
| See what changed | `git status` |
| See recent history | `git log --oneline -10` |
| Undo uncommitted edits to one file | `git restore app.py` |
| Unstage a file (before commit) | `git restore --staged filename` |
| Save half-done work, get a clean state | `git stash` (restore with `git stash pop`) |
| Check you are in sync with GitHub | `git status` should say "up to date with origin/main" |

**Avoid** `git reset --hard` and `git push --force`: they can delete teammates' work.

---

## 8. Demo-safe checkpoint

When the demo works (a few hours before judging), tag it:
```powershell
git tag demo-ready
git push --tags
```
If anything breaks later, anyone can get back to the working version:
```powershell
git checkout demo-ready
```
Return to normal work with `git checkout main`. After tagging: **bug fixes only, no new features.**

---

## 9. Final hour

- **Person 4** is the only one who pushes. Others send changes to them, or announce before pushing.
- Everyone runs `git pull` and tests the app on their own laptop.
- Keep an updated zip of the project on a USB drive or phone.

---

## 10. Quick reference (paste in the team chat)

```
GIT RULES
1. Work on main. Own your files.
2. Every 20-30 min: git add . > git commit -m "msg" > git pull > git push
3. Run the app before pushing.
4. Push rejected? git pull, then git push.
5. Never commit .env or .venv.
6. Last 2 hours: bug fixes only. Tag: git tag demo-ready
```
