#!/usr/bin/env python3
"""Build a single self-contained index.html reader for the CCA-F Python tutorial.

Renders every markdown doc to HTML and embeds it, alongside its interactive HTML
explainer, into one offline file. Just double-click index.html — no server, no
internet, no markdown tools required.

Re-run after editing any doc:  python build_reader.py
"""
import html
import json
import re
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
MD_DIR = HERE / "md"

# (number, markdown file under md/, friendly title, tier, one-line blurb, companion html)
DOCS = [
    ("F", "md/FOUNDATION_FOR_AI_SYSTEMS.md",
     "Foundation for AI Systems", "Foundation",
     "Read first \u2014 systems, LLMs, inference, precision. Everything else assumes this.",
     "html/foundation_for_ai_systems_explainer.html"),
    ("F2", "md/FOUNDATION_COMPUTER_ENGINEERING.md",
     "Foundation for Computer Engineering", "Foundation",
     "Session 1 \u2014 ports, daemons, kernel, storage; serve script, Postgres, Ollama; HTTP, auth, SSE, scaling.",
     "html/foundation_computer_engineering_explainer.html"),
    ("00", "md/00_OVERVIEW_AND_RUNNING_EXAMPLE.md",
     "Overview & Running Example", "Overview",
     "CCA-F reframe: Python to read Skilljar. Running example: 10-book advertising RAG.",
     "html/00_overview_explainer.html"),
    ("01", "md/01_PYTHON_SURVIVAL_KIT.md",
     "Module 1: Python Survival Kit", "Modules",
     "Read Python aloud \u2014 indentation, types, docstrings. 45 min.",
     "html/01_survival_kit_explainer.html"),
    ("02", "md/02_DICTIONARIES_LISTS_JSON.md",
     "Module 2: Dicts, Lists & JSON", "Modules",
     "Tool schemas and API payloads are nested dicts. ~38% of exam territory.",
     "html/02_dicts_json_explainer.html"),
    ("03", "md/03_FUNCTIONS_TYPE_HINTS_TOOLS.md",
     "Module 3: Functions & Tools", "Modules",
     "Tools are functions. Type hints and docstrings = how Claude picks tools.",
     "html/03_functions_tools_explainer.html"),
    ("04", "md/04_CONTROL_FLOW_AND_THE_AGENTIC_LOOP.md",
     "Module 4: The Agentic Loop", "Modules",
     "while stop_reason == tool_use \u2014 Domain 1, highest leverage.",
     "html/04_agentic_loop_explainer.html"),
    ("05", "md/05_DECORATORS_IMPORTS_PYDANTIC.md",
     "Module 5: OOP, Decorators & Pydantic", "Modules",
     "Classes, @server.tool(), BaseModel — API/DB contracts.",
     "html/05_decorators_pydantic_explainer.html"),
    ("06", "md/06_READING_REAL_ANTHROPIC_SDK_CODE.md",
     "Module 6: Reading SDK Code", "Modules",
     "Walk real Anthropic SDK samples; .env vs export for API keys.",
     "html/06_sdk_env_explainer.html"),
    ("07", "md/07_TEN_BOOK_RAG_WITH_TARTAURUSLOOP.md",
     "Module 7: RAG + TartaurusLoop", "Integration",
     "Full 10-book pipeline orchestrated with Anthropic TartaurusLoop.",
     "html/07_tartaurus_rag_explainer.html"),
    ("08", "md/08_BAYESIAN_SIX_SCHEMA_LOOP.md",
     "Module 8: Six-Schema Bayesian Loop", "Integration",
     "Score keeping: six @dataclass schemas, hypothesis to evidence to belief update.",
     "html/08_bayesian_schemas_explainer.html"),
]

# HTML-only self-check. No markdown pane; opens full-width under the Foundation
# section. Scores live only in the page (nothing saved or sent).
QUIZ = {
    "num": "Q",
    "title": "Foundation Self-Check Quiz",
    "tier": "Foundation",
    "blurb": "Multiple choice over both foundation docs. Wrong answer \u2192 explanation, then retry. Nothing is scored or saved.",
    "companion": "html/foundation_quiz.html",
}

ABSTRACT = (
    "Python for the Claude Certified Architect \u2014 Foundations exam. Not Python to pass "
    "the exam \u2014 Python to absorb Skilljar without getting lost in syntax. Running example: "
    "10-book RAG, TartaurusLoop, six-schema Bayesian score keeping. Named venvs; @dataclass "
    "as API/DB contracts."
)

TIER_NOTE = {
    "Foundation": "Session 1 \u2014 honest data + LLMs, then the machine: ports, daemons, storage, networking.",
    "Overview": "CCA-F reframe, named venv, running example, module map.",
    "Modules": "Core Python for Skilljar (~5 hours).",
    "Integration": "RAG + TartaurusLoop + Bayesian six-schema loop.",
}

MD_EXTS = ["extra", "sane_lists", "toc"]


def render_md(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    md = markdown.Markdown(extensions=MD_EXTS, output_format="html5")
    return md.convert(text)


def rewrite_internal_links(rendered: str, name_to_anchor: dict) -> str:
    """Point links between docs (foo.md) at in-app navigation (#NN)."""
    def repl(m):
        href = m.group(1)
        base = href.split("/")[-1].split("#")[0]
        if base in name_to_anchor:
            return f'href="#{name_to_anchor[base]}" data-internal="1"'
        return m.group(0)
    return re.sub(r'href="([^"]+\.md[^"]*)"', repl, rendered)


def build():
    name_to_anchor = {Path(d[1]).name: d[0] for d in DOCS}

    cards, templates, companions = [], [], []
    for num, mdfile, title, tier, blurb, companion in DOCS:
        mdpath = HERE / mdfile
        if not mdpath.exists():
            print(f"  ! missing {mdfile} \u2014 skipping")
            continue
        rendered = render_md(mdpath)
        rendered = rewrite_internal_links(rendered, name_to_anchor)
        templates.append(
            f'<template data-doc="{num}">{rendered}</template>'
        )
        comp_path = HERE / companion
        comp = companion if comp_path.exists() else ""
        if comp:
            # Embed the whole explainer inline so the right pane needs no file
            # load (works under file:// in every browser, even from a zip).
            payload = json.dumps(comp_path.read_text(encoding="utf-8"))
            payload = payload.replace("</", "<\\/")  # neutralize </script>
            companions.append(
                f'<script type="application/json" id="comp-{num}">{payload}</script>'
            )
        cards.append({
            "num": num, "title": title, "tier": tier,
            "blurb": blurb, "companion": comp,
        })
        print(f"  rendered {mdfile}  (companion: {comp or 'none'})")

    # Quiz: HTML-only card embedded like a companion (no markdown template).
    # Inserted right after the last Foundation card so it sits below the
    # foundation docs it tests.
    q_path = HERE / QUIZ["companion"]
    if q_path.exists():
        payload = json.dumps(q_path.read_text(encoding="utf-8")).replace("</", "<\\/")
        companions.append(
            f'<script type="application/json" id="comp-{QUIZ["num"]}">{payload}</script>'
        )
        insert_at = max(
            (i for i, c in enumerate(cards) if c["tier"] == "Foundation"), default=-1
        ) + 1
        cards.insert(insert_at, {
            "num": QUIZ["num"], "title": QUIZ["title"], "tier": QUIZ["tier"],
            "blurb": QUIZ["blurb"], "companion": QUIZ["companion"], "quiz": True,
        })
        print(f"  embedded {QUIZ['companion']}  (quiz card)")
    else:
        print(f"  ! missing {QUIZ['companion']} \u2014 quiz card skipped")

    # Group cards by tier for the home list.
    tiers_order = ["Foundation", "Overview", "Modules", "Integration"]
    list_html = []
    for tier in tiers_order:
        group = [c for c in cards if c["tier"] == tier]
        if not group:
            continue
        list_html.append(
            f'<div class="tier"><span class="tier-name">{tier}</span>'
            f'<span class="tier-note">{html.escape(TIER_NOTE[tier])}</span></div>'
        )
        for c in group:
            is_quiz = c.get("quiz")
            card_cls = "doc-card quiz-card" if is_quiz else "doc-card"
            badge_cls = "badge t-quiz" if is_quiz else f"badge t-{tier.lower()}"
            go_label = "Take quiz &rarr;" if is_quiz else "Read &rarr;"
            list_html.append(
                f'<a class="{card_cls}" href="#{c["num"]}" data-internal="1">'
                f'<span class="{badge_cls}">{c["num"]}</span>'
                f'<span class="doc-text"><b>{html.escape(c["title"])}</b>'
                f'<small>{html.escape(c["blurb"])}</small></span>'
                f'<span class="go">{go_label}</span></a>'
            )

    # Doc meta for JS (number -> title + companion path + quiz flag).
    meta = ",".join(
        '"{n}":{{"title":{t},"companion":{c},"quiz":{q}}}'.format(
            n=c["num"],
            t=_jsstr(c["title"]),
            c=_jsstr(c["companion"]),
            q=("true" if c.get("quiz") else "false"),
        )
        for c in cards
    )

    out = PAGE.replace("/*__LIST__*/", "\n".join(list_html))
    out = out.replace("/*__TEMPLATES__*/", "\n".join(templates))
    out = out.replace("/*__COMPANIONS__*/", "\n".join(companions))
    out = out.replace("/*__META__*/", "{" + meta + "}")
    out = out.replace("/*__ABSTRACT__*/", html.escape(ABSTRACT))

    (HERE / "index.html").write_text(out, encoding="utf-8")
    print(f"\n  wrote {HERE / 'index.html'}  ({len(out):,} bytes)")


def _jsstr(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Python for CCA-F &mdash; AJA Tutorial</title>
<style>
  :root{
    --bg:#0d1117; --panel:#161b22; --panel2:#1c2530; --border:#30363d;
    --text:#e6edf3; --muted:#8b949e; --blue:#58a6ff; --green:#3fb950;
    --amber:#d29922; --red:#f85149; --purple:#bc8cff;
  }
  *{box-sizing:border-box}
  html,body{height:100%}
  body{margin:0;background:radial-gradient(1200px 700px at 18% -12%,#16202c 0%,var(--bg) 55%);
    color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.6}
  a{color:var(--blue);text-decoration:none} a:hover{text-decoration:underline}

  /* ---------- HOME ---------- */
  #home{max-width:860px;margin:0 auto;padding:54px 22px 90px}
  .kicker{font-size:11px;text-transform:uppercase;letter-spacing:2px;color:var(--muted);margin-bottom:10px}
  h1.title{font-size:34px;margin:0 0 14px;letter-spacing:-.6px;line-height:1.15}
  .abstract{font-size:16px;color:var(--text);background:var(--panel);border:1px solid var(--border);
    border-left:3px solid var(--blue);border-radius:12px;padding:18px 20px;max-width:760px}
  .by{color:var(--muted);font-size:13px;margin:14px 0 30px}
  .tier{display:flex;align-items:baseline;gap:12px;margin:30px 0 12px;border-bottom:1px solid var(--border);padding-bottom:8px}
  .tier-name{font-size:13px;text-transform:uppercase;letter-spacing:1.5px;font-weight:700;color:var(--text)}
  .tier-note{font-size:12.5px;color:var(--muted)}
  .doc-card{display:flex;align-items:center;gap:16px;background:var(--panel);border:1px solid var(--border);
    border-radius:13px;padding:15px 18px;margin:10px 0;transition:border-color .15s,transform .06s,background .15s}
  .doc-card:hover{border-color:var(--blue);background:#19222e;text-decoration:none;transform:translateY(-1px)}
  .badge{flex:0 0 auto;width:42px;height:42px;border-radius:11px;display:flex;align-items:center;justify-content:center;
    font-weight:800;font-size:16px;background:var(--panel2);border:1px solid var(--border)}
  .badge.t-foundation{color:var(--blue);border-color:var(--blue)}
  .badge.t-foundations{color:var(--blue);border-color:var(--blue)}
  .badge.t-mvp{color:var(--green);border-color:var(--green)}
  .badge.t-vision{color:var(--purple);border-color:var(--purple)}
  .badge.t-quiz{color:var(--amber);border-color:var(--amber)}
  .quiz-card{border-style:dashed}
  .quiz-card:hover{border-color:var(--amber);background:#221d12}
  .quiz-card:hover .go{color:var(--amber)}
  .doc-text{flex:1;display:flex;flex-direction:column;gap:3px}
  .doc-text b{font-size:16px} .doc-text small{color:var(--muted);font-size:13px}
  .go{flex:0 0 auto;color:var(--muted);font-size:13px;font-weight:600}
  .doc-card:hover .go{color:var(--blue)}
  .home-foot{margin-top:40px;color:var(--muted);font-size:12.5px;border-top:1px solid var(--border);padding-top:16px}

  /* ---------- VIEWER ---------- */
  #viewer{display:none;height:100vh;flex-direction:column}
  #viewer.on{display:flex}
  .bar{flex:0 0 auto;display:flex;align-items:center;gap:14px;padding:11px 18px;background:var(--panel);
    border-bottom:1px solid var(--border)}
  .bar button{font:inherit;font-size:13px;font-weight:600;cursor:pointer;border-radius:9px;padding:8px 13px;
    border:1px solid var(--border);background:var(--panel2);color:var(--text)}
  .bar button:hover{filter:brightness(1.25)}
  .bar button:disabled{opacity:.35;cursor:default;filter:none}
  .bar button.ghost{background:transparent;color:var(--muted)}
  .bar button.ghost:hover{color:var(--text);filter:none}
  .bar .vtitle{font-size:15px;font-weight:700} .bar .vnum{color:var(--muted);font-weight:600;margin-right:2px}
  .bar .spacer{flex:1}
  .panes{flex:1;display:grid;grid-template-columns:1fr 1fr;min-height:0}
  .panes.solo{grid-template-columns:1fr}
  .panes.full-right{grid-template-columns:1fr}
  .pane{min-height:0;overflow:auto}
  .pane.left{border-right:1px solid var(--border)}
  .panes.solo .pane.right{display:none}
  .panes.full-right .pane.left{display:none}
  .pane-head{position:sticky;top:0;background:rgba(13,17,23,.92);backdrop-filter:blur(4px);
    border-bottom:1px solid var(--border);padding:8px 22px;font-size:11px;text-transform:uppercase;
    letter-spacing:1.2px;color:var(--muted);z-index:5}
  iframe{width:100%;height:100%;border:0;background:var(--bg)}

  /* rendered markdown typography */
  .md{padding:8px 34px 80px;max-width:820px}
  .md h1{font-size:27px;margin:26px 0 10px;letter-spacing:-.4px;line-height:1.2}
  .md h2{font-size:21px;margin:30px 0 10px;border-bottom:1px solid var(--border);padding-bottom:6px}
  .md h3{font-size:16px;margin:22px 0 8px;color:var(--text)}
  .md h4{font-size:14px;margin:18px 0 6px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
  .md p{margin:12px 0;font-size:15.5px}
  .md ul,.md ol{padding-left:24px;margin:12px 0} .md li{margin:6px 0;font-size:15.5px}
  .md a{color:var(--blue)}
  .md strong{color:#fff}
  .md em{color:var(--text)}
  .md code{background:var(--panel2);border:1px solid var(--border);border-radius:5px;padding:1px 6px;
    font-size:13px;color:var(--blue);font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
  .md pre{background:#0b0f14;border:1px solid var(--border);border-radius:10px;padding:14px 16px;overflow:auto;margin:14px 0}
  .md pre code{background:none;border:0;padding:0;color:#c9d1d9;font-size:13px;line-height:1.5}
  .md blockquote{margin:14px 0;padding:10px 16px;border-left:3px solid var(--amber);background:var(--panel);
    border-radius:0 8px 8px 0;color:var(--text)}
  .md blockquote p{margin:6px 0;font-size:14.5px}
  .md table{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px;display:block;overflow:auto}
  .md th,.md td{border:1px solid var(--border);padding:8px 11px;text-align:left;vertical-align:top}
  .md th{background:var(--panel2);color:var(--muted);font-size:12.5px;text-transform:uppercase;letter-spacing:.4px}
  .md hr{border:0;border-top:1px solid var(--border);margin:26px 0}
  .md .mermaid{background:var(--panel2);border:1px solid var(--border);border-radius:10px;padding:16px;text-align:center}
  .md pre.mermaid-src{opacity:.85}

  /* Narrow screens (phones, iPad portrait): stack and let the whole page scroll —
     the writing first, the picture below it. */
  @media(max-width:900px){
    #viewer.on{display:block;height:auto;min-height:100vh}
    .bar{position:sticky;top:0;z-index:20}
    .panes,.panes.solo{display:block;min-height:0}
    .pane{overflow:visible;height:auto}
    .pane.left{border-right:0}
    .pane.right{border-top:1px solid var(--border)}
    .pane-head{position:static}
    .md{padding:8px 18px 36px;max-width:none}
    iframe{height:84vh;min-height:520px}
  }
</style>
</head>
<body>

<!-- ================= HOME ================= -->
<main id="home">
  <div class="kicker">AI Jedi Academy &middot; Python for CCA-F</div>
  <h1 class="title">Python for CCA-F &mdash; AJA Tutorial</h1>
  <div class="abstract">/*__ABSTRACT__*/</div>
  <div class="by">Written by Dylan, with AI assistance &middot; click any chapter: the writing opens on the left,
  a little interactive picture on the right.</div>

  /*__LIST__*/

  <div class="home-foot">Nothing here needs the internet. Everything runs right in this file. &middot;
  Tip: on a small screen the picture sits below the text.</div>
</main>

<!-- ================= VIEWER ================= -->
<section id="viewer">
  <div class="bar">
    <button onclick="goBack()" title="Go back to where you were">&larr; Back</button>
    <button class="ghost" onclick="goToHome()" title="Jump to the chapter list">All chapters</button>
    <span class="vnum" id="vnum"></span><span class="vtitle" id="vtitle"></span>
    <span class="spacer"></span>
    <button id="prevBtn" onclick="step(-1)">&uarr; Prev</button>
    <button id="nextBtn" onclick="step(1)">Next &darr;</button>
  </div>
  <div class="panes" id="panes">
    <div class="pane left">
      <div class="pane-head">The writing</div>
      <div class="md" id="mdpane"></div>
    </div>
    <div class="pane right">
      <div class="pane-head" id="rightHead">The picture</div>
      <iframe id="frame" title="explainer"></iframe>
    </div>
  </div>
</section>

<!-- embedded rendered markdown -->
/*__TEMPLATES__*/
<!-- embedded interactive explainers (loaded into the right pane via srcdoc) -->
/*__COMPANIONS__*/

<script>
const META = /*__META__*/;
const ORDER = Object.keys(META);
let current = null;

function tmpl(num){
  const t = document.querySelector('template[data-doc="'+num+'"]');
  return t ? t.innerHTML : '<p>Not found.</p>';
}

function renderMermaid(root){
  const blocks = root.querySelectorAll('code.language-mermaid, code.mermaid');
  if(!blocks.length) return;
  blocks.forEach(code=>{
    const pre = code.closest('pre') || code;
    const src = code.textContent;
    const holder = document.createElement('div');
    holder.className = 'mermaid';
    holder.textContent = src;
    pre.replaceWith(holder);
  });
  if(window.mermaid){
    try{ window.mermaid.run({nodes: root.querySelectorAll('.mermaid')}); }
    catch(e){ /* leave as text if it fails */ }
  } else {
    // offline / no mermaid: show the diagram source as a readable code block
    root.querySelectorAll('.mermaid').forEach(d=>{
      const pre=document.createElement('pre'); pre.className='mermaid-src';
      const c=document.createElement('code'); c.textContent=d.textContent;
      pre.appendChild(c); d.replaceWith(pre);
    });
  }
}

// Always land at the top when a chapter opens. Reset every possible scroller,
// and run again next frame to beat the browser restoring the old position on
// hash navigation.
function resetScroll(){
  window.scrollTo(0,0);
  document.documentElement.scrollTop = 0;
  document.body.scrollTop = 0;
  const l = document.querySelector('.pane.left'); if(l){ l.scrollTop = 0; }
  const r = document.querySelector('.pane.right'); if(r){ r.scrollTop = 0; }
}

function showDoc(num){
  current = num;
  const isQuiz = !!(META[num] && META[num].quiz);
  document.getElementById('vnum').textContent = num + ' \u00b7 ';
  document.getElementById('vtitle').textContent = META[num].title;
  document.getElementById('rightHead').textContent = isQuiz ? 'Self-check quiz' : 'The picture';
  const md = document.getElementById('mdpane');
  md.innerHTML = isQuiz ? '' : tmpl(num);     // quiz has no markdown pane
  if(!isQuiz) renderMermaid(md);

  const frame = document.getElementById('frame');
  const panes = document.getElementById('panes');
  const embed = document.getElementById('comp-'+num);
  // Quiz fills the whole viewer; docs keep the writing|picture split.
  panes.classList.toggle('full-right', isQuiz);
  if(embed){
    // Inline payload — no file load, works offline / from a zip / any browser.
    frame.srcdoc = JSON.parse(embed.textContent);
    panes.classList.remove('solo');
  } else if(META[num].companion){
    frame.removeAttribute('srcdoc');
    frame.src = META[num].companion;
    panes.classList.remove('solo');
  } else {
    frame.removeAttribute('src');
    frame.removeAttribute('srcdoc');
    panes.classList.add('solo');
  }
  const i = ORDER.indexOf(num);
  document.getElementById('prevBtn').disabled = (i <= 0);
  document.getElementById('nextBtn').disabled = (i >= ORDER.length-1);
  document.getElementById('home').style.display='none';
  document.getElementById('viewer').classList.add('on');
  resetScroll();
  requestAnimationFrame(resetScroll);
}

function showHome(){
  current = null;
  document.getElementById('viewer').classList.remove('on');
  document.getElementById('home').style.display='';
  const frame = document.getElementById('frame');
  frame.removeAttribute('src');
  frame.removeAttribute('srcdoc');
  resetScroll();
  requestAnimationFrame(resetScroll);
}

// Back walks your actual history (home -> 01 -> 02 -> Back -> 01 -> Back -> home).
function goBack(){
  if(history.length > 1){ history.back(); }
  else { goToHome(); }
}
function goToHome(){
  if(location.hash && location.hash !== '#'){ location.hash=''; }
  else { showHome(); }
}
function step(dir){
  if(current===null) return;
  const i = ORDER.indexOf(current) + dir;
  if(i>=0 && i<ORDER.length){ location.hash = '#'+ORDER[i]; }
}

// One source of truth: the URL hash. Every nav just changes the hash;
// this renderer reacts. That's what makes Back (and the browser/phone
// back gesture) work for free.
function render(){
  const h = location.hash.replace('#','').trim();
  if(h && META[h]){ showDoc(h); }
  else { showHome(); }
}
// Don't let the browser restore the previous scroll position on navigation —
// we always want a fresh chapter to start at the top.
if('scrollRestoration' in history){ history.scrollRestoration = 'manual'; }
window.addEventListener('hashchange', render);
window.addEventListener('DOMContentLoaded', render);

// Try to load mermaid for nicer diagrams; silently fine if offline.
(function(){
  const s=document.createElement('script');
  s.src='https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js';
  s.onload=function(){ try{ window.mermaid.initialize({startOnLoad:false, theme:'dark'});
    if(current!==null) renderMermaid(document.getElementById('mdpane')); }catch(e){} };
  document.head.appendChild(s);
})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    print("Building offline reader...")
    build()
