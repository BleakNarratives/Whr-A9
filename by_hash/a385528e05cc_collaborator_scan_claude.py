"""
[DNA_TAG]
ORIGIN: Moto4_A9
PILLAR: valet_concierge
PATH: collaborator_scan_claude.py
LAST_SYNC: 2026-08-02T01:12:54Z
[/DNA_TAG]
"""
#!/usr/bin/env python3
"""
collaborator_scan.py

Scans Vibe session logs (messages.jsonl) AND scattered plain-text notes
(.txt, .md, and generic dump files) for mentions of your AI collaborators
-- Claude, Gemini, Mistral/Vibe, KIMI, DeepSeek, Qwen, GPT, Copilot -- and
builds a per-collaborator HTML report: mention frequency over time, context
word tags, tone tally, and a raw sample-quote list.

Also writes a companion collaborator_hits.jsonl with EVERY hit (name,
source file, timestamp, full context) so you can grep/filter the raw data
yourself -- "grab everything that said Claude" as a literal filterable file.

No third-party dependencies. Pure stdlib.

USAGE
  python3 collaborator_scan.py DIR [DIR ...] -o report.html
  python3 collaborator_scan.py /storage/emulated/0/RootBase/vibe_logs/session \
                               /storage/emulated/0/RootBase \
                               -o collab_report.html

  # only scan specific extensions (default: jsonl,txt,md)
  python3 collaborator_scan.py DIR --extensions jsonl,txt,md,log

NOTES ON ACCURACY
  "Claude", "Gemini", "Mistral", "KIMI", "DeepSeek", "Qwen", "Copilot" are
  matched as whole words, case-insensitive -- reasonably distinctive.

  "Jim" (phonetic mishear of Gemini in voice-to-text) and bare "Vibe" (also
  an everyday word / "vibe coding") are matched separately as AMBIGUOUS --
  reported with a warning, not folded into the clean counts, because they
  will catch unrelated hits in freeform notes.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

DEFAULT_EXTENSIONS = {"jsonl", "txt", "md"}

SESSION_DIR_RE = re.compile(r"session_(\d{8})_(\d{6})_")
WORD_RE = re.compile(r"[a-zA-Z']+")

STOPWORDS = set("""
a about above after again against all am an and any are as at be because
been before being below between both but by can cannot could did do does
doing don down during each few for from further had has have having he her
here hers herself him himself his how i if in into is it its itself just
let me more most my myself no nor not now of off on once only or other our
ours ourselves out over own same she should so some such than that the
their theirs them themselves then there these they this those through to
too under until up very was we were what when where which while who whom
why will with would you your yours yourself yourselves im youre dont didnt
doesnt cant wont isnt arent ive youve theyve weve theres thats whats heres
okay ok yeah yep nope null true false none use used using also like got
one two need needs still going go went already even really actually
""".split())

TONE_KEYWORDS = {
    "frustration": ["fuck", "fucking", "shit", "damn", "ugh", "wtf", "stupid",
                    "broken", "not working", "doesn't work", "isn't working",
                    "annoying", "hate", "sick of", "pissed", "goddamn", "christ"],
    "humor": ["lol", "lmao", "haha", "hahaha", "funny", "hilarious", "goofy",
              "lolol", "rofl"],
    "urgency": ["asap", "immediately", "urgent", "hurry", "right now",
                "quick", "quickly", "fast"],
    "gratitude": ["thanks", "thank you", "appreciate", "nice job",
                  "great job", "perfect", "awesome", "love it", "nailed it"],
    "uncertainty": ["not sure", "maybe", "i think", "possibly", "might be",
                     "unclear", "confused", "i guess", "no idea"],
    "confidence": ["confirmed", "definitely", "certain", "exactly",
                   "correct", "verified", "done", "fixed", "works now"],
}
TONE_COLORS = {
    "frustration": "#ff5555", "humor": "#f1c40f", "urgency": "#ff9f43",
    "gratitude": "#2ecc71", "uncertainty": "#8888ff", "confidence": "#00e5c0",
}

# canonical name -> (pattern, ambiguous?)
RELIABLE = {
    "Claude":   r"\bclaude\b",
    "Gemini":   r"\bgemini\b",
    "Mistral":  r"\bmistral\b",
    "Vibe CLI": r"\bvibe[\s\-_]?cli\b",
    "KIMI":     r"\bkimi\b",
    "DeepSeek": r"\bdeep[\s\-_]?seek\b",
    "Qwen":     r"\bqwen\b",
    "GPT":      r"\b(chat)?gpt[\-\s]?\d*\b",
    "Copilot":  r"\bcopilot\b",
}
AMBIGUOUS = {
    "Gemini (as 'Jim')": r"\bjim\b",
    "Vibe (bare word)":  r"\bvibe\b",
}

COMPILED_RELIABLE = {name: re.compile(pat, re.IGNORECASE) for name, pat in RELIABLE.items()}
COMPILED_AMBIGUOUS = {name: re.compile(pat, re.IGNORECASE) for name, pat in AMBIGUOUS.items()}

ALL_NAMES = list(RELIABLE.keys()) + list(AMBIGUOUS.keys())

NAME_COLORS = {
    "Claude": "#d97757", "Gemini": "#4285f4", "Mistral": "#ff7000",
    "Vibe CLI": "#39ff8f", "KIMI": "#a259ff", "DeepSeek": "#00b4d8",
    "Qwen": "#f72585", "GPT": "#10a37f", "Copilot": "#8957e5",
    "Gemini (as 'Jim')": "#4285f4aa", "Vibe (bare word)": "#39ff8faa",
}


# --------------------------------------------------------------------------
# Parsing helpers
# --------------------------------------------------------------------------

def session_timestamp_from_path(path):
    m = SESSION_DIR_RE.search(path)
    if not m:
        return None
    date_s, time_s = m.groups()
    try:
        return datetime.strptime(date_s + time_s, "%Y%m%d%H%M%S")
    except ValueError:
        return None


def file_mtime(path):
    try:
        return datetime.fromtimestamp(os.path.getmtime(path))
    except OSError:
        return None


def extract_text_from_jsonl_obj(obj):
    parts = []
    content = obj.get("content")
    if isinstance(content, str):
        parts.append(content)
    reasoning = obj.get("reasoning_content")
    if isinstance(reasoning, str):
        parts.append(reasoning)
    return " ".join(parts)


def tokenize(text):
    return [w.lower() for w in WORD_RE.findall(text)]


def tone_hits(text_lower):
    counts = Counter()
    for category, phrases in TONE_KEYWORDS.items():
        for phrase in phrases:
            counts[category] += text_lower.count(phrase)
    return counts


def find_matches(line_text):
    """Returns list of (canonical_name, ambiguous_bool) found in this text."""
    hits = []
    for name, rx in COMPILED_RELIABLE.items():
        if rx.search(line_text):
            hits.append((name, False))
    for name, rx in COMPILED_AMBIGUOUS.items():
        if rx.search(line_text):
            hits.append((name, True))
    return hits


def walk_files(roots, extensions):
    for root in roots:
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                ext = fn.rsplit(".", 1)[-1].lower() if "." in fn else ""
                if ext in extensions:
                    yield os.path.join(dirpath, fn)


# --------------------------------------------------------------------------
# Scanning
# --------------------------------------------------------------------------

def scan_jsonl_messages(path, context_lines, hits_out):
    session_ts = session_timestamp_from_path(path)
    try:
        with open(path, "r", errors="ignore") as f:
            lines = f.readlines()
    except OSError:
        return

    parsed = []
    for line in lines:
        line = line.strip()
        if not line:
            parsed.append(None)
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            parsed.append(None)
            continue
        parsed.append(obj)

    for i, obj in enumerate(parsed):
        if obj is None or obj.get("role") not in ("user", "assistant"):
            continue
        text = extract_text_from_jsonl_obj(obj)
        if not text:
            continue
        matches = find_matches(text)
        if not matches:
            continue
        ctx_parts = []
        for j in range(max(0, i - context_lines), min(len(parsed), i + context_lines + 1)):
            o = parsed[j]
            if o and o.get("role") in ("user", "assistant"):
                t = extract_text_from_jsonl_obj(o)
                if t:
                    ctx_parts.append(f"[{o.get('role')}] {t}")
        context = " || ".join(ctx_parts)[:800]
        for name, ambiguous in matches:
            hits_out.append({
                "name": name,
                "ambiguous": ambiguous,
                "source": path,
                "source_type": "vibe_session",
                "role": obj.get("role"),
                "timestamp": session_ts.isoformat() if session_ts else None,
                "context": context,
            })


def scan_text_file(path, context_lines, hits_out):
    mtime = file_mtime(path)
    try:
        with open(path, "r", errors="ignore") as f:
            lines = f.readlines()
    except OSError:
        return

    for i, line in enumerate(lines):
        matches = find_matches(line)
        if not matches:
            continue
        lo = max(0, i - context_lines)
        hi = min(len(lines), i + context_lines + 1)
        context = " ".join(l.strip() for l in lines[lo:hi] if l.strip())[:800]
        for name, ambiguous in matches:
            hits_out.append({
                "name": name,
                "ambiguous": ambiguous,
                "source": path,
                "source_type": "note_file",
                "line_no": i + 1,
                "timestamp": mtime.isoformat() if mtime else None,
                "context": context,
            })


def scan_all(roots, extensions, context_lines):
    hits = []
    files_scanned = 0
    for path in walk_files(roots, extensions):
        files_scanned += 1
        if os.path.basename(path) == "messages.jsonl":
            scan_jsonl_messages(path, context_lines, hits)
        else:
            scan_text_file(path, context_lines, hits)
    return hits, files_scanned


# --------------------------------------------------------------------------
# Aggregation
# --------------------------------------------------------------------------

def build_per_name_data(hits):
    per_name = defaultdict(lambda: {
        "count": 0, "ambiguous": False, "by_date": Counter(),
        "words": Counter(), "tone": Counter(), "samples": [],
        "by_source_type": Counter(),
    })
    for h in hits:
        d = per_name[h["name"]]
        d["ambiguous"] = h["ambiguous"]
        d["count"] += 1
        d["by_source_type"][h["source_type"]] += 1
        if h["timestamp"]:
            date_key = h["timestamp"][:10]
            d["by_date"][date_key] += 1
        ctx_lower = h["context"].lower()
        words = [w for w in tokenize(h["context"]) if w not in STOPWORDS and len(w) > 2]
        d["words"].update(words)
        d["tone"].update(tone_hits(ctx_lower))
        if len(d["samples"]) < 40:
            d["samples"].append(h)
    return per_name


# --------------------------------------------------------------------------
# HTML rendering
# --------------------------------------------------------------------------

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def render_html(per_name, title, files_scanned, total_hits):
    reliable_names = [n for n in RELIABLE if per_name.get(n, {}).get("count", 0) > 0]
    ambiguous_names = [n for n in AMBIGUOUS if per_name.get(n, {}).get("count", 0) > 0]

    def card(name):
        d = per_name[name]
        color = NAME_COLORS.get(name, "#39ff8f")
        top_words = d["words"].most_common(18)
        max_w = top_words[0][1] if top_words else 1
        word_tags = "".join(
            f'<span class="tag" style="font-size:{10 + (c/max_w)*14:.0f}px; '
            f'opacity:{0.5 + (c/max_w)*0.5:.2f}; color:{color}">{esc(w)}</span>'
            for w, c in top_words
        ) or '<span class="tag-empty">no context words captured</span>'

        tone_bars = "".join(
            f'<div class="tone-row"><span class="tone-label">{cat}</span>'
            f'<div class="tone-bar-bg"><div class="tone-bar-fill" '
            f'style="width:{min(100, d["tone"].get(cat,0)*8)}%; background:{TONE_COLORS[cat]}"></div></div>'
            f'<span class="tone-count">{d["tone"].get(cat,0)}</span></div>'
            for cat in TONE_KEYWORDS
        )

        dates = sorted(d["by_date"].keys())
        spark = ""
        if dates:
            max_v = max(d["by_date"].values())
            pts = []
            n = len(dates)
            for i, dt in enumerate(dates):
                x = (i / max(1, n - 1)) * 460 if n > 1 else 230
                y = 50 - (d["by_date"][dt] / max_v) * 44
                pts.append(f"{x:.1f},{y:.1f}")
            spark = (
                f'<svg viewBox="0 0 460 56" style="width:100%; height:56px;">'
                f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="1.6"/>'
                f'<text x="0" y="56" font-size="9" fill="#6f9c85">{dates[0]}</text>'
                f'<text x="410" y="56" font-size="9" fill="#6f9c85" text-anchor="end">{dates[-1]}</text>'
                f'</svg>'
            )
        else:
            spark = '<div class="tag-empty">no timestamps available for these hits</div>'

        samples_html = "".join(
            f'<div class="sample">'
            f'<div class="sample-meta">{esc(os.path.basename(s["source"]))} '
            f'{"(" + s["timestamp"][:10] + ")" if s.get("timestamp") else ""}</div>'
            f'<div class="sample-text">{esc(s["context"][:300])}</div></div>'
            for s in d["samples"][:12]
        )

        ambiguous_banner = (
            '<div class="warn">AMBIGUOUS MATCH -- this string collides with everyday '
            'language. Treat counts as noisy upper bounds, not clean signal.</div>'
            if d["ambiguous"] else ""
        )

        src_breakdown = ", ".join(f"{k}: {v}" for k, v in d["by_source_type"].items())

        return f"""
        <div class="collab-card" style="border-color:{color}">
          <div class="collab-header" style="color:{color}">{esc(name)}
            <span class="collab-count">{d['count']} mentions</span></div>
          {ambiguous_banner}
          <div class="collab-sub">sources: {src_breakdown}</div>
          <div class="collab-section-label">mentions over time</div>
          {spark}
          <div class="collab-section-label">context vocabulary</div>
          <div class="tag-cloud">{word_tags}</div>
          <div class="collab-section-label">tone in context</div>
          <div class="tone-block">{tone_bars}</div>
          <div class="collab-section-label">sample hits ({min(len(d['samples']),12)} of {d['count']})</div>
          <div class="samples">{samples_html or '<div class="tag-empty">none captured</div>'}</div>
        </div>
        """

    reliable_cards = "".join(card(n) for n in sorted(reliable_names, key=lambda n: -per_name[n]["count"]))
    ambiguous_cards = "".join(card(n) for n in ambiguous_names)

    return HTML_TEMPLATE.replace("__TITLE__", esc(title)) \
        .replace("__FILES_SCANNED__", str(files_scanned)) \
        .replace("__TOTAL_HITS__", str(total_hits)) \
        .replace("__RELIABLE_CARDS__", reliable_cards or '<p class="tag-empty">no reliable-name mentions found</p>') \
        .replace("__AMBIGUOUS_CARDS__", ambiguous_cards or '<p class="tag-empty">no ambiguous-name mentions found</p>')


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<style>
  :root {
    --bg: #05080a; --bg-panel: #0b1114; --phosphor: #39ff8f;
    --phosphor-dim: #1f7a4c; --amber: #ffb238; --ink: #c9f3d8; --ink-dim: #6f9c85;
    --mono: 'Courier New', ui-monospace, Menlo, Consolas, monospace;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--ink); font-family: var(--mono);
    padding: 28px 20px 80px;
    background-image: repeating-linear-gradient(0deg, rgba(57,255,143,0.035) 0px, rgba(57,255,143,0.035) 1px, transparent 1px, transparent 3px);
  }
  header { max-width: 1100px; margin: 0 auto 26px; border-bottom: 1px solid var(--phosphor-dim); padding-bottom: 14px; }
  .boot-line { color: var(--phosphor-dim); font-size: 12px; }
  h1 { font-size: 20px; color: var(--phosphor); text-shadow: 0 0 8px rgba(57,255,143,0.4); margin: 6px 0 4px; }
  .subtitle { color: var(--ink-dim); font-size: 12px; }
  main { max-width: 1100px; margin: 0 auto; }
  .section-title { color: var(--amber); font-size: 13px; text-transform: uppercase; letter-spacing: 0.1em;
    margin: 30px 0 14px; border-bottom: 1px dashed var(--phosphor-dim); padding-bottom: 6px; }
  .warn-global { background: #2a1a0a; border: 1px solid #ff9f43; color: #ffb238; font-size: 12px; padding: 10px 14px; margin-bottom: 10px; }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 18px; }
  .collab-card { background: var(--bg-panel); border: 1px solid var(--phosphor-dim); border-left-width: 4px; padding: 14px 16px; }
  .collab-header { font-size: 15px; font-weight: bold; display: flex; justify-content: space-between; }
  .collab-count { font-size: 11px; color: var(--ink-dim); font-weight: normal; }
  .collab-sub { font-size: 10px; color: var(--ink-dim); margin: 4px 0 10px; }
  .collab-section-label { font-size: 10px; color: var(--ink-dim); text-transform: uppercase; letter-spacing: 0.08em; margin: 10px 0 4px; }
  .warn { background: #2a1a0a; border: 1px solid #ff9f43; color: #ffb238; font-size: 10px; padding: 6px 8px; margin: 4px 0; }
  .tag-cloud { line-height: 2; }
  .tag { margin-right: 8px; display: inline-block; }
  .tag-empty { color: var(--ink-dim); font-size: 11px; font-style: italic; }
  .tone-row { display: flex; align-items: center; gap: 6px; font-size: 10px; margin: 2px 0; }
  .tone-label { width: 72px; color: var(--ink-dim); }
  .tone-bar-bg { flex: 1; background: #111; height: 6px; }
  .tone-bar-fill { height: 6px; }
  .tone-count { width: 20px; text-align: right; color: var(--ink-dim); }
  .samples { max-height: 220px; overflow-y: auto; border-top: 1px dashed var(--phosphor-dim); padding-top: 6px; }
  .sample { margin-bottom: 8px; }
  .sample-meta { font-size: 9px; color: var(--phosphor-dim); }
  .sample-text { font-size: 11px; color: var(--ink); }
  footer { max-width: 1100px; margin: 30px auto 0; color: var(--ink-dim); font-size: 11px; text-align: center; }
</style>
</head>
<body>
<header>
  <div class="boot-line">SYSTEM: collaborator_scan.py :: OFFLINE PARSE :: __FILES_SCANNED__ FILES / __TOTAL_HITS__ HITS</div>
  <h1>__TITLE__</h1>
  <div class="subtitle">mention frequency, context vocabulary, and tone -- per AI collaborator, across sessions and notes</div>
</header>
<main>
  <div class="section-title">reliable name matches</div>
  <div class="cards">__RELIABLE_CARDS__</div>

  <div class="section-title">ambiguous matches (noisy -- read the warning on each)</div>
  <div class="warn-global">"Jim" and bare "Vibe" collide with everyday language and other content
    in scattered notes. Counts below are upper bounds, not clean signal -- check the sample hits
    before drawing conclusions.</div>
  <div class="cards">__AMBIGUOUS_CARDS__</div>
</main>
<footer>raw hits also written to collaborator_hits.jsonl next to this report -- grep it directly for anything not shown here</footer>
</body>
</html>
"""


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Scan Vibe sessions + notes for AI-collaborator mentions.")
    ap.add_argument("roots", nargs="+", help="One or more directories to scan recursively")
    ap.add_argument("-o", "--output", default="collaborator_report.html")
    ap.add_argument("--title", default="COLLABORATOR MENTION SCAN")
    ap.add_argument("--extensions", default="jsonl,txt,md",
                     help="Comma-separated extensions to scan (default: jsonl,txt,md)")
    ap.add_argument("--context-lines", type=int, default=1,
                     help="Lines/messages of context to capture around each hit")
    args = ap.parse_args()

    extensions = {e.strip().lower() for e in args.extensions.split(",") if e.strip()}
    for r in args.roots:
        if not os.path.isdir(r):
            print(f"error: {r} is not a directory", file=sys.stderr)
            sys.exit(1)

    print(f"scanning {len(args.roots)} root(s) for extensions {sorted(extensions)} ...")
    hits, files_scanned = scan_all(args.roots, extensions, args.context_lines)
    print(f"  files scanned: {files_scanned}")
    print(f"  total hits: {len(hits)}")

    per_name = build_per_name_data(hits)
    for name in ALL_NAMES:
        if per_name.get(name, {}).get("count", 0):
            tag = " [AMBIGUOUS]" if per_name[name]["ambiguous"] else ""
            print(f"    {name}{tag}: {per_name[name]['count']}")

    hits_path = os.path.join(os.path.dirname(os.path.abspath(args.output)) or ".", "collaborator_hits.jsonl")
    with open(hits_path, "w") as f:
        for h in hits:
            f.write(json.dumps(h) + "\n")
    print(f"wrote raw hits: {hits_path}")

    html_doc = render_html(per_name, args.title, files_scanned, len(hits))
    with open(args.output, "w") as f:
        f.write(html_doc)
    print(f"wrote report: {args.output}")


if __name__ == "__main__":
    main()
