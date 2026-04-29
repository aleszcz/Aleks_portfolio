# Install Claude Code on Windows

> Claude Code is an AI assistant that lives in your terminal — it writes, debugs, and explains code. This guide covers both a quick native install and the recommended WSL2 setup for the full experience.

---

## What You'll Need

- Windows 10 (version 2004+) or Windows 11
- Administrator access
- A Claude Pro/Max subscription, Anthropic API key, or Azure Foundry access
- 10–15 minutes

---

## Key Concepts

| Term | What It Means |
|------|---------------|
| **WSL** | Windows Subsystem for Linux — runs a real Linux system alongside Windows |
| **Ubuntu** | A beginner-friendly Linux distribution, installed through WSL |
| **PowerShell** | Windows' built-in command-line tool, used to kick off the install |

---

## Option A: Native Windows Install (quick but limited)

Open PowerShell and run:

```powershell
irm https://claude.ai/install.ps1 | iex
```

Verify it worked:

```powershell
claude --version
```

**Limitations of native install:**
- No Bash tool sandboxing (a security feature only available in WSL2/macOS)
- Some tools and workflows work better in a Linux environment

The steps below set up WSL2 for the full experience.

---

## Recommended: WSL2 Install

### Step 1 — Check Virtualization

Open Task Manager → **Performance** tab → **CPU** → look for **Virtualization: Enabled**.

If it says **Disabled**, you'll need to enable it in your BIOS:
1. Restart and press your BIOS key (usually `F2`, `F10`, `Del`, or `Esc`)
2. Find "Virtualization Technology", "Intel VT-x", "AMD-V", or "SVM Mode"
3. Enable it, save (`F10`), and restart

### Step 2 — Install WSL and Ubuntu

Open PowerShell **as Administrator** and check if WSL is already installed:

```powershell
wsl --list --verbose
```

If Ubuntu is listed, skip to Step 3. Otherwise, install it:

```powershell
wsl --install
```

Restart your computer when prompted.

### Step 3 — Set Up Ubuntu

After restarting, an Ubuntu terminal should open automatically (wait 2–5 minutes). If it doesn't, open it manually from the Start menu.

Complete first-time setup:
1. Enter a username (lowercase, no spaces — e.g. `john`)
2. Enter a password (you won't see characters as you type — this is normal)
3. Confirm the password

**Remember these credentials — you'll need them later.**

### Step 4 — Install Claude Code in WSL

In the Ubuntu terminal:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Verify:

```bash
claude --version
```

---

## Connect to Your Account

Choose one of the options below.

### Option A — Claude Pro or Max Subscription

```bash
claude
```

Claude will try to open a browser. If it can't, hold `Ctrl` and click the URL, or copy-paste it manually. Log in, click **Authorize**, copy the code, and paste it back in the terminal (`Ctrl+Shift+V` or right-click → Paste).

### Option B — Anthropic API Key

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

To make it permanent:

```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
```

Reopen the terminal for the change to take effect.

### Option C — OpenRouter (free tier available)

Sign up at [openrouter.ai](https://openrouter.ai), get an API key, then:

```bash
export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
export ANTHROPIC_AUTH_TOKEN="your-openrouter-api-key"
export ANTHROPIC_API_KEY=""
export ANTHROPIC_DEFAULT_SONNET_MODEL="openai/gpt-5.1-codex-max"
export ANTHROPIC_DEFAULT_OPUS_MODEL="openai/gpt-5.2-pro"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="minimax/minimax-m2:exacto"
```

Start Claude Code and verify with `/status`. Free tier includes 50 API requests/day. Browse models at [openrouter.ai/models](https://openrouter.ai/models).

### Option D — Azure Foundry

```bash
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE=xxxx-eastus2        # your resource name, not the full URL
export ANTHROPIC_DEFAULT_OPUS_MODEL=claude-opus-4-5
export ANTHROPIC_DEFAULT_SONNET_MODEL=claude-sonnet-4-5
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-4-5
export ANTHROPIC_FOUNDRY_API_KEY=your_api_key
```

Then run `claude`.

---

## Navigating to Your Projects

**In WSL (Ubuntu):**
```bash
cd /mnt/c/Users/YOUR_USERNAME/Documents/your-project
claude
```

**In native PowerShell:**
```powershell
cd ~/Documents/your-project
claude
```

Claude operates inside a project folder and stores its settings there. Start by asking it to explain the codebase.

---

## Updating Claude Code

**WSL:**
```bash
sudo claude update
```

**Native Windows (PowerShell as Administrator):**
```powershell
claude update
```

---

## Troubleshooting

**Start here:** run `claude doctor` — it checks your installation and reports common issues.

| Problem | Fix |
|---------|-----|
| `claude` not found (Windows) | Reopen PowerShell and re-run the install script |
| "Virtual Machine Platform" error | Virtualization is disabled — enable it in BIOS (see Step 1) |
| `wsl --install` doesn't work | Run PowerShell as Administrator; confirm Windows 10 v2004+ or Win 11 |
| Ubuntu didn't open after restart | Start menu → type **Ubuntu** → click the orange icon |
| Claude commands not found (WSL) | Close and reopen the terminal; re-run the `curl` install command |

**Further help:**
- WSL issues: [Microsoft WSL Documentation](https://learn.microsoft.com/en-us/windows/wsl/)
- Claude Code issues: [Claude Code GitHub](https://github.com/anthropics/claude-code)
