"""
[DNA_TAG]
ORIGIN: Moto4_A9
PILLAR: valet_concierge
PATH: collaborator_scan_fixed.py
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
word tags, tone tally, raw sample quotes, AND a full 3D interactive city
visualisation (Three.js) where each collaborator is a building.

Also writes a companion collaborator_hits.jsonl with EVERY hit (name,
source file, timestamp, full context) so you can grep/filter the raw data
yourself -- "grab everything that said Claude" as a literal filterable file.

No third-party Python dependencies. Pure stdlib.

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

# REMOVED "frustration" entirely -- no more false accusations.
TONE_KEYWORDS = {
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
    "humor": "#f1c40f", "urgency": "#ff9f43",
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
# Author detection patterns
# --------------------------------------------------------------------------

# Matches lines like "Claude:", "c:", "me:", "m:", "Gemini:", "g:", etc.
AUTHOR_PATTERNS = [
    # Full model name followed by colon
    re.compile(r"^\s*(Claude|Gemini|Mistral|Vibe\s*CLI|KIMI|DeepSeek|Qwen|GPT|Copilot)\s*:\s*(.*)", re.IGNORECASE),
    # Single letter model aliases: c, g, m, v, k, d, q, p (for copilot)
    re.compile(r"^\s*([cgmvkdqp])\s*:\s*(.*)", re.IGNORECASE),
    # "me" or "m" followed by colon
    re.compile(r"^\s*(me|i)\s*:\s*(.*)", re.IGNORECASE),
    re.compile(r"^\s*m\s*:\s*(.*)", re.IGNORECASE),
]

MODEL_ALIASES = {
    'c': 'Claude', 'claude': 'Claude',
    'g': 'Gemini', 'gemini': 'Gemini',
    'm': 'Mistral', 'mistral': 'Mistral',
    'v': 'Vibe CLI', 'vibe': 'Vibe CLI', 'vibe cli': 'Vibe CLI',
    'k': 'KIMI', 'kimi': 'KIMI',
    'd': 'DeepSeek', 'deepseek': 'DeepSeek',
    'q': 'Qwen', 'qwen': 'Qwen',
    'p': 'Copilot', 'copilot': 'Copilot',
}


def detect_author(line_text):
    """
    Try to detect if a line has an author prefix.
    Returns (author_type, content) where author_type is:
      - a model name string (e.g. "Claude", "Gemini")
      - "user" for "me:", "m:", "i:"
      - None if no prefix detected
    """
    line = line_text.strip()
    # Pattern 1: full model name
    m = AUTHOR_PATTERNS[0].match(line)
    if m:
        name = m.group(1).strip()
        return (MODEL_ALIASES.get(name.lower(), name.title()), m.group(2).strip())
    # Pattern 2: single letter alias
    m = AUTHOR_PATTERNS[1].match(line)
    if m:
        alias = m.group(1).lower()
        content = m.group(2).strip()
        model = MODEL_ALIASES.get(alias)
        if model:
            return (model, content)
    # Pattern 3: "me" or "i"
    m = AUTHOR_PATTERNS[2].match(line)
    if m:
        return ("user", m.group(2).strip())
    # Pattern 4: bare "m:" (ambiguous, check if it looks like a model alias or "me")
    m = AUTHOR_PATTERNS[3].match(line)
    if m:
        content = m.group(1).strip()
        # Heuristic: if content starts with model-like words, treat as model
        return ("user", content)
    return (None, line_text)


def split_text_by_author(text):
    """
    Split a block of text into (author, content) segments.
    Returns list of tuples. If no author detected, returns [(None, text)].
    """
    lines = text.split('\n')
    segments = []
    current_author = None
    current_lines = []

    for line in lines:
        author, content = detect_author(line)
        if author is not None:
            # Flush previous segment
            if current_lines:
                segments.append((current_author, '\n'.join(current_lines)))
            current_author = author
            current_lines = [content]
        else:
            current_lines.append(line)

    if current_lines:
        segments.append((current_author, '\n'.join(current_lines)))

    return segments if segments else [(None, text)]


# --------------------------------------------------------------------------
# Sentiment / nuance scoring
# --------------------------------------------------------------------------

SENTIMENT_MARKERS = {
    "sarcasm": [
        "sure", "right", "obviously", "clearly", "totally", "definitely",
        "absolutely", "of course", "great", "wonderful", "fantastic",
        "love that for me", "just what i needed", "perfect", "brilliant",
        "oh great", "oh wonderful", "oh perfect", "gee", "gosh",
        "how nice", "lovely", "marvelous", "spectacular",
    ],
    "frustration": [
        "ugh", "argh", "damn", "hell", "stupid", "ridiculous",
        "annoying", "irritating", "waste of time", "broken", "useless",
        "why won't", "why doesnt", "why cant", "for fucks sake",
        "ffs", "wtf", "seriously", "come on", "give me a break",
    ],
    "excitement": [
        "yes!", "woohoo", "lets go", "crushed it", "nailed it",
        "perfect!", "exactly!", "brilliant!", "amazing!", "incredible!",
        "holy shit", "no way", "unreal", "insane", "fire",
    ],
    "dismissive": [
        "whatever", "who cares", "not my problem", "not interested",
        "boring", "skip", "tl;dr", "too long", "dont care",
        "meh", "pass", "next", "moving on",
    ],
    "self_deprecating": [
        "im an idiot", "im stupid", "i suck", "im the worst",
        "of course i did", "typical me", "story of my life",
        "why do i even", "what did i expect", "par for the course",
    ],
    "affection": [
        "youre the best", "love you", "appreciate you", "youre amazing",
        "you rock", "youre awesome", "youre incredible", "youre a lifesaver",
        "best assistant", "favorite", "my favorite",
    ],
}

SENTIMENT_COLORS = {
    "sarcasm": "#ff6b6b",
    "frustration": "#ff4757",
    "excitement": "#2ed573",
    "dismissive": "#a4b0be",
    "self_deprecating": "#ffa502",
    "affection": "#ff69b4",
}


def score_sentiment(text_lower):
    """
    Score text for sentiment/nuance markers.
    Returns dict of {sentiment: count} and overall intensity (0-100).
    """
    scores = Counter()
    for sentiment, phrases in SENTIMENT_MARKERS.items():
        for phrase in phrases:
            scores[sentiment] += text_lower.count(phrase)

    total = sum(scores.values())
    # Intensity: how many markers per 100 words (capped at 100)
    words = len(text_lower.split())
    intensity = min(100, (total / max(1, words)) * 100) if words else 0

    return dict(scores), intensity


def dominant_sentiment(sentiment_scores):
    """Return the dominant sentiment key or None."""
    if not sentiment_scores:
        return None
    return max(sentiment_scores, key=sentiment_scores.get)


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

        # Author/word count analysis
        text_lower = text.lower()
        sentiment_scores, sentiment_intensity = score_sentiment(text_lower)

        # Try to detect if this is model or user speaking
        detected_author = None
        if obj.get("role") == "user":
            detected_author = "user"
        elif obj.get("role") == "assistant":
            detected_author = "assistant"  # generic, will try to match later

        for name, ambiguous in matches:
            hits_out.append({
                "name": name,
                "ambiguous": ambiguous,
                "source": path,
                "source_type": "vibe_session",
                "role": obj.get("role"),
                "timestamp": session_ts.isoformat() if session_ts else None,
                "context": context,
                "sentiment_scores": sentiment_scores,
                "sentiment_intensity": sentiment_intensity,
                "detected_author": detected_author,
                "word_count": len(tokenize(text)),
            })


def scan_text_file(path, context_lines, hits_out):
    mtime = file_mtime(path)
    try:
        with open(path, "r", errors="ignore") as f:
            raw_text = f.read()
            lines = raw_text.split('\n')
    except OSError:
        return

    # Try to split entire file by author first for word count tracking
    segments = split_text_by_author(raw_text)
    segment_map = {}  # line_idx -> (author, content)

    # Build a rough line-to-author mapping
    line_idx = 0
    for author, content in segments:
        content_lines = content.split('\n')
        for _ in content_lines:
            if line_idx < len(lines):
                segment_map[line_idx] = (author, content)
                line_idx += 1

    for i, line in enumerate(lines):
        matches = find_matches(line)
        if not matches:
            continue
        lo = max(0, i - context_lines)
        hi = min(len(lines), i + context_lines + 1)
        context = " ".join(l.strip() for l in lines[lo:hi] if l.strip())[:800]

        text_lower = line.lower()
        sentiment_scores, sentiment_intensity = score_sentiment(text_lower)

        # Author detection
        detected_author, stripped_content = detect_author(line)
        if detected_author is None:
            # Try to infer from segment
            detected_author = segment_map.get(i, (None, None))[0]

        # Word count: if we stripped an author prefix, count the content only
        wc = len(tokenize(stripped_content if stripped_content else line))

        for name, ambiguous in matches:
            hits_out.append({
                "name": name,
                "ambiguous": ambiguous,
                "source": path,
                "source_type": "note_file",
                "line_no": i + 1,
                "timestamp": mtime.isoformat() if mtime else None,
                "context": context,
                "sentiment_scores": sentiment_scores,
                "sentiment_intensity": sentiment_intensity,
                "detected_author": detected_author,
                "word_count": wc,
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
        "sentiment": Counter(),
        "sentiment_intensity_total": 0.0,
        "sentiment_intensity_count": 0,
        "model_word_count": 0,
        "user_word_count": 0,
        "unknown_word_count": 0,
        "author_hits": Counter(),  # tracks which author said what
    })
    for h in hits:
        d = per_name[h["name"]]
        d["ambiguous"] = h["ambiguous"]
        d["count"] += 1
        d["by_source_type"][h["source_type"]] += 1

        # Word count by author
        author = h.get("detected_author")
        wc = h.get("word_count", 0)
        if author == "user":
            d["user_word_count"] += wc
        elif author in ALL_NAMES or author == "assistant":
            d["model_word_count"] += wc
        else:
            d["unknown_word_count"] += wc

        if author:
            d["author_hits"][author] += 1

        if h["timestamp"]:
            date_key = h["timestamp"][:10]
            d["by_date"][date_key] += 1
        ctx_lower = h["context"].lower()
        words = [w for w in tokenize(h["context"]) if w not in STOPWORDS and len(w) > 2]
        d["words"].update(words)
        d["tone"].update(tone_hits(ctx_lower))

        # Sentiment aggregation
        for sent, score in h.get("sentiment_scores", {}).items():
            d["sentiment"][sent] += score
        if h.get("sentiment_intensity") is not None:
            d["sentiment_intensity_total"] += h["sentiment_intensity"]
            d["sentiment_intensity_count"] += 1

        if len(d["samples"]) < 40:
            d["samples"].append(h)
    return per_name


# --------------------------------------------------------------------------
# HTML rendering (now with 3D city + sentiment slider)
# --------------------------------------------------------------------------

def esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def render_html(per_name, title, files_scanned, total_hits):
    reliable_names = [n for n in RELIABLE if per_name.get(n, {}).get("count", 0) > 0]
    ambiguous_names = [n for n in AMBIGUOUS if per_name.get(n, {}).get("count", 0) > 0]

    # Build data for the 3D city
    city_data = []
    for name, d in per_name.items():
        if d["count"] == 0:
            continue
        # dominant tone
        if d["tone"]:
            dom_tone = max(d["tone"], key=d["tone"].get)
            dom_color = TONE_COLORS.get(dom_tone, "#39ff8f")
        else:
            dom_tone = "none"
            dom_color = "#39ff8f"

        # dominant sentiment
        dom_sent = dominant_sentiment(d["sentiment"])
        sent_color = SENTIMENT_COLORS.get(dom_sent, "#39ff8f") if dom_sent else dom_color

        # avg sentiment intensity
        avg_intensity = d["sentiment_intensity_total"] / max(1, d["sentiment_intensity_count"])

        city_data.append({
            "name": name,
            "count": d["count"],
            "tone": dom_tone,
            "color": dom_color,
            "sentiment": dom_sent or "none",
            "sentiment_color": sent_color,
            "sentiment_intensity": round(avg_intensity, 1),
            "ambiguous": d["ambiguous"],
            "model_wc": d["model_word_count"],
            "user_wc": d["user_word_count"],
            "unknown_wc": d["unknown_word_count"],
        })

    # Generate the 3D city JavaScript
    city_js = generate_3d_city_js(city_data)

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

        # Sentiment bars
        sent_bars = ""
        if d["sentiment"]:
            max_sent = max(d["sentiment"].values())
            sent_bars = "".join(
                f'<div class="tone-row"><span class="tone-label">{esc(cat)}</span>'
                f'<div class="tone-bar-bg"><div class="tone-bar-fill" '
                f'style="width:{min(100, (d["sentiment"].get(cat,0)/max_sent)*100)}%; background:{SENTIMENT_COLORS.get(cat, "#888")}"></div></div>'
                f'<span class="tone-count">{d["sentiment"].get(cat,0)}</span></div>'
                for cat in SENTIMENT_MARKERS if d["sentiment"].get(cat, 0) > 0
            )
        else:
            sent_bars = '<span class="tag-empty">no sentiment markers detected</span>'

        # Word count breakdown
        total_wc = d["model_word_count"] + d["user_word_count"] + d["unknown_word_count"]
        wc_html = f"""
        <div class="wc-block">
          <div class="wc-row"><span class="wc-label">model words:</span><span class="wc-val" style="color:#39ff8f">{d['model_word_count']:,}</span></div>
          <div class="wc-row"><span class="wc-label">your words:</span><span class="wc-val" style="color:#ffb238">{d['user_word_count']:,}</span></div>
          <div class="wc-row"><span class="wc-label">unknown:</span><span class="wc-val" style="color:#6f9c85">{d['unknown_word_count']:,}</span></div>
          <div class="wc-row"><span class="wc-label">total:</span><span class="wc-val">{total_wc:,}</span></div>
        </div>
        """ if total_wc > 0 else '<span class="tag-empty">no author-prefixed text detected for word count</span>'

        # Author hit breakdown
        author_html = ""
        if d["author_hits"]:
            author_items = ", ".join(f"{esc(k)}: {v}" for k, v in sorted(d["author_hits"].items(), key=lambda x: -x[1]))
            author_html = f'<div class="collab-sub">detected authors: {author_items}</div>'

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
            f'{"(" + s["timestamp"][:10] + ")" if s.get("timestamp") else ""}'
            f'{" [" + esc(str(s.get("detected_author"))) + "]" if s.get("detected_author") else ""}'
            f'{" intensity:" + str(round(s.get("sentiment_intensity", 0), 1)) if s.get("sentiment_intensity") else ""}'
            f'</div>'
            f'<div class="sample-text">{esc(s["context"][:300])}</div></div>'
            for s in d["samples"][:12]
        )

        ambiguous_banner = (
            '<div class="warn">AMBIGUOUS MATCH -- this string collides with everyday '
            'language. Treat counts as noisy upper bounds, not clean signal.</div>'
            if d["ambiguous"] else ""
        )

        src_breakdown = ", ".join(f"{k}: {v}" for k, v in d["by_source_type"].items())

        # Sentiment intensity gauge
        avg_int = d["sentiment_intensity_total"] / max(1, d["sentiment_intensity_count"])
        intensity_gauge = f"""
        <div class="intensity-row">
          <span class="intensity-label">nuance intensity</span>
          <div class="intensity-track">
            <div class="intensity-fill" style="width:{min(100, avg_int)}%; background: {sent_color if d['sentiment'] else '#6f9c85'}"></div>
          </div>
          <span class="intensity-val">{avg_int:.1f}</span>
        </div>
        """ if d["sentiment_intensity_count"] > 0 else ""

        return f"""
        <div class="collab-card" style="border-color:{color}">
          <div class="collab-header" style="color:{color}">{esc(name)}
            <span class="collab-count">{d['count']} mentions</span></div>
          {ambiguous_banner}
          <div class="collab-sub">sources: {src_breakdown}</div>
          {author_html}
          {intensity_gauge}
          <div class="collab-section-label">word count breakdown</div>
          {wc_html}
          <div class="collab-section-label">mentions over time</div>
          {spark}
          <div class="collab-section-label">context vocabulary</div>
          <div class="tag-cloud">{word_tags}</div>
          <div class="collab-section-label">tone in context</div>
          <div class="tone-block">{tone_bars}</div>
          <div class="collab-section-label">sentiment / nuance markers</div>
          <div class="tone-block">{sent_bars}</div>
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
        .replace("__AMBIGUOUS_CARDS__", ambiguous_cards or '<p class="tag-empty">no ambiguous-name mentions found</p>') \
        .replace("__3D_CITY_JS__", city_js)


def generate_3d_city_js(city_data):
    """Return a complete JavaScript block that builds the 3D city using Three.js."""
    data_json = json.dumps(city_data)
    return f"""
    <script type="importmap">
    {{
        "imports": {{
            "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
            "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
        }}
    }}
    </script>
    <script type="module">
    import * as THREE from 'three';
    import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

    const cityData = {data_json};

    const container = document.getElementById('city-container');
    const width = container.clientWidth;
    const height = window.innerHeight * 0.6;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x05080a);
    scene.fog = new THREE.FogExp2(0x05080a, 0.08);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(10, 8, 14);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(width, height);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.target.set(0, 1, 0);
    controls.maxPolarAngle = Math.PI / 2.1;  // Don't go below ground
    controls.minDistance = 5;
    controls.maxDistance = 30;

    // lights
    const ambientLight = new THREE.AmbientLight(0x203040, 0.6);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight.position.set(8, 15, 10);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 1024;
    dirLight.shadow.mapSize.height = 1024;
    scene.add(dirLight);

    const backLight = new THREE.DirectionalLight(0x4488ff, 0.5);
    backLight.position.set(-8, 8, -10);
    scene.add(backLight);

    // ground -- reflective dark surface
    const groundGeo = new THREE.PlaneGeometry(40, 40);
    const groundMat = new THREE.MeshStandardMaterial({{
        color: 0x0a1215,
        roughness: 0.1,
        metalness: 0.8,
        envMapIntensity: 1.0
    }});
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.05;
    ground.receiveShadow = true;
    scene.add(ground);

    // subtle grid on ground
    const grid = new THREE.GridHelper(40, 40, 0x1a3a2a, 0x0d1f15);
    grid.position.y = 0.01;
    scene.add(grid);

    // buildings
    const maxCount = Math.max(1, ...cityData.map(d => d.count));
    const spacing = 3.0;
    const total = cityData.length;
    const cols = Math.ceil(Math.sqrt(total * 1.5));
    const rows = Math.ceil(total / cols);

    const meshes = [];
    const labels = [];

    cityData.forEach((d, i) => {{
        const col = i % cols;
        const row = Math.floor(i / cols);
        const x = col * spacing - ((cols - 1) * spacing) / 2;
        const z = row * spacing - ((rows - 1) * spacing) / 2;
        const height = 0.5 + (d.count / maxCount) * 5.0;

        const color = new THREE.Color(d.color);
        const sentColor = d.sentiment_color ? new THREE.Color(d.sentiment_color) : color;

        // Main building -- slightly tapered for style
        const geo = new THREE.BoxGeometry(0.9, height, 0.9);
        const mat = new THREE.MeshStandardMaterial({{
            color: color,
            emissive: sentColor,
            emissiveIntensity: 0.15 + (d.sentiment_intensity / 100) * 0.4,
            roughness: 0.2,
            metalness: 0.6
        }});
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.set(x, height / 2, z);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        mesh.userData = {{ name: d.name, count: d.count, tone: d.tone, sentiment: d.sentiment, intensity: d.sentiment_intensity }};
        scene.add(mesh);
        meshes.push(mesh);

        // Top cap -- brighter emissive
        const capGeo = new THREE.BoxGeometry(0.7, 0.15, 0.7);
        const capMat = new THREE.MeshBasicMaterial({{ color: sentColor }});
        const cap = new THREE.Mesh(capGeo, capMat);
        cap.position.set(x, height + 0.075, z);
        scene.add(cap);

        // Base ring
        const ringGeo = new THREE.RingGeometry(0.6, 0.8, 32);
        const ringMat = new THREE.MeshBasicMaterial({{ color: color, transparent: true, opacity: 0.4, side: THREE.DoubleSide }});
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = -Math.PI / 2;
        ring.position.set(x, 0.02, z);
        scene.add(ring);

        // Label sprite
        const canvas = document.createElement('canvas');
        canvas.width = 320;
        canvas.height = 80;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'rgba(5, 8, 10, 0.85)';
        ctx.beginPath();
        ctx.roundRect(4, 4, canvas.width - 8, canvas.height - 8, 10);
        ctx.fill();
        ctx.strokeStyle = d.color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.roundRect(4, 4, canvas.width - 8, canvas.height - 8, 10);
        ctx.stroke();
        ctx.font = 'bold 22px "Courier New", monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = '#c9f3d8';
        ctx.fillText(d.name, canvas.width / 2, canvas.height / 2 - 10);
        ctx.font = '16px "Courier New", monospace';
        ctx.fillStyle = '#6f9c85';
        ctx.fillText(d.count + ' mentions', canvas.width / 2, canvas.height / 2 + 14);
        if (d.sentiment && d.sentiment !== 'none') {{
            ctx.font = '12px "Courier New", monospace';
            ctx.fillStyle = d.sentiment_color;
            ctx.fillText(d.sentiment + ' (' + d.sentiment_intensity + ')', canvas.width / 2, canvas.height / 2 + 32);
        }}
        const texture = new THREE.CanvasTexture(canvas);
        const spriteMat = new THREE.SpriteMaterial({{ map: texture, transparent: true, depthTest: false }});
        const sprite = new THREE.Sprite(spriteMat);
        sprite.position.set(x, height + 1.2, z);
        sprite.scale.set(2.5, 0.625, 1);
        scene.add(sprite);
        labels.push(sprite);

        // Vertical glow beam
        const beamGeo = new THREE.CylinderGeometry(0.05, 0.3, height * 0.6, 8, 1, true);
        const beamMat = new THREE.MeshBasicMaterial({{
            color: sentColor,
            transparent: true,
            opacity: 0.08,
            side: THREE.DoubleSide,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        }});
        const beam = new THREE.Mesh(beamGeo, beamMat);
        beam.position.set(x, height * 0.7, z);
        scene.add(beam);
    }});

    // Starfield
    const starsGeo = new THREE.BufferGeometry();
    const starCount = 2000;
    const pos = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount * 3; i++) {{
        pos[i] = (Math.random() - 0.5) * 300;
    }}
    starsGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const starsMat = new THREE.PointsMaterial({{ color: 0xffffff, size: 0.12, transparent: true, opacity: 0.6, sizeAttenuation: true }});
    const stars = new THREE.Points(starsGeo, starsMat);
    scene.add(stars);

    // Floating particles (around buildings)
    const particleCount = 600;
    const particleGeo = new THREE.BufferGeometry();
    const pPos = new Float32Array(particleCount * 3);
    const pVel = [];
    for (let i = 0; i < particleCount; i++) {{
        pPos[i * 3] = (Math.random() - 0.5) * 20;
        pPos[i * 3 + 1] = Math.random() * 8;
        pPos[i * 3 + 2] = (Math.random() - 0.5) * 20;
        pVel.push({{
            x: (Math.random() - 0.5) * 0.01,
            y: (Math.random() - 0.5) * 0.005,
            z: (Math.random() - 0.5) * 0.01
        }});
    }}
    particleGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
    const particleMat = new THREE.PointsMaterial({{ color: 0x39ff8f, size: 0.04, transparent: true, opacity: 0.4, sizeAttenuation: true }});
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // Raycaster for hover
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let hoveredMesh = null;

    container.addEventListener('mousemove', (e) => {{
        const rect = container.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
    }});

    // Animation loop
    let time = 0;
    function animate() {{
        requestAnimationFrame(animate);
        time += 0.01;
        controls.update();

        // gentle rotation of stars
        stars.rotation.y += 0.00015;

        // particle drift
        const positions = particles.geometry.attributes.position.array;
        for (let i = 0; i < particleCount; i++) {{
            positions[i * 3] += pVel[i].x + Math.sin(time + i) * 0.002;
            positions[i * 3 + 1] += pVel[i].y;
            positions[i * 3 + 2] += pVel[i].z + Math.cos(time + i) * 0.002;
            // wrap around
            if (positions[i * 3 + 1] > 10) positions[i * 3 + 1] = 0;
            if (positions[i * 3 + 1] < 0) positions[i * 3 + 1] = 10;
        }}
        particles.geometry.attributes.position.needsUpdate = true;
        particles.rotation.y += 0.0003;

        // Hover effect
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(meshes);
        if (intersects.length > 0) {{
            const mesh = intersects[0].object;
            if (hoveredMesh !== mesh) {{
                if (hoveredMesh) hoveredMesh.material.emissiveIntensity = hoveredMesh.userData.baseEmissive || 0.15;
                hoveredMesh = mesh;
                mesh.userData.baseEmissive = mesh.material.emissiveIntensity;
                mesh.material.emissiveIntensity = 0.8;
            }}
        }} else {{
            if (hoveredMesh) {{
                hoveredMesh.material.emissiveIntensity = hoveredMesh.userData.baseEmissive || 0.15;
                hoveredMesh = null;
            }}
        }}

        renderer.render(scene, camera);
    }}
    animate();

    // handle resize
    window.addEventListener('resize', () => {{
        const w = container.clientWidth;
        const h = window.innerHeight * 0.6;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
    }});
    </script>
    """


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
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 18px; }
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

  /* Word count block */
  .wc-block { background: rgba(0,0,0,0.3); padding: 8px 10px; border-radius: 3px; margin: 4px 0; }
  .wc-row { display: flex; justify-content: space-between; font-size: 11px; margin: 2px 0; }
  .wc-label { color: var(--ink-dim); }
  .wc-val { font-weight: bold; }

  /* Intensity slider */
  .intensity-row { display: flex; align-items: center; gap: 8px; font-size: 10px; margin: 6px 0; }
  .intensity-label { width: 90px; color: var(--ink-dim); text-transform: uppercase; letter-spacing: 0.05em; }
  .intensity-track { flex: 1; background: #111; height: 8px; border-radius: 4px; overflow: hidden; }
  .intensity-fill { height: 100%; border-radius: 4px; transition: width 0.3s ease; }
  .intensity-val { width: 36px; text-align: right; color: var(--ink-dim); }

  #city-container {
    width: 100%;
    height: 60vh;
    min-height: 400px;
    border: 1px solid var(--phosphor-dim);
    border-radius: 4px;
    background: #05080a;
    margin: 20px 0;
    cursor: crosshair;
  }
  .city-label { color: var(--amber); font-size: 13px; text-transform: uppercase; letter-spacing: 0.1em;
    margin: 30px 0 10px; border-bottom: 1px dashed var(--phosphor-dim); padding-bottom: 6px; }
  footer { max-width: 1100px; margin: 30px auto 0; color: var(--ink-dim); font-size: 11px; text-align: center; }
</style>
</head>
<body>
<header>
  <div class="boot-line">SYSTEM: collaborator_scan.py :: OFFLINE PARSE :: __FILES_SCANNED__ FILES / __TOTAL_HITS__ HITS</div>
  <h1>__TITLE__</h1>
  <div class="subtitle">mention frequency, context vocabulary, tone, sentiment nuance, and word count -- per AI collaborator, across sessions and notes</div>
</header>
<main>
  <div class="section-title">reliable name matches</div>
  <div class="cards">__RELIABLE_CARDS__</div>

  <div class="section-title">ambiguous matches (noisy -- read the warning on each)</div>
  <div class="warn-global">"Jim" and bare "Vibe" collide with everyday language and other content
    in scattered notes. Counts below are upper bounds, not clean signal -- check the sample hits
    before drawing conclusions.</div>
  <div class="cards">__AMBIGUOUS_CARDS__</div>

  <div class="city-label">&#10022; 3D collaboration city (hover & drag) &#10022;</div>
  <div id="city-container"></div>
  __3D_CITY_JS__
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
            d = per_name[name]
            wc_info = f" | model:{d['model_word_count']} user:{d['user_word_count']}"
            print(f"    {name}{tag}: {d['count']} mentions{wc_info}")

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
