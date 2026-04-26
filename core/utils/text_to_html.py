"""
Text-to-HTML Converter
======================
Converts plain text with custom block syntax into formatted HTML.

Supported blocks:
  [fill N]                          → text input (id="questionN")
  [mchq N {A ...}{B ...}...]        → single-choice MCQ
  [mchm N M {A ...}{B ...}...]      → multi-answer MCQ (N, M = question IDs)
  [match ({N ...}{M ...}) ({A ...}{B ...})] → drag-and-drop matching
  [drop ({1 text}{2 text}...) ({I}{II}{III}...)] → dropdown per question row
  [img filename.ext]                → inline image (matched by filename)
  [box ...]                         → bordered text container
  [guide ...]                       → guide/instruction container

Inline formatting (works everywhere):
  *text*    → <strong>
  //text//    → <em>
  __text__  → <u>
"""

import re
from typing import Optional


# ---------------------------------------------------------------------------
# Inline formatter
# ---------------------------------------------------------------------------

def apply_inline_formatting(text: str) -> str:
    """Apply *bold*, /italic/, __underline__ inline formatting."""
    # Bold: *...*  (non-greedy, dots may include newlines)
    text = re.sub(r'\*(.+?)\*', r'<strong>\1</strong>', text, flags=re.DOTALL)
    # Italic: //…//
    text = re.sub(r'//(.+?)//', r'<em>\1</em>', text, flags=re.DOTALL)
    # Underline: __…__
    text = re.sub(r'__(.+?)__', r'<u>\1</u>', text, flags=re.DOTALL)
    return text


# ---------------------------------------------------------------------------
# Option parser  {X text} ... {Y text}
# ---------------------------------------------------------------------------

def parse_options(raw: str) -> list[tuple[str, str]]:
    """
    Parse a sequence of {KEY text} chunks.
    Returns list of (key, text) pairs.
    The key is the first non-space token; the rest is the option text.
    """
    options = []
    for m in re.finditer(r'\{([^}]+)\}', raw, flags=re.DOTALL):
        content = m.group(1).strip()
        parts = content.split(None, 1)          # split on first whitespace
        if parts:
            key  = parts[0]
            text = parts[1].strip() if len(parts) > 1 else ''
            options.append((key, text))
    return options


# ---------------------------------------------------------------------------
# Block renderers
# ---------------------------------------------------------------------------

def render_fill(question_id: str) -> str:
    qid = f"question{question_id}"
    return (
        f'<input type="text" id="{qid}" name="{qid}" '
        f'class="fill-input" placeholder="{question_id}" '
        f'data-question-id="{question_id}" autocomplete="off">'
    )


def render_mchq(question_id: str, options: list[tuple[str, str]]) -> str:
    qid = f"question{question_id}"
    items = []
    for key, text in options:
        label_id = f"{qid}_{key}"
        items.append(
            f'  <li class="mchq-option">'
            f'<input type="radio" id="{label_id}" name="{qid}" value="{key}">'
            f'<label for="{label_id}">'
            f'<span class="option-key">{key}</span>'
            f'<span class="option-text">{apply_inline_formatting(text)}</span>'
            f'</label></li>'
        )
    inner = '\n'.join(items)
    return (
        f'<ul class="mchq" id="{qid}" data-question-id="{question_id}" '
        f'role="radiogroup">\n{inner}\n</ul>'
    )


def render_mchm(question_ids: list[str], options: list[tuple[str, str]]) -> str:
    """
    Multi-answer MCQ: one checkbox group per question_id.
    The options are shared; each checkbox is named after its question_id.
    When the user selects an option the value goes to the corresponding question.
    We render them side by side or stacked, one column per question slot.
    """
    # We render a single checkbox group; each checkbox stores its answer
    # for the FIRST question ID.  Extra IDs are stored as data attributes
    # so the JS / back-end can split the answer.
    primary_qid = f"question{question_ids[0]}"
    all_qids    = [f"question{q}" for q in question_ids]
    data_ids    = ' '.join(all_qids)

    items = []
    for key, text in options:
        label_id = f"{primary_qid}_{key}"
        items.append(
            f'  <li class="mchm-option">'
            f'<input type="checkbox" id="{label_id}" '
            f'name="{primary_qid}" value="{key}" '
            f'data-question-ids="{data_ids}">'
            f'<label for="{label_id}">'
            f'<span class="option-key">{key}</span>'
            f'<span class="option-text">{apply_inline_formatting(text)}</span>'
            f'</label></li>'
        )
    inner = '\n'.join(items)
    id_badges = ''.join(
        f'<span class="qid-badge">Q{q}</span>' for q in question_ids
    )
    return (
        f'<div class="mchm" data-question-ids="{data_ids}">'
        f'<div class="mchm-ids">{id_badges}</div>'
        f'<ul class="mchm-list" id="{primary_qid}">\n{inner}\n</ul>'
        f'</div>'
    )


def render_match(left_items: list[tuple[str, str]],
                 right_items: list[tuple[str, str]]) -> str:
    """
    Drag-and-drop matching.
    left_items  → drop zones (keyed by numeric question IDs)
    right_items → draggable chips (keyed by letters)
    """
    left_html = []
    for key, text in left_items:
        qid = f"question{key}"
        left_html.append(
            f'  <div class="match-left-row">'
            f'<div class="match-prompt">{apply_inline_formatting(text)}</div>'
            f'<div class="match-drop-zone" '
            f'     id="{qid}" '
            f'     data-question-id="{key}" '
            f'     data-accepts="chip" '
            f'     ondragover="matchDragOver(event)" '
            f'     ondrop="matchDrop(event)" '
            f'     ondragleave="matchDragLeave(event)">'
            f'<span class="drop-hint">Drop here</span>'
            f'</div>'
            f'</div>'
        )

    right_html = []
    for key, text in right_items:
        right_html.append(
            f'  <div class="match-chip" '
            f'       id="chip_{key}" '
            f'       draggable="true" '
            f'       data-value="{key}" '
            f'       ondragstart="matchDragStart(event)">'
            f'<span class="chip-key">{key}</span>'
            f'<span class="chip-text">{apply_inline_formatting(text)}</span>'
            f'</div>'
        )

    left_block  = '\n'.join(left_html)
    right_block = '\n'.join(right_html)

    return (
        f'<div class="match-widget">'
        f'<div class="match-left">\n{left_block}\n</div>'
        f'<div class="match-right">\n{right_block}\n</div>'
        f'</div>'
    )


def render_box(content: str) -> str:
    return (
        f'<div class="text-box">'
        f'{apply_inline_formatting(content.strip())}'
        f'</div>'
    )


def render_guide(content: str) -> str:
    # Try to split first line as title
    lines = content.strip().split('\n', 1)
    title = lines[0].strip()
    body  = lines[1].strip() if len(lines) > 1 else ''
    title_html = f'<div class="guide-title">{apply_inline_formatting(title)}</div>' if title else ''
    body_html  = f'<div class="guide-body">{apply_inline_formatting(body)}</div>'   if body  else ''
    return f'<div class="guide-box">{title_html}{body_html}</div>'


def render_drop(left_items: list[tuple[str, str]], options: list[str]) -> str:
    """
    Dropdown matching: each question row gets its own <select>.

    left_items  → list of (question_id, question_text)  e.g. [('1', 'Quest'), ('2', 'Quest 2')]
    options     → list of option label strings           e.g. ['I', 'II', 'III', 'IV', 'V']

    Renders every row as:
        <question_text>   [dropdown ▾]
    The <select> id/name is "question{id}" so collectAnswers() picks it up automatically.
    """
    rows_html = []
    for qid, text in left_items:
        full_qid = f"question{qid}"
        opts_html = '<option value="">—</option>'
        for opt in options:
            opts_html += f'<option value="{opt}">{opt}</option>'
        rows_html.append(
            f'<div class="drop-row">'
            f'<span class="drop-qnum">{qid}.</span>'
            f'<span class="drop-text">{apply_inline_formatting(text)}</span>'
            f'<select id="{full_qid}" name="{full_qid}" '
            f'class="drop-select" data-question-id="{qid}">'
            f'{opts_html}'
            f'</select>'
            f'</div>'
        )
    return f'<div class="drop-widget">{"".join(rows_html)}</div>'

def render_img(label: str, images: dict) -> str:
    url = images.get(label)
    if url:
        return (
            f'<div class="img-block">'
            f'<img src="{url}" class="img-insert" alt="{label}">'
            f'</div>'
        )
    return ''  # silently skip if label not found


# ---------------------------------------------------------------------------
# Master block parser
# ---------------------------------------------------------------------------

def extract_blocks(text: str) -> list[tuple[str, str]]:
    """
    Split the source text into a flat list of (kind, content) tokens.
    kind == 'text'  → literal text
    kind == 'block' → raw block content inside [...]
    """
    tokens = []
    i = 0
    n = len(text)
    buf = []

    while i < n:
        if text[i] == '[':
            # Flush buffered literal text
            if buf:
                tokens.append(('text', ''.join(buf)))
                buf = []
            # Find matching ]
            depth = 1
            j = i + 1
            while j < n and depth > 0:
                if text[j] == '[':
                    depth += 1
                elif text[j] == ']':
                    depth -= 1
                j += 1
            block_inner = text[i+1:j-1]
            tokens.append(('block', block_inner))
            i = j
        else:
            buf.append(text[i])
            i += 1

    if buf:
        tokens.append(('text', ''.join(buf)))

    return tokens


def parse_block(raw: str, images: dict = {}) -> str:
    raw = raw.strip()

    m = re.match(r'^fill\s+(\d+)\s*$', raw, re.DOTALL | re.IGNORECASE)
    if m:
        return render_fill(m.group(1))

    m = re.match(r'^mchq\s+(\d+)\s+(.+)$', raw, re.DOTALL | re.IGNORECASE)
    if m:
        return render_mchq(m.group(1), parse_options(m.group(2)))

    m = re.match(r'^mchm\s+((?:\d+\s+)+)(.+)$', raw, re.DOTALL | re.IGNORECASE)
    if m:
        return render_mchm(m.group(1).strip().split(), parse_options(m.group(2)))

    m = re.match(r'^match\s*\(([^)]+)\)\s*\(([^)]+)\)\s*$', raw, re.DOTALL | re.IGNORECASE)
    if m:
        return render_match(parse_options(m.group(1)), parse_options(m.group(2)))

    m = re.match(r'^box\s+(.+)$', raw, re.DOTALL | re.IGNORECASE)
    if m:
        return render_box(m.group(1))

    m = re.match(r'^guide\s+(.+)$', raw, re.DOTALL | re.IGNORECASE)
    if m:
        return render_guide(m.group(1))
    
    # ---- [drop ({1 text}{2 text}...) ({I}{II}...)] ----
    # Each {N text} in the first group becomes a question row with a dropdown.
    # Each {opt} in the second group becomes a <select> option.
    m = re.match(
        r'^drop\s*\(([^)]+)\)\s*\(([^)]+)\)\s*$',
        raw, re.DOTALL | re.IGNORECASE
    )
    if m:
        left_raw  = m.group(1)   # {1 Quest }{2 Quest 2}...
        opts_raw  = m.group(2)   # {I}{II}{III}...
        left_items = parse_options(left_raw)          # [(id, text), ...]
        opts_parsed = parse_options(opts_raw)         # [(label, extra_text), ...]
        # Combine label + any extra text into a single display string
        options = [f"{k} {t}".strip() for k, t in opts_parsed]
        return render_drop(left_items, options)

    # ---- [img label] ----
    m = re.match(r'^img\s+(\w+)\s*$', raw, re.IGNORECASE)
    if m:
        return render_img(m.group(1), images)

    return f'<!-- UNKNOWN BLOCK: [{raw}] -->'


# ---------------------------------------------------------------------------
# Plain text → paragraphs
# ---------------------------------------------------------------------------

def render_plain_text(text: str) -> str:
    """Convert literal text segments into <p> tags, preserving blank-line paragraphs."""
    paragraphs = re.split(r'\n{2,}', text)
    parts = []
    for para in paragraphs:
        para = para.strip()
        if para:
            # Single newlines within a paragraph become <br>
            para = para.replace('\n', '<br>\n')
            parts.append(f'<p>{apply_inline_formatting(para)}</p>')
    return '\n'.join(parts)


# ---------------------------------------------------------------------------
# Top-level converter
# ---------------------------------------------------------------------------

def convert(source: str, images: dict = {}) -> str:
    tokens = extract_blocks(source)
    result = []
    buffer = []

    def flush_buffer():
        if buffer:
            result.append(f'<p>{"".join(buffer)}</p>')
            buffer.clear()

    for kind, content in tokens:
        if kind == 'block':
            raw = content.strip()
            is_inline = bool(re.match(r'^fill\s+\d+', raw, re.IGNORECASE))
            if is_inline:
                buffer.append(parse_block(content, images))
            else:
                flush_buffer()
                result.append(parse_block(content, images))
        else:
            paragraphs = re.split(r'\n{2,}', content)
            for i, para in enumerate(paragraphs):
                para = para.strip()
                if not para:
                    if i > 0:
                        flush_buffer()
                    continue
                inline_text = apply_inline_formatting(para.replace('\n', '<br>\n'))
                buffer.append(inline_text)
                if i < len(paragraphs) - 1:
                    flush_buffer()

    flush_buffer()
    return '\n'.join(result)

# ---------------------------------------------------------------------------
# Full HTML page wrapper  (includes CSS + JS)
# ---------------------------------------------------------------------------

CSS = """
/* ───── Base ───── */
body {
  font-family: 'Segoe UI', system-ui, sans-serif;
  line-height: 1.6;
  max-width: 860px;
  margin: 2rem auto;
  padding: 0 1.5rem;
  color: #222;
  background: #fafafa;
}

/* ───── Fill input ───── */
.fill-input {
  display: inline-block;
  border: none;
  border-bottom: 2px solid #555;
  background: transparent;
  font-size: 1em;
  padding: 2px 6px;
  min-width: 120px;
  outline: none;
  color: #111;
}
.fill-input:focus { border-bottom-color: #0077cc; }

/* ───── MCH Q / M ───── */
.mchq, .mchm-list {
  list-style: none;
  padding: 0;
  margin: .6rem 0;
}
.mchq-option, .mchm-option {
  margin: .35rem 0;
}
.mchq-option label,
.mchm-option label {
  display: inline-flex;
  align-items: baseline;
  gap: .5rem;
  cursor: pointer;
}
.option-key {
  font-weight: 700;
  min-width: 1.6em;
}
.mchm { margin: .6rem 0; }
.mchm-ids { margin-bottom: .4rem; }
.qid-badge {
  display: inline-block;
  background: #0077cc;
  color: #fff;
  border-radius: 4px;
  padding: 1px 7px;
  font-size: .75em;
  margin-right: 4px;
}

/* ───── Match ───── */
.match-widget {
  display: flex;
  gap: 2rem;
  margin: 1rem 0;
  align-items: flex-start;
}
.match-left  { flex: 1; display: flex; flex-direction: column; gap: .7rem; }
.match-right { display: flex; flex-direction: column; gap: .6rem; }

.match-left-row {
  display: flex;
  align-items: center;
  gap: .8rem;
}
.match-prompt { flex: 1; }

.match-drop-zone {
  min-width: 110px;
  min-height: 36px;
  border: 2px dashed #aaa;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px 8px;
  background: #f4f4f4;
  transition: background .15s, border-color .15s;
  position: relative;
}
.match-drop-zone.drag-over {
  background: #e0f0ff;
  border-color: #0077cc;
}
.match-drop-zone.filled { border-style: solid; background: #eaf7ea; }
.drop-hint { color: #bbb; font-size: .85em; pointer-events: none; }

.match-chip {
  display: flex;
  align-items: center;
  gap: .5rem;
  padding: 6px 12px;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 6px;
  cursor: grab;
  user-select: none;
  box-shadow: 0 1px 3px rgba(0,0,0,.1);
  transition: opacity .15s, transform .1s;
}
.match-chip:active { cursor: grabbing; }
.match-chip.dragging { opacity: .45; transform: scale(.97); }
.chip-key {
  font-weight: 700;
  background: #0077cc;
  color: #fff;
  border-radius: 3px;
  padding: 1px 6px;
  font-size: .8em;
}

/* ───── Box ───── */
.text-box {
  display: inline-block;
  border: 2px solid #444;
  border-radius: 5px;
  padding: .5rem 1rem;
  margin: .5rem 0;
  background: #fff;
  max-width: 100%;
  white-space: pre-wrap;
}

/* ───── Guide ───── */
.guide-box {
  border-left: 4px solid #0077cc;
  background: #f0f7ff;
  border-radius: 0 6px 6px 0;
  padding: .75rem 1.2rem;
  margin: .8rem 0;
}
.guide-title {
  font-weight: 700;
  font-size: 1.05em;
  margin-bottom: .35rem;
  color: #0055aa;
}
.guide-body { color: #333; }

/* ───── Drop (dropdown matching) ───── */
.drop-widget {
  margin: .8rem 0;
  display: flex;
  flex-direction: column;
  gap: .5rem;
}
.drop-row {
  display: flex;
  align-items: center;
  gap: .6rem;
  flex-wrap: wrap;
}
.drop-qnum {
  font-weight: 700;
  min-width: 1.6em;
  color: #444;
}
.drop-text {
  flex: 1;
  min-width: 140px;
}
.drop-select {
  appearance: auto;
  border: 2px solid #9c9c9c;
  border-radius: 5px;
  padding: 4px 8px;
  font-size: 1em;
  background: #fff;
  cursor: pointer;
  outline: none;
  transition: border-color .15s;
}
.drop-select:focus { border-color: #0077cc; }

/* ───── Image insert ───── */
.img-block {
  display: block;
  margin: .8rem 0;
  line-height: 0;          /* removes phantom gap below inline img */
}
.img-insert {
  max-width: 100%;         /* never overflow the container */
  height: auto;            /* preserve aspect ratio */
  display: block;
  border-radius: 4px;
}
"""

JS = """
/* ═══════════════════════════════════
   Drag-and-Drop for [match] blocks
   ═══════════════════════════════════ */
let _draggedChip = null;

function matchDragStart(e) {
  _draggedChip = e.currentTarget;
  _draggedChip.classList.add('dragging');
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/plain', _draggedChip.dataset.value);
}

function matchDragOver(e) {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
  e.currentTarget.classList.add('drag-over');
}

function matchDragLeave(e) {
  e.currentTarget.classList.remove('drag-over');
}

function matchDrop(e) {
  e.preventDefault();
  const zone = e.currentTarget;
  zone.classList.remove('drag-over');

  if (!_draggedChip) return;

  const value = _draggedChip.dataset.value;

  // If the zone already has a chip, send it back to the palette
  const existing = zone.querySelector('.match-chip');
  if (existing) {
    const palette = document.querySelector('.match-right');
    if (palette) palette.appendChild(existing);
    existing.setAttribute('draggable', true);
  }

  // Move the dragged chip into the zone
  zone.appendChild(_draggedChip);
  _draggedChip.classList.remove('dragging');
  zone.classList.add('filled');
  zone.querySelector('.drop-hint') && (zone.querySelector('.drop-hint').style.display = 'none');

  // Store the value in a hidden input so it can be submitted
  let hidden = zone.querySelector('input[type=hidden]');
  if (!hidden) {
    hidden = document.createElement('input');
    hidden.type  = 'hidden';
    hidden.name  = zone.id;
    zone.appendChild(hidden);
  }
  hidden.value = value;

  _draggedChip = null;
}

document.addEventListener('dragend', () => {
  if (_draggedChip) {
    _draggedChip.classList.remove('dragging');
    _draggedChip = null;
  }
});
"""


def convert_to_full_page(source: str, title: str = "Exercise") -> str:
    """Wrap the converted HTML fragment in a complete HTML page."""
    body = convert(source)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
{CSS}
  </style>
</head>
<body>
{body}
<script>
{JS}
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert custom-block plain text to HTML."
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to the input .txt file (omit to read from stdin).",
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to write the output HTML file (omit to print to stdout).",
    )
    parser.add_argument(
        "--fragment",
        action="store_true",
        help="Output only the HTML fragment, not a full page.",
    )
    parser.add_argument(
        "--title",
        default="Exercise",
        help="Page title (used in full-page mode, default: 'Exercise').",
    )
    args = parser.parse_args()

    # Read source
    if args.input:
        with open(args.input, encoding="utf-8") as f:
            source = f.read()
    else:
        source = sys.stdin.read()

    # Convert
    result = convert(source) if args.fragment else convert_to_full_page(source, args.title)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(result)