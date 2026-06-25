# Python for CCA-F — AJA Tutorial

Tutorial for the **AI Jedi Academy** cohort preparing for the **Claude Certified Architect —
Foundations (CCA-F)** exam. Teaches the Python needed to read Skilljar course code, using a
**10-book advertising knowledge assistant** as the running example.

> **Private consulting deliverable.** Built for Don Ranns and his company — not for public
> release. The publishable product line lives in
> [`../advertising_systems_tutorial_legacy/`](../advertising_systems_tutorial_legacy/).

**Source brief:** `Python_for_CCA-F_Teaching_Brief.docx`

**Build plan:** [`md/TUTORIAL_IMPLEMENTATION_PLAN.md`](md/TUTORIAL_IMPLEMENTATION_PLAN.md)

---

## How to read the tutorial (most people — start here)

**You do not need Python, a venv, or `build_reader.py` to read this tutorial.**

This repo ships with a **pre-built `index.html`** at the project root. It already contains every
chapter, visual explainer, and the foundation quiz — fully offline, no server required.

### Just open it

| OS | What to do |
|----|------------|
| **Any** | **Double-click `index.html`** (or drag it into Chrome / Edge / Firefox / Safari) |

That is the entire setup for reading. Clone or unzip the repo, open `index.html`, done.

> **Mermaid diagrams:** when you open `index.html` directly (`file://`), some browsers cannot
> load the Mermaid CDN and a few flow diagrams may show as plain text. **All prose, code, quiz,
> and HTML explainers work.** If you need every diagram rendered, use a local server below.

> **If anything else fails** (Windows admin prompt, port blocked, no Python): **still just double-click
> `index.html`.** The pre-built file from git is complete.

---

## Share on Wi-Fi (optional — local server)

Use a server only when you want a **"Share on Wi-Fi" link** for phones/tablets on the same
network, or to demo HTTP live (Foundation doc). **Reading on your own machine does not require this.**

| OS | Command | Notes |
|----|---------|-------|
| **Windows** | double-click **`serve.bat`** (quiet) or **`serve-log.bat`** (demo — prints each request) | May ask for Administrator permission to open a network port |
| **macOS / Linux / WSL** | `./build_and_serve.sh` | Serves the pre-built `index.html`; requests log to the terminal |

### Windows: Administrator / security blocked the server?

`serve.bat` may open a **"Do you want to allow this app to make changes?"** (UAC) prompt. That is
normal — it needs permission to listen on your network.

**If you click No, or Windows blocks it:**

1. **You do not need the server.** Double-click **`index.html`** — same tutorial, no admin, no port.
2. To try the server again: right-click **`serve.bat`** → **Run as administrator**, then click **Yes**.
3. If SmartScreen or your org blocks PowerShell scripts: open **`index.html`** directly (always works),
   or run from a normal PowerShell window:
   ```powershell
   powershell -ExecutionPolicy Bypass -File serve.ps1
   ```
4. Still stuck? **`index.html`** is the workaround. Nothing is missing from the pre-built file.

---

## Edit the tutorial (authors only — rebuild `index.html`)

**Learners can skip this entire section.**

`index.html` is generated from `md/` + `html/` by `build_reader.py`. You only need to rebuild if
**you changed** a markdown module or HTML explainer and want those edits in the reader.

```bash
source setup_venv.sh          # once — creates named venv, installs markdown
python build_reader.py        # writes index.html
```

Or on macOS/Linux/WSL, build and serve in one step:

```bash
chmod +x build_and_serve.sh   # once, if needed
./build_and_serve.sh --build  # rebuild, then serve on :8000
./build_and_serve.sh          # serve only (no rebuild) — same as git's index.html
```

| OS / shell | One-time venv setup |
|------------|---------------------|
| **macOS / Linux / WSL** | `source setup_venv.sh` |
| **Windows (PowerShell)** | `. .\setup_venv.ps1` |

> **WSL:** if the project is on `/mnt/c/...`, `setup_venv.sh` puts the venv on `~/venvs/aja-cca-f`
> (fast native storage). Building a venv on `/mnt/c` can take *45 minutes*; off the bridge it's seconds.

---

## Run the code examples (optional — Modules 3–8)

Reading the tutorial needs **no installs**. Running live RAG / agent / MCP examples needs the venv
plus API keys:

```bash
source setup_venv.sh                              # or . .\setup_venv.ps1 on Windows
cp .env.example .env                              # add ANTHROPIC_API_KEY

python code/rag/advertising_knowledge.py "fair use in ad copy"
python code/mcp/server.py
python code/loop/tartaurus/run_advertising_rag.py --dry-run
python code/schemas/bayesian_loop.py
```

Dependencies: `requirements.txt` — `markdown` (build only), `anthropic` + `mcp` (live code runs).

---

## Modules

| # | File | Topic |
|---|------|-------|
| — | [`md/FOUNDATION_FOR_AI_SYSTEMS.md`](md/FOUNDATION_FOR_AI_SYSTEMS.md) | **Read first** — AI systems foundation |
| — | [`md/FOUNDATION_COMPUTER_ENGINEERING.md`](md/FOUNDATION_COMPUTER_ENGINEERING.md) | **Session 1** — ports, daemons, kernel, storage, networking |
| Q | Foundation quiz (in `index.html`) | Self-check — both foundation docs |
| 00 | `md/00_OVERVIEW_AND_RUNNING_EXAMPLE.md` | Reframe + 10-book RAG intro |
| 01–08 | `md/01_…` through `md/08_…` | Python modules + integration |

---

## Layout

```
README.md              # you are here
index.html             # ← OPEN THIS (pre-built, ships in git)
build_and_serve.sh     # macOS/Linux/WSL: serve (optional --build)
serve.bat              # Windows: serve (optional)
md/                    # source prose (authors edit these)
html/                  # visual explainers
build_reader.py        # authors only: md/ + html/ → index.html
code/                  # runnable examples (optional)
```

## Legacy

Prior advertising-systems engineering tutorial:
[`../advertising_systems_tutorial_legacy/`](../advertising_systems_tutorial_legacy/)
