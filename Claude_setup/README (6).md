# Claude Code with Version Control for Windows

> Use AI to write code and Git to save your progress. Every working version is preserved — discard mistakes fearlessly.

---

## What This Is

Claude Code writes and fixes your code. Git acts as an undo button for your entire project — every time you save a snapshot (called a **commit**), you create a restore point you can always return to. Everything runs locally on your computer.

---

## Key Concepts

| Term | What It Means |
|------|---------------|
| **WSL** | Windows Subsystem for Linux — runs Linux tools like Git natively on Windows |
| **Git** | Tracks every change to your files, creating restore points you can return to anytime |
| **Commit** | A snapshot of your project at a specific point in time, with a description of what changed |
| **Claude Code** | AI coding assistant that writes code, fixes bugs, and handles Git through simple requests |

---

## Prerequisites

- Claude Code installed on Windows
- WSL and Ubuntu installed
- ~20 minutes

---

## Setup (One Time)

### 1. Open Ubuntu Terminal

Start menu → type **Ubuntu** → open it. You'll see a prompt ending with `$`.

### 2. Install Git

```bash
sudo apt-get install git
```

Verify it worked:

```bash
git --version
# Expected: git version 2.34.1 (or similar)
```

### 3. Configure Your Identity

Git needs a name and email for commit messages (can be anything):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 4. Navigate to Your Windows Files

WSL accesses Windows files through `/mnt/c/`:

```bash
cd /mnt/c/Users/YOUR_USERNAME/Documents
```

### 5. Create a Project Folder

```bash
mkdir test_claude
cd test_claude
```

### 6. Start Claude Code

```bash
claude
```

---

## The Core Workflow

```
Make a change → Test it → Works? Commit it. Broken? Fix or discard.
```

### Useful things to say to Claude Code

| What you want | What to say |
|--------------|-------------|
| Start tracking changes | `Start tracking changes` |
| Save your progress | `Save these changes` |
| Throw away bad changes | `Discard these changes` |
| See your save history | `Show my change history` |
| See what changed | `Show me the diff` |
| Undo everything since last save | `Go back to the previous commit` |
| Understand the code | `Explain this code. Just big picture.` |

---

## Walkthrough: Building a Timer App

Follow these steps to practice the workflow end-to-end.

**Step 1 — Initialize Git**
```
Start tracking changes
```

**Step 2 — Build the app**
```
Create a simple countdown timer app in a single file called timer.html. It should have:
- An input field to set minutes
- Start and Stop buttons
- Display showing time remaining in MM:SS format
```

Open `Documents\test_claude\timer.html` in your browser and test it.

**Step 3 — Commit the working version**
```
Save these changes
```

**Step 4 — Add preset buttons**
```
Add two buttons on the top. If I click on them it automatically starts 1- and 5-minute timers.
```

Test → commit if it works.

**Step 5 — Practice discarding bad changes**
```
Add a 15-minute button.
```

Pretend it doesn't work. Instead of committing:
```
Discard these changes
```

Confirm when prompted. The bad change disappears; your last commit is restored.

**Step 6 — Add a sound notification**
```
Add a sound notification when the timer reaches zero.
```

Test → commit if it works.

**Step 7 — Add a snooze button**
```
The sound should continue until I click a button to snooze it.
```

Test → commit if it works.

**Step 8 — View your history**
```
Show my change history
```

You'll see every commit — and notice the discarded 15-minute button is nowhere in it.

---

## Troubleshooting

**"not a git repository" error**
You're in the wrong folder. Run:
```bash
cd /mnt/c/Users/YOUR_USERNAME/Documents/test_claude
```

**Can't find timer.html in Windows Explorer**
Look at: `C:\Users\YOUR_USERNAME\Documents\test_claude\timer.html`

**Git asks for a password**
You mistyped your `sudo` password — try again.

**Timer doesn't work in the browser**
Right-click the page → Inspect → Console tab. Copy any red error messages and paste them to Claude Code.

---

## Next Feature Ideas

Once you're comfortable with the workflow, try adding:

- ✅ A working 15-minute preset button (redo what you discarded!)
- ⏸ A Pause/Resume toggle button
- 🎨 A modern color scheme and larger fonts
- 📊 A visual progress bar showing time remaining

**Rule of thumb:** Test after each feature. Commit after each success. Discard failures. Repeat.
