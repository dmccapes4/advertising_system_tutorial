# Foundation for Computer Engineering

**Read this in Session 1, right after `FOUNDATION_FOR_AI_SYSTEMS.md`.** That document said a
**system** is *a service that persists user data* and that its first job is to *manage data
honestly*. This document is the **machine underneath** that idea: what actually runs, where the
bytes live, how a request gets in, and how one box becomes many.

> **Goal: exposure, not mastery.** You are not expected to retain all of this. You are expected
> to stop being surprised by the words — *port, daemon, kernel, VRAM, NAT, SSE* — when they show
> up in our advertising system, in Skilljar, or in a teammate's sentence. Read it once. It will
> click later when you see it live.

We hang everything on **three things you will actually run**:

1. **The tutorial's own `serve` script** — ports, daemons, the kernel, and networking.
2. **Postgres** — a long-running service that guards data on disk.
3. **Ollama** — a long-running service that loads an AI model into fast memory.

---

## Part 1 · The machine: kernel, daemons, ports, storage

### The kernel — the boss of the hardware

Your computer has one program in charge of the hardware: the **kernel** (the core of the
operating system — Linux, macOS, Windows). Normal programs do **not** touch the disk, the
network card, or memory chips directly. They **ask the kernel**, and the kernel grants or
denies the request. Think of the kernel as the building manager: you don't run your own
plumbing, you file a request and the manager allocates it.

Every example below is, underneath, **a program asking the kernel for something**:

- Postgres asks: *"give me a network port, and let me read and write these files on disk."*
- Ollama asks: *"give me a network port, and reserve a big block of fast memory for a model."*
- The tutorial server asks: *"give me a network port so browsers can reach me."*

### Daemons — programs that stay running and listen

A **daemon** is a program that does not finish and exit — it **keeps running in the background
and waits for requests**. (On Windows the same idea is called a *service*.) A web server, a
database, and Ollama are all daemons: you start them once and they sit there, listening, until
you stop them.

Contrast with a **script** (Module 3, "run the file"): a script runs top-to-bottom and exits.
A daemon is a script that, instead of exiting, enters a loop and waits for connections forever.

### Ports — numbered doors into a machine

A machine has **one address** but thousands of numbered **ports** (doors). A daemon "**listens
on**" a port, and only **one** daemon can own a given port at a time. When traffic arrives for
port 5432, the kernel routes it to whichever daemon claimed 5432.

You will memorize a few by sheer repetition:

| Port | Who listens | In this tutorial |
|------|-------------|------------------|
| `8000` | the tutorial web server | `serve` script |
| `5432` | PostgreSQL | our knowledge database |
| `11434` | Ollama | our local model server |
| `80` / `443` | web servers (HTTP / HTTPS) | the public internet |

"Register a port, then listen on it" is the **first move of every daemon** in this document.

### Storage: three tiers, fast to slow, small to big

Where do the bytes live? Three places, and the trade-off is always **speed vs. size vs.
"does it survive a reboot?"**

| Tier | Survives reboot? | Speed | Size (typical) | What lives here |
|------|------------------|-------|----------------|------------------|
| **Disk** (SSD/HDD) | ✅ persistent | slowest | huge (TBs) | the database files, the books, your `.env` |
| **RAM** (system memory) | ❌ wiped on reboot | fast | medium (8–128 GB) | running programs, query working sets |
| **VRAM** (GPU memory) | ❌ wiped | fastest | small (8–192 GB) | AI model weights during inference |

The whole game of running AI locally is: **the model lives on disk (persistent), but to *think*
it must be loaded into VRAM (fast)**. Postgres is the opposite emphasis: its job is to keep data
**safely on disk** and pull pieces into RAM as needed.

### Why VRAM is fast — and what GPUs are good at

Plain version, corrected to be accurate:

- A GPU's speed advantage is mostly **memory bandwidth**, not lower latency. VRAM sits on a very
  **wide bus** with many memory channels, so thousands of GPU cores can be **fed data in
  parallel**. System RAM has a narrower path to the CPU's handful of cores. So "parallel access"
  is the right intuition: *many cores reading and writing many locations at once.*
- GPUs are specialized for **matrix math** — doing the **same operation on huge batches of
  numbers at the same time** (this is called SIMD: *single instruction, multiple data*). Modern
  GPUs add **tensor cores** that accelerate matrix-multiply specifically.
- Why this matters for AI: a model's **weights are matrices**, and inference is **matrix
  multiplication** (Foundation doc: "the magic is in the parameters"). So you put the weight
  matrices in VRAM, right next to the thousands of cores built to multiply matrices, kept fed by
  a wide-bandwidth bus. That is why a model "runs on the GPU."

One nuance to keep honest: a *single* VRAM read is not magically faster than a single RAM read —
the win is **throughput** (volume per second), because you are doing thousands of reads and
multiplies at once.

### Apple Unified Memory vs. Nvidia GPUs

Two different bets on where that fast memory lives:

| | **Apple Unified Memory** (M-series) | **Nvidia discrete GPU** |
|---|-------------------------------------|--------------------------|
| Layout | **One** memory pool shared by CPU + GPU | Separate **VRAM** on the GPU card |
| Copy cost | No copy — CPU and GPU see the same bytes | Data copied across PCIe into VRAM |
| Capacity | Very large (e.g. **192 GB** on M2 Ultra) usable by the GPU | Smaller per card (e.g. 24 GB on a 4090; 80 GB on an H100) |
| Bandwidth | High, but below top datacenter cards (~800 GB/s class) | Highest at the top end (HBM, multiple TB/s) |
| Power | Very efficient | Power-hungry |
| Best at | Loading **big** models on one quiet box | Maximum raw matrix throughput; scale by adding cards |

**Takeaway for our system:** a Mac Studio with unified memory can hold a large model *and* a
small model in memory at once because the pool is huge — exactly the setup we lean on later.
A stack of Nvidia cards wins when you need raw speed and can scale horizontally.

---

## Part 2 · Example 1 — serving the tutorial (networking)

You have already met `serve.bat` / `serve.ps1`. Double-clicking it turns *this very tutorial*
into a tiny website. Watch what it actually does — it is a daemon in miniature:

1. **Asks the kernel for permission** to open a network port (on Windows it asks for admin +
   adds a firewall rule — that is the kernel guarding the network card).
2. **Registers a port** (`8000`) and starts **listening**.
3. **Loops forever**, serving files to any browser that connects — until you close the window.

```
On THIS computer :  http://localhost:8000
Share on Wi-Fi   :  http://192.168.1.37:8000
```

Two addresses for the same server. Understanding *why* is most of networking.

### localhost — the machine talking to itself

`localhost` (always `127.0.0.1`) means **this machine, to itself**. Traffic never leaves the
box. When you open `http://localhost:8000`, your browser and the server are the same computer.
This is how you talk to Postgres and Ollama too — they listen on `localhost` so only programs
on your machine can reach them.

### Device IP — your address on the local network (LAN)

`192.168.1.37` is your computer's **device IP**: its address on your home/office network (your
**LAN** — local area network). Other devices on the **same Wi-Fi** can reach you at that
address. That is the "Share on Wi-Fi" link — a phone on the same router can open the tutorial.

Device IPs almost always start with `192.168.`, `10.`, or `172.` — these are **private ranges**,
meaningful only inside your network. The wider internet cannot see them.

### Public IP — what the world sees

Your **router** has a single **public IP** assigned by your ISP (AT&T, Comcast, etc.). Every
device in your home shares that one public address to reach the internet. The world sees the
router; it does not see your individual devices.

### NAT — how one public IP serves many devices

**NAT = Network Address Translation.** Your router keeps a table. When your laptop
(`192.168.1.37`) requests a web page, the router rewrites the outgoing packet to use the
**public IP**, remembers "this conversation belongs to `192.168.1.37`," and when the reply comes
back it translates the address back and hands it to your laptop. One public IP, many private
devices, kept straight by the NAT table.

Crucial consequence: NAT handles **replies to conversations your devices started**. It does
**not** know what to do with **unsolicited** traffic arriving from the internet — there is no
table entry for it, so by default the router drops it. That is a free firewall. It is also why
the next step exists.

### Port forwarding — letting the outside in (on purpose)

To make a server on your machine reachable from the **public internet** (not just your Wi-Fi),
you add a **port-forwarding rule** on the router: *"any traffic arriving on public port 8000,
send it to `192.168.1.37` port 8000."* You are manually creating the NAT entry that NAT would
not create on its own.

On a typical **AT&T** gateway you do this at **`http://192.168.1.254`** (the router's own device
IP). It will demand the **device access code** printed on a sticker on the gateway before it lets
you change anything.

> **Disclaimer — the access code, and not being afraid of daemons.**
>
> **Tape over the sticker.** The single highest security risk in most homes is not a
> sophisticated hacker — it is **someone snapping a photo of that access-code sticker** on the
> gateway. A guest, a contractor, a party. With that code and the router's address
> (`192.168.1.254`) they can open ports straight to your devices. Treat it like a house key:
> **put a piece of tape over the printed code.** And **only forward a port when you truly need
> to** — for something like this tutorial, prefer the LAN (Wi-Fi) link.
>
> **You don't need to be afraid of daemons. You can kill them.** A daemon is just a program that
> stays running. If one is stuck, hogging memory, or squatting on a port you want, you end it —
> nothing dramatic happens. To do that you need its **PID** (*process ID*): the number the kernel
> assigns to every running program so it can be referred to individually.
>
> - **Apple (GUI):** open **Activity Monitor**, search the process by name (e.g. `ollama`),
>   select it, and click the **✕ → Force Quit**. The PID is shown in its own column.
> - **Find what's holding a port (macOS/Linux):** `lsof -i :8000` lists the process and its PID
>   using port `8000` (`lsof` = "list open files"; on Unix a network port counts as an open file).
> - **Kill it politely:** `kill <pid>` sends a "please shut down" signal so the program can clean
>   up first.
> - **Kill it for real:** `kill -9 <pid>` tells the kernel to terminate it **immediately**, no
>   cleanup. Use this when a polite `kill` is ignored.
> - **Linux, find the PID by name:** `ps aux | grep ollama`, or list listening ports with
>   `ss -ltnp` (or `netstat -ltnp`).
> - **Windows (this tutorial's `serve`):** `netstat -ano | findstr :8000` shows the PID, then
>   `taskkill /PID <pid> /F` force-ends it.

### Where the tutorial server fits the Foundation definition

It is the smallest possible **System** (from `FOUNDATION_FOR_AI_SYSTEMS.md`): it holds state
(the files), listens on a port, and answers requests. Postgres and Ollama are the same shape
with bigger jobs.

> **Disclaimer — HTTP vs HTTPS, and IPv4 vs IPv6.** Two pairs of words you will see constantly.
>
> **HTTP vs HTTPS.** Same conversation (Part 5), but **HTTPS is encrypted** — a lock between you
> and the server so nobody on the wire can read or tamper with it (the padlock in the browser).
> Plain `http://` is fine for `localhost` and the LAN link in this tutorial (the traffic never
> leaves your network); anything crossing the public internet should be `https://`.
>
> **IPv4 vs IPv6.** IPv4 addresses look like `192.168.1.37` — four numbers, ~4 billion total,
> and the world ran out of them (that scarcity is *why* NAT exists). IPv6 is the bigger
> replacement and looks like `2601:0db8:85a3::8a2e:0370:7334` — effectively unlimited. You will
> see both; they name the same idea (a machine's address) at different scales.
>
> **Tools to look with (your instructor will demo these live):**
> - `ifconfig` (macOS/Linux) or `ipconfig` (Windows) — show **your own** addresses, IPv4 and
>   IPv6, per network interface. On newer Linux, `ip addr` is the modern replacement.
> - `netstat` (e.g. `netstat -an`, or `ss -tunap` on Linux) — list **active connections** and
>   which ports are listening: a live picture of every conversation your machine has open.
> - To **see IPs around the world visually** in the terminal, the tool is most likely
>   **`nexttrace`** (`nexttrace --map google.com` plots the network route on a map). Close
>   cousins: classic `traceroute` / `mtr` (the hop list those map tools are built on) and
>   `tracemap`. Any of these turns "a request leaves my machine" into a route you can watch.

---

## Part 3 · Example 2 — Postgres (a service that guards disk)

**PostgreSQL** is the database for our advertising knowledge base. Installed and started, it is
a **daemon** that:

1. **Registers port `5432`** and listens (the kernel ask: *give me this port*).
2. **Waits** for connection requests.
3. On request, **reads and writes its data files on disk** (the kernel ask: *let me touch these
   files*) and returns rows.

That is the entire shape: **register a port → daemon listens → serve requests against storage on
disk.** Postgres's specialty is doing this **safely** — it must never lose or corrupt the data it
persists (Foundation doc: *manage data honestly*).

### Connecting to it — the `DATABASE_URL`

Programs find Postgres through a **connection string**. Ours, for the medical sister-project,
looks like this:

```
DATABASE_URL=postgresql+asyncpg://2ndopinionmd@localhost:5432/2ndopinionmd
```

Read it left to right — it is just an address with parts:

| Piece | Meaning |
|-------|---------|
| `postgresql+asyncpg` | speak the Postgres protocol, using the `asyncpg` driver |
| `2ndopinionmd@` | connect **as** this database user |
| `localhost` | the daemon is on **this machine** (Part 2) |
| `5432` | on **this port** |
| `/2ndopinionmd` | use **this database** (one server can hold many) |

A different project just swaps the parts — our advertising build would use a
`postgresql+asyncpg://...@localhost:5432/advertising` style string. Same shape.

### Hidden files — where the `DATABASE_URL` lives

That line goes in a file named **`.env`**. The leading dot makes it a **hidden file** (a
"dotfile") on macOS/Linux — it does not show in a normal `ls` or Finder window; you need
`ls -a` ("all") to see it. Dotfiles are the convention for **configuration that should stay out
of the way**.

Two rules that matter (Foundation doc: honest, careful data handling):

- **`.env` holds secrets** — database URLs, API keys. It lives on your machine only.
- **`.env` is never committed to git** (it is in `.gitignore`). You commit a safe
  **`.env.example`** with blanks so teammates know *which* variables to set, never the values.

This is exactly the `.env` vs `export` distinction from Module 6 — now you know *why* the file is
hidden and why secrets live there.

---

## Part 4 · Example 3 — Ollama serve (a service that loads a brain)

**Ollama** runs AI models **locally** — on your own machine, offline, no API key. Running
`ollama serve` starts a daemon that:

1. **Registers port `11434`** and listens.
2. On first request for a model, **loads that model's tensor weights from disk into VRAM**
   (or unified memory).
3. **Listens for requests to run the model** and streams back generated tokens.

### Same shape, different kernel ask — Postgres vs. Ollama

This contrast is the point of using both as examples:

| | **Postgres** | **Ollama** |
|---|--------------|------------|
| Register a port | `5432` | `11434` |
| Then the daemon... | listens for queries | listens for generation requests |
| Core kernel ask | *let me read/write **disk*** | *reserve a big block of **VRAM*** |
| Heavy resource | disk I/O | GPU / VRAM |
| Returns | rows of data | generated tokens |

Both are daemons that "register a port and listen." They differ in **what they ask the kernel
for** and **where the heavy work happens** — disk for Postgres, fast parallel memory for Ollama.

### Model size vs. the memory you actually need

People assume "a 7-billion-parameter model needs 7 GB." Not quite. You need room for **two**
things in VRAM:

1. **The weights** — the model itself (Foundation doc: the baked parameters). Size depends on
   parameter count and **quantization** (how many bits per weight; 4-bit is common and shrinks
   the footprint a lot).
2. **The working memory for the request** — the **context**: your input tokens, the model's
   intermediate reasoning, and the output it generates all consume additional memory (the
   **KV cache**), and it **grows with how much context you feed and generate**.

So a model that *loads* in 5 GB might need noticeably more once you hand it a long curated
briefing and ask for a long answer. **Big context = more memory, on top of the weights.** This
is the same lesson as the Foundation doc's "overloading context hurts" — here it also literally
costs RAM/VRAM.

### CPU offloading (brief)

If a model does not fully fit in VRAM, Ollama can **offload** some layers to **system RAM and the
CPU**. It still runs — but the CPU part is far slower than the GPU part, so generation crawls.
The rule of thumb: **fits in fast memory → fast; spills to CPU → slow.** This is a major reason
unified memory (huge pool) is attractive for big local models.

### Modelfiles — registering your own model variant

Ollama lets you write a **`Modelfile`**: a small recipe that starts from a base model and bakes
in defaults — a **system prompt**, parameters (temperature, context length), even **tool
descriptions**. You then `ollama create my-model -f Modelfile` and it is **registered as a new
model** you can serve like any other.

```dockerfile
FROM llama3.1:8b
SYSTEM "You are the advertising knowledge assistant. Always cite book and page."
PARAMETER temperature 0.2
```

Why this is interesting for us: you can **bake a tool dictionary or retrieval instructions
straight into the model** so every call already knows them. Note that **Anthropic does not teach
this** — and cannot, because Claude is their **hosted** model; you do not own its weights, so you
configure it per-request instead. With a local model **you own the weights**, so baking config
into a Modelfile is on the table. Different ownership, different options.

---

## Part 5 · Talking to daemons: HTTP, CRUD, and auth

A daemon is listening on a port. How do you talk to it? For most requests, the answer is
**HTTP** — the language of the web.

> **Disclaimer — HTTP vs HTML, and MD vs HTML.** Two near-identical acronyms that mean completely
> different things, plus a third you are reading right now.
>
> - **HTTP** = *HyperText **Transfer** Protocol* — the **delivery system**. It is the rules for
>   *moving* a file from a server to your browser (the request/response handshake below). It does
>   not care what the file is.
> - **HTML** = *HyperText **Markup** Language* — the **content**. It is what web pages are written
>   in: text wrapped in tags (`<h1>`, `<p>`, `<a>`) that a browser knows how to display.
>
> So HTTP **transfers** the HTML. One is the truck; the other is the cargo. The tutorial's `serve`
> script (Part 2) is an HTTP server **delivering** HTML files.
>
> **MD vs HTML.** **Markdown (`.md`)** is a plain-text shorthand for formatting — `#` for a
> heading, `**bold**`, `- ` for a list. It is easy for *humans* to write and read. **HTML** is the
> verbose, tag-based form a *browser* renders. Markdown is deliberately a smaller, simpler
> language; a tool **converts `.md` into `.html`** for display (that is exactly what
> `build_reader.py` does for this tutorial).
>
> **You are looking at both right now.** Every module is authored as a **Markdown file on the
> left** in `md/` (the prose you read, e.g. `md/FOUNDATION_COMPUTER_ENGINEERING.md`) paired with a
> hand-built **HTML explainer on the right** in `html/` (the visual diagrams, e.g.
> `html/foundation_computer_engineering_explainer.html`). Left = easy-to-edit text; right =
> rendered visuals. Same ideas, two formats.

### HTTP is a handshake, then it hangs up

One HTTP call is a **short conversation that ends abruptly on purpose**:

1. Client **opens** a connection to the server's port.
2. Client **sends a request** (method + path + optional body).
3. Server **sends one response** (status code + body).
4. Connection **closes.** Done.

No lingering, no ongoing relationship — ask once, answer once, hang up. That is exactly right for
quick operations and is why HTTP scales so well (the server is not holding thousands of
connections open). It is also why HTTP is **wrong for long workflows** — which is what Part 7 is
about.

### CRUD — the four things you do to data

Almost everything a system does to stored data is one of four verbs, abbreviated **CRUD**, and
each maps to an HTTP method:

| CRUD | Meaning | HTTP method | Example |
|------|---------|-------------|---------|
| **C**reate | make a new record | `POST` | add an advertisement |
| **R**ead | fetch records | `GET` | list advertisements |
| **U**pdate | change a record | `PUT` / `PATCH` | edit an advertisement |
| **D**elete | remove a record | `DELETE` | delete an advertisement |

### The "C" in CRUD — `POST /api/advertisements` (simple version)

A clean **Create** endpoint for our advertising system. Read it as: *a request arrives on a port,
the server validates the body, writes one row to Postgres (Part 3), and returns the new record.*

```python
# POST /api/advertisements  — create one advertisement
@app.post("/api/advertisements")
def create_advertisement(ad: AdvertisementCreate) -> dict:
    """Create a new advertisement record and return it with its new id."""
    row = db.insert(
        "advertisements",
        headline=ad.headline,
        body=ad.body,
        campaign_id=ad.campaign_id,
    )
    return {"id": row.id, "status": "created", "advertisement": row.as_dict()}
```

Request and response, on the wire:

```
POST /api/advertisements
Content-Type: application/json

{ "headline": "Limited drop — 24h", "body": "...", "campaign_id": "camp-001" }
```
```
201 Created
{ "id": 4412, "status": "created", "advertisement": { ... } }
```

That is the whole "Create" story: one `POST`, one row, one response, connection closes.

### The same endpoint — now with auth middleware

In the real world you cannot let *anyone* create advertisements. You add **middleware**: code
that runs **before** your handler on every request, checks **who is calling**, and rejects them
if they are not allowed. The handler itself barely changes — the gate goes in front.

```python
# Middleware runs FIRST on every request to a protected route.
@app.middleware
def require_auth(request, call_next):
    token = request.headers.get("Authorization")      # "Bearer <token>"
    user = verify_token(token)                         # decode + check
    if user is None:
        return Response(status_code=401)               # 401 Unauthorized — stop here
    request.state.user = user                          # hand identity to the handler
    return call_next(request)                          # allowed → continue

@app.post("/api/advertisements")
def create_advertisement(ad: AdvertisementCreate, request) -> dict:
    """Create an advertisement. Caller already authenticated by middleware."""
    user = request.state.user
    row = db.insert(
        "advertisements",
        headline=ad.headline,
        body=ad.body,
        campaign_id=ad.campaign_id,
        created_by=user.id,                            # provenance — who made it
    )
    return {"id": row.id, "status": "created", "advertisement": row.as_dict()}
```

Two things to notice: the **happy path is unchanged** (Module 1 — guard clauses run first and
bail early with `401`), and we now record **who** created the row (`created_by`) — provenance,
straight from the Foundation doc.

### API keys vs. JWTs vs. bearer tokens — what is the difference?

These three get conflated constantly. They answer different questions.

| | What it is | Who it identifies | Typical use |
|---|------------|-------------------|-------------|
| **API key** | A long random secret string | **An application / account** | Your server → Anthropic (`ANTHROPIC_API_KEY`) |
| **JWT** (JSON Web Token) | A **signed**, self-contained token holding claims (user id, role, expiry) | **A specific user**, for a while | A logged-in user's session |
| **Bearer token** | **How** a token is sent, not what it is | (whatever the token says) | The HTTP header format |

The clean way to hold them apart:

- **API key** = a house key. Whoever holds it gets in **as the account**. No expiry, no built-in
  identity beyond "this account." That is why it lives in `.env` and never ships to a browser.
- **JWT** = a signed wristband. It **contains** facts ("user 88, role editor, expires 5pm") and a
  signature the server can verify **without a database lookup**. Good for user sessions; expires.
- **"Bearer token"** = the **envelope**, not the letter. Both of the above are usually sent the
  same way, in the HTTP header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsIn...
```

"Bearer" literally means *"whoever bears (carries) this token is granted access"* — so the token
is a secret you must protect, exactly like the router access code in Part 2.

---

## Part 6 · Talking to Ollama: `curl` and curated context

`curl` is a command-line tool that makes one HTTP request — perfect for poking a daemon by hand.
Here we ask our **local** Ollama model (Part 4) a question. Notice the shape of the message list:
**system prompt + user prompt + the curated context we retrieved from our sources.**

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.1:8b",
  "stream": false,
  "messages": [
    {
      "role": "system",
      "content": "You are the advertising knowledge assistant. Answer ONLY from the provided context. Always cite book and page."
    },
    {
      "role": "user",
      "content": "Is this headline OK under fair use?\n\nCONTEXT:\n- [The Legal Ad p.15] Fair use in advertising is narrow; assume you need a license for recognizable assets.\n- [The Legal Ad p.31] Disclaimers must sit next to the claim they qualify."
    }
  ]
}'
```

This is **precision applied at scale** from the Foundation doc, made concrete. The context block
is not the whole book — it is the **curated, cited briefing** our RAG pipeline produced (Modules
7–8). Three ingredients, every time:

1. **System prompt** — the standing rules ("cite book and page; answer only from context").
2. **User prompt** — the actual question.
3. **Context from sources** — the retrieved, cited passages, pasted in so the model reasons over
   *your* evidence instead of guessing from its weights.

Same anatomy whether you call Claude (Module 6) or a local model — only the address and auth
differ. A hosted model needs an API key; `localhost:11434` needs nothing because it never leaves
your machine.

---

## Part 7 · Streams and SSE — for workflows that take time

HTTP (Part 5) is one quick question and one quick answer, then hang up. But our real system does
something **slow and multi-step**: take a question, route to sources, search the knowledge base,
read passages, *then* generate a cited answer token by token. That is a **workflow**, and a
workflow can run for many seconds.

You have two bad options and one good one:

- ❌ **One long HTTP request** — the user stares at a frozen spinner for 20 seconds with no idea
  whether it is working or hung.
- ❌ **Polling** — the browser asks "done yet? done yet?" every second. Wasteful and amateur.
- ✅ **A stream** — open the connection **once** and let the server **push updates as they
  happen** until the work is done.

### SSE — Server-Sent Events (define)

**SSE = Server-Sent Events.** It is the simple kind of stream: the client opens one connection
(with an ordinary HTTP handshake — that part is fine, Part 5), and instead of sending one
response and hanging up, the server **keeps the connection open and pushes a sequence of
events** down it. One direction (server → client), text-based, easy to read. When the workflow
finishes, the server sends a final event and closes.

> **Connect it back:** HTTP = ask once, answer once (a quick `GET`/`POST`). SSE = ask once, then
> receive a **running commentary** until done (a workflow). Use the cheap thing for cheap work
> and the stream for the slow, multi-step work. Picking the wrong one is the most common way
> distributed systems look amateurish.

### Our main feature, as a stream

The heart of the proposed system — **retrieve from the advertising knowledge base and answer** —
is a streamed workflow. This is a trimmed-down version of the real `ask_stream` generator in our
medical sister-project, retargeted to the ad library. Each `yield` is **one SSE event** the
browser receives the instant it happens:

```python
# Simplified ask_stream for the advertising knowledge base.
# Each yield is ONE SSE event pushed to the browser as it happens.
async def ad_knowledge_stream(request, q: str, sources: list[str]):
    yield sse("start",  {"q": q, "sources": sources})       # 1. acknowledge instantly

    yield sse("status", {"status": "embedding_query"})       # 2. narrate each step...
    q_vec = await embed_query(q)

    yield sse("status", {"status": "retrieving"})            # 3. search the books
    matches = await search_sources(q_vec, sources)
    yield sse("matches", {"matches": matches})               #    show what we found

    yield sse("status", {"status": "generating_answer"})     # 4. ask the model
    async for token in stream_llm(q, context=matches):       #    push tokens AS they generate
        if await request.is_disconnected():                  #    user closed tab? stop working
            return
        yield sse("token", {"text": token})

    yield sse("citations", {"citations": cite(matches)})     # 5. the receipts
    yield sse("end", {"status": "done"})                     # 6. final event, then close
```

The user sees **progress the whole time** — "searching… found 6 passages… writing…" — and the
answer appears word by word, exactly like a chat UI. That experience is impossible over a single
blocking HTTP call. Two details worth keeping:

- `request.is_disconnected()` — if the user closes the tab, **stop doing expensive work.** An
  abandoned stream that keeps burning the GPU is the streaming cousin of the runaway agentic loop
  from Module 4.
- Every step is a **named event** (`start`, `status`, `matches`, `token`, `citations`, `end`) —
  the same provenance instinct as `session_log.json`: the workflow narrates itself.

---

## Part 8 · Limits and scaling — the system as resource allocator

Streams are wonderful and **not free.** Each open stream holds a connection *and*, for us, often
a slice of the GPU. Hardware is finite, so a real system must ration it.

### Stream concurrency limits

A single box can only keep so many streams alive at once. On a **Mac Studio**, plan for roughly
**15–20 concurrent inference streams** before quality of service falls apart — each one needs
memory and a share of compute, and they compete. Past that ceiling, new requests must **wait**,
not barge in (or everyone's stream stutters).

### GPU concurrency — one model, in use

Here is the hard constraint people miss: **a loaded model is largely a one-at-a-time resource for
heavy generation.** While the GPU is busy doing the matrix math for one big inference, it is not
also doing someone else's. Some realities:

- You **can** write several **Modelfiles** (Part 4) for the *same small model* and serve them, and
  small/fast models can interleave many light requests acceptably.
- But under **heavy** inference (e.g. a large model on an **Apple M2 Ultra**), the realistic
  pattern is to **keep one small model and one large model resident** — small for cheap/fast
  tasks (routing, term extraction), large for the final answer — and route work between them,
  rather than pretending you can run ten big generations at once.

### How heavy work *erodes* unified memory

Remember unified memory is **one shared pool** (Part 1). That is a strength and a trap: everything
draws from the same well. Two heavy things at once compete:

- **Many inference streams** hold weights + per-request context (the KV cache that grows with
  context — Part 4).
- **Heavy database work** — picture a semantic search that needs a **sequential fallback** when
  the fast approximate index (ANN) goes wrong, forcing a brute-force scan across **huge tables**
  (in the medical project, MIMIC). That scan pulls enormous data into memory.

Run both at once on one box and the shared pool **erodes** — inference slows as the database
work steals memory and bandwidth, and vice versa. The box does not crash; it just gets slow and
unpredictable, which is worse.

### The three classic ways out

When one box is not enough, you reach for one (or all) of these:

| Strategy | Tool example | Idea |
|----------|--------------|------|
| **Queue** | RabbitMQ | Accept all requests, but **process them in an orderly line** instead of all at once. Smooths spikes. |
| **Schedule** | overnight `cron` job | Do the heavy, non-urgent work (re-embedding the whole library, big scans) **when nobody is waiting** — e.g. 3 a.m. |
| **Scale** | another box/node, AWS, cloud GPUs | **Add hardware.** Buy a second machine, or rent cloud compute that grows and shrinks with demand. |

A **queue** (Module 4's loop, but for whole jobs) is usually the first reach: it turns "everyone
at once → meltdown" into "everyone in turn → steady." Scheduling moves load off peak hours.
Scaling spends money to buy more of the finite thing.

---

## Part 9 · Tie it back — the system owns all of this

`FOUNDATION_FOR_AI_SYSTEMS.md` defined a **system** as the honest manager of state. Now you can
see what that manager is actually *managing* — the machinery of this whole document:

- **Environment & secrets** — it loads the `.env` (Part 3): the `DATABASE_URL`, the API keys.
  Nothing is hardcoded; nothing secret is committed.
- **Incoming requests, including auth** — it owns the ports and the HTTP/stream endpoints (Parts
  5, 7), and the middleware that checks **who** is calling before any work happens (Part 5).
- **Resource allocation** — it decides what loads into **VRAM**, which model answers which
  request, how many **streams** run at once, and what gets **queued, scheduled, or pushed to
  another node** (Parts 4, 8).

That is the job. A "system" is not the AI model and it is not one clever function — it is the
**daemon that owns the port, guards the secrets, checks the caller, allocates the hardware, and
keeps an honest record of what it did.** Everything in this tutorial — the books, the RAG, the
TartaurusLoop, the Bayesian scorekeeper — runs **inside** that system.

> **What to take from Session 1.** You will not remember every term. You should now be able to
> hear *"the Ollama daemon registers a port and loads weights into VRAM, the API gates requests
> with a bearer token, and the workflow streams results over SSE"* and follow the **shape** of
> it, even where the details are still fuzzy. That is the whole goal: exposure. The fog burns off
> the first time you watch it run.
