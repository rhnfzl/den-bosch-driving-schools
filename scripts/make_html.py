#!/usr/bin/env python3
"""Generate the interactive HTML decision aid from the enriched dataset.

Self-contained single file (no external deps): embeds the per-school data plus
the score inputs (quality, maturity, review_trust, sentiment) so the browser can
recompute decision_score live from the weight + review-influence sliders. The raw
star rating is NOT a score input (shown only as a reference in the row detail).

Reads:  data/den_bosch_rijscholen_enriched.json
Writes: docs/human-html/2026-06-08-decision-den-bosch-rijschool-explorer.html
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "den_bosch_rijscholen_enriched.json")
OUT = os.path.join(ROOT, "docs", "human-html", "2026-06-08-decision-den-bosch-rijschool-explorer.html")
GENERATED = "2026-06-08"


def numornull(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def slim(r):
    return {
        "name": r.get("rijschool", ""),
        "town": (r.get("plaats", "") or "").lstrip("'"),
        "n": numornull(r.get("sample_n")),
        "first": numornull(r.get("slagingspercentage_eerste_examens")),
        "eng": r.get("english_instruction", "unknown"),
        "engConf": r.get("english_confidence", ""),
        "engEvi": r.get("english_evidence") or "",
        "engSrc": r.get("english_source") or "",
        "trans": r.get("transmission", "unknown"),
        "q": numornull(r.get("reliability_adjusted_score")),
        "ciLow": r.get("pass_rate_ci_low", ""),
        "ciHigh": r.get("pass_rate_ci_high", ""),
        "rating": r.get("google_rating", ""),
        "reviews": r.get("review_count", ""),
        "avail": r.get("availability", "unknown"),
        "years": numornull(r.get("years_in_business")),
        "maturity": r.get("maturity_flag", "unknown"),
        "founded": r.get("founding_year", ""),
        "foundedBasis": r.get("founding_year_basis", ""),
        "locality": r.get("locality", ""),
        "website": r.get("website") or "",
        "phone": r.get("phone") or "",
        "kvk": r.get("kvk_number") or "",
        "waitlist": r.get("waitlist_signal") or "",
        "notes": r.get("notes") or "",
        "rawRank": r.get("rank_first_weighted", ""),
        "basis": r.get("pass_rate_basis", ""),
        "trust": r.get("review_trust", "insufficient"),
        "sent": r.get("sentiment_index", ""),
        "sentLabel": r.get("sentiment_label", ""),
        "sentSrc": r.get("sentiment_source", ""),
        "sentConf": r.get("sentiment_confidence", ""),
        "reviewSummary": r.get("review_summary", ""),
        "themesPos": r.get("review_themes_pos", ""),
        "themesNeg": r.get("review_themes_neg", ""),
        "redFlags": r.get("review_red_flags", ""),
        "reviewVerified": r.get("review_verified", ""),
        "englishInReviews": r.get("english_in_reviews", ""),
    }


def _esc(s):
    return (str(s) if s is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _barcolor(v):
    return "var(--status-success)" if v >= 58 else ("var(--status-warning)" if v >= 48 else "var(--status-error)")


STATIC_COLS = ["School", "English", "Trans.", "Decision", "Reliability", "Reviews",
               "Avail. (claimed)", "Age (yrs)", "Exams n", "Contact"]


def render_static_header():
    return "<th></th>" + "".join(f"<th>{c}</th>" for c in STATIC_COLS)


def _static_row(d):
    """One static <tr> mirroring the JS render — the no-JS fallback row.

    Uses the same classes + data-label attributes so the mobile card CSS applies
    even with scripts disabled. JS overwrites #body with its own render on load.
    """
    eng = d.get("english_instruction", "unknown")
    ec = d.get("english_confidence", "")
    engbadge = f'<span class="badge b-{eng}">{eng}{(" · " + _esc(ec)) if ec else ""}</span>'
    trans = d.get("transmission", "unknown")
    dec = d.get("decision_score", "")
    try:
        decf = float(dec)
    except (TypeError, ValueError):
        decf = None
    decbar = "" if decf is None else (
        f'<div class="bar"><i style="width:{max(2.0, min(100.0, decf))}%;'
        f'background:{_barcolor(decf)}"></i></div>')
    q = d.get("reliability_adjusted_score", "")
    rel = ('<span class="small">n/a</span>' if q == "" else
           f'{q} <span class="ci">[{d.get("pass_rate_ci_low", "")}-'
           f'{d.get("pass_rate_ci_high", "")}] n={d.get("sample_n", "")}</span>')
    t = d.get("review_trust", "insufficient")
    dots = {"strong": "●●●", "moderate": "●●○", "weak": "●○○", "insufficient": "○○○"}.get(t, "○○○")
    si = d.get("sentiment_index", "")
    reviews = f"{dots} {t}" + (f' <span class="small">· sent {si}</span>' if si != "" else "")
    av = d.get("availability", "unknown")
    avtxt = {"open": '<span class="av-open">✓ open</span>', "wait": '<span class="av-wait">⏳ wait</span>',
             "closed": '<span class="av-closed">✕ closed</span>',
             "unknown": '<span class="av-unknown">-</span>'}.get(av, "-")
    yrs = d.get("years_in_business", "")
    age = ('<span class="small">-</span>' if yrs == "" else
           f'{yrs} <span class="small">{_esc(d.get("maturity_flag", ""))}</span>')
    n = d.get("sample_n", "")
    bits = []
    if d.get("phone"):
        bits.append(_esc(d.get("phone")))
    if d.get("website"):
        bits.append(f'<a href="{_esc(d.get("website"))}" target="_blank" rel="noopener">site↗</a>')
    contact = " · ".join(bits) or "-"
    transtxt = "-" if trans == "unknown" else trans
    return (
        '<tr class="row"><td class="expand"></td>'
        f'<td class="namecell"><span class="name">{_esc(d.get("rijschool", ""))}</span> '
        f'<span class="town">{_esc((d.get("plaats", "") or "").lstrip(chr(39)))}</span></td>'
        f'<td data-label="English">{engbadge}</td>'
        f'<td data-label="Transmission">{_esc(transtxt)}</td>'
        f'<td data-label="Decision"><span class="score">{_esc(dec)}</span>{decbar}</td>'
        f'<td data-label="Reliability">{rel}</td>'
        f'<td data-label="Reviews">{reviews}</td>'
        f'<td data-label="Avail (claimed)">{avtxt}</td>'
        f'<td data-label="Age (yrs)">{age}</td>'
        f'<td data-label="Exams (n)">{_esc(n) if n != "" else "-"}</td>'
        f'<td data-label="Contact" class="small">{contact}</td></tr>'
    )


def render_static_body(rows):
    return "".join(_static_row(d) for d in rows)


def main():
    full = json.load(open(SRC, encoding="utf-8"))
    rows = [slim(r) for r in full]
    payload = json.dumps(rows, ensure_ascii=False).replace("<", "\\u003c")
    # Static fallback: pre-render the default English shortlist into the HTML so the
    # artifact still shows data when JS is OFF (iOS Quick Look / file preview disables
    # scripts). JS overwrites #hrow/#body/#shown with its own render on load.
    def _num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return -1.0
    default = [r for r in full
               if r.get("english_instruction") in ("yes", "likely") and r.get("meets_min_sample") == "yes"]
    default.sort(key=lambda r: _num(r.get("decision_score")), reverse=True)
    html = (TEMPLATE
            .replace("__DATA__", payload)
            .replace("__COUNT__", str(len(rows)))
            .replace("__GENERATED__", GENERATED)
            .replace("__HEAD__", render_static_header())
            .replace("__BODY__", render_static_body(default))
            .replace("__SHOWN__", str(len(default))))
    # Replace em/en dashes with a plain ASCII hyphen across the whole artifact
    # (template text AND embedded data: review summaries, CI ranges, etc.). Only
    # the dash glyph is swapped, so surrounding spaces — and thus " - " spacing —
    # are preserved; ranges like [43.4–71.4] become [43.4-71.4].
    html = html.replace("—", "-").replace("–", "-")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Wrote {OUT} ({len(rows)} schools embedded)")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Den Bosch driving schools — interactive decision aid</title>
<meta name="artifact-kind" content="decision">
<meta name="artifact-audience" content="human">
<meta name="artifact-created" content="__GENERATED__">
<meta name="artifact-source" content="scripts/make_html.py from den_bosch_rijscholen_enriched.json">
<meta name="artifact-read-time" content="4 min">
<style>
:root{
  --blue:#226fb2; --ink:#1c2530; --muted:#5b6776; --line:#e3e8ee; --bg:#f6f8fb; --card:#fff;
  --status-info:#226fb2; --status-success:#2d7a55; --status-warning:#d97706; --status-error:#b91c1c; --neutral:#7a8693;
}
*{box-sizing:border-box}
body{margin:0;font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}
.wrap{max-width:1280px;margin:0 auto;padding:24px 20px 80px}
h1{font-size:24px;margin:0 0 4px}
h2{font-size:19px;margin:30px 0 10px;padding-top:8px}
h3{font-size:16px;margin:18px 0 8px}
a{color:var(--blue)}
.sub{color:var(--muted);margin:0 0 14px}
.meta-ribbon{display:flex;flex-wrap:wrap;gap:6px 18px;background:#eef3f8;border:1px solid var(--line);border-radius:8px;padding:9px 14px;font-size:13px;color:var(--muted);margin:12px 0 20px}
.meta-ribbon strong{color:var(--ink)}
.pm-summary{border-left:4px solid var(--blue);background:var(--card);border:1px solid var(--line);border-left-width:4px;border-radius:8px;padding:14px 18px;margin:0 0 8px}
.pm-summary h2{margin:0 0 8px;padding:0;font-size:17px}
.pm-summary ul{margin:0;padding-left:18px}
.pm-summary li{margin:4px 0}
.panel{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:14px 0}
.controls{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px}
.ctl label.h{display:block;font-weight:600;font-size:13px;margin-bottom:6px;color:var(--ink)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{display:inline-flex;align-items:center;gap:5px;border:1px solid var(--line);border-radius:20px;padding:3px 10px;font-size:13px;cursor:pointer;user-select:none;background:#fafbfc}
.chip input{margin:0}
.chip.on{background:#e7f0f8;border-color:var(--blue)}
.slider-row{display:flex;align-items:center;gap:10px;margin:4px 0}
.slider-row span.lbl{width:96px;font-size:13px;color:var(--muted)}
.slider-row input[type=range]{flex:1}
.slider-row span.val{width:34px;text-align:right;font-variant-numeric:tabular-nums;font-size:13px}
input[type=search]{width:100%;padding:7px 10px;border:1px solid var(--line);border-radius:7px;font-size:14px}
.btn{border:1px solid var(--line);background:#fff;border-radius:7px;padding:7px 12px;font-size:13px;cursor:pointer}
.btn:hover{background:#f0f3f7}
.toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:10px 0}
.count{font-size:14px;color:var(--muted)}
.count b{color:var(--ink)}
table{width:100%;border-collapse:collapse;font-size:13.5px;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
thead th{position:sticky;top:0;background:#eef3f8;text-align:left;padding:9px 8px;font-size:12px;color:var(--ink);cursor:pointer;white-space:nowrap;border-bottom:1px solid var(--line)}
thead th .ar{color:var(--blue)}
tbody td{padding:8px;border-bottom:1px solid var(--line);vertical-align:top}
tbody tr.row:hover{background:#f7fafd}
.name{font-weight:600}
.town{color:var(--muted);font-size:12px}
.badge{display:inline-block;border-radius:5px;padding:1px 7px;font-size:12px;font-weight:600;white-space:nowrap}
.b-yes{background:#e3f3ea;color:var(--status-success)}
.b-likely{background:#fdf0dc;color:var(--status-warning)}
.b-no{background:#fae3e3;color:var(--status-error)}
.b-unknown{background:#eef1f4;color:var(--neutral)}
.av-open{color:var(--status-success);font-weight:600}
.av-wait{color:var(--status-warning);font-weight:600}
.av-closed{color:var(--status-error);font-weight:600}
.av-unknown{color:var(--neutral)}
.score{font-weight:700;font-variant-numeric:tabular-nums}
.bar{height:5px;border-radius:3px;background:#eceff3;margin-top:3px;overflow:hidden}
.bar i{display:block;height:100%}
.ci{color:var(--muted);font-size:12px;white-space:nowrap}
.expand{cursor:pointer;color:var(--blue);user-select:none;font-weight:700}
tr.detail td{background:#f8fafc;color:var(--ink);font-size:13px}
tr.detail .kv{margin:3px 0}
tr.detail .kv b{color:var(--muted);font-weight:600}
.small{color:var(--muted);font-size:12px}
details{margin:10px 0}
summary{cursor:pointer;font-weight:600}
footer.provenance{margin-top:34px;border-top:1px solid var(--line);padding-top:12px;color:var(--muted);font-size:12px}
.legend{font-size:12px;color:var(--muted);margin-top:6px}
@media (max-width:760px){
  .wrap{padding:16px 12px 60px}
  h1{font-size:21px}
  thead{display:none}
  table{border:0;background:transparent}
  tbody,tr,td{display:block;width:100%}
  tr.row{position:relative;background:var(--card);border:1px solid var(--line);border-radius:10px;margin:0 0 10px;padding:12px 14px}
  tr.row td{border:0;padding:4px 0;display:flex;justify-content:space-between;align-items:baseline;gap:14px}
  tr.row td[data-label]::before{content:attr(data-label);font-weight:600;color:var(--muted);font-size:12px;flex:0 0 auto}
  tr.row td.namecell{display:block;font-size:16px;font-weight:600;padding:0 28px 6px 0;border-bottom:1px solid var(--line);margin-bottom:4px}
  tr.row td.namecell::before{content:none}
  tr.row td.expand{position:absolute;top:10px;right:12px;padding:0;font-size:20px;line-height:1}
  tr.row td .bar{display:none}
  .town{display:inline;font-weight:400}
  tr.detail{display:block;background:#f8fafc;border:1px solid var(--line);border-radius:10px;margin:-6px 0 10px;padding:10px 12px}
  tr.detail[hidden]{display:none}   /* keep collapsed by default on mobile (display:block was overriding [hidden]) */
  tr.detail td{display:block;border:0;padding:0}
  .controls{gap:14px}
}
</style>
<noscript><style>.controls{display:none!important}.js-only{display:none!important}</style></noscript>
</head>
<body data-human-html-artifact="true">
<div class="wrap">
<h1>Den Bosch driving schools — interactive decision aid</h1>
<noscript><div class="panel" style="border-left:4px solid var(--status-warning);background:#fdf6ec;margin-top:10px"><b>You're viewing this in a preview with JavaScript off</b> (iOS Quick Look, or a file / in-app preview), so the filters and sliders are hidden — they need JavaScript. You can still read the default English shortlist below. <b>To filter, sort, and re-weight, open this file in a real browser:</b> iPhone — tap Share, then "Open in Safari"; Android — open it in Chrome (not the preview).</div></noscript>
<p class="sub">Sort, filter, and <strong>re-weight the score live</strong>. Pass rates from CBR Rijschoolzoeker (a rolling 12-month window; CBR showed ~Apr&nbsp;2025 to Mar&nbsp;2026 at extraction, the exact period depends on the pull date). Everything else enriched via web research + LLM sentiment. Runs fully offline; your filters persist on reload.</p>

<div class="meta-ribbon" data-meta-ribbon="true" aria-label="Artifact metadata">
  <span><strong>Kind</strong> decision aid</span>
  <span><strong>Schools</strong> __COUNT__</span>
  <span><strong>Generated</strong> __GENERATED__</span>
  <span><strong>Read time</strong> ~4 min</span>
</div>

<section data-audience="pm" class="pm-summary" id="pm-summary">
  <h2>In plain terms</h2>
  <ul>
    <li><strong>What this does:</strong> Lets you pick a Den Bosch driving school on what matters to an expat — does it teach in <em>English</em>, what <em>real reviews</em> say about it (trust-gated sentiment), is the pass rate <em>statistically trustworthy</em>, and is it <em>established</em> — not just the raw CBR pass-rate headline.</li>
    <li><strong>Why it matters:</strong> The raw CBR #1 (Asro, 92%) is English-unconfirmed and had no slots when contacted; the real best-for-you options were buried. Volume and a flashy small-sample percentage are not the same as a good fit.</li>
    <li><strong>What to do:</strong> Use the filters and weight sliders below to build your own shortlist, then phone your top 2–3 to confirm English + a slot.</li>
  </ul>
</section>

<h2 id="explorer">Interactive shortlist explorer</h2>
<p class="sub" style="margin-top:0">English and availability are filters; the <b>Decision</b> column is a live weighted blend you control. Click any column header to sort; click <span class="expand">▸</span> on a row for evidence, notes, and contact details.</p>

<div class="panel">
  <div class="controls">
    <div class="ctl">
      <label class="h" for="search">Search name / town</label>
      <input type="search" id="search" placeholder="e.g. Amir, Rosmalen, ANWB…" autocomplete="off">
      <div class="slider-row" style="margin-top:12px"><span class="lbl">Min. exams (n)</span><input type="range" id="minN" min="0" max="120" step="1" value="25"><span class="val" id="minNval">25</span></div>
      <div class="legend">Gates out statistically thin samples. Default 25 (CBR's comparability guidance).</div>
    </div>
    <div class="ctl">
      <label class="h">English instruction</label>
      <div class="chips" id="engChips"></div>
      <label class="h" style="margin-top:12px">Transmission</label>
      <div class="chips" id="transChips"></div>
      <label class="h" style="margin-top:12px">Availability <span class="small">(claimed — verify)</span></label>
      <div class="chips" id="availChips"></div>
    </div>
    <div class="ctl">
      <label class="h">Weights — drag to re-rank (decision_score)</label>
      <div class="slider-row"><span class="lbl">Quality (CBR)</span><input type="range" id="wq" min="0" max="100" value="85"><span class="val" id="wqv">85</span></div>
      <div class="slider-row"><span class="lbl">Maturity</span><input type="range" id="wm" min="0" max="100" value="15"><span class="val" id="wmv">15</span></div>
      <div class="slider-row"><span class="lbl">Review influence</span><input type="range" id="wi" min="0" max="100" value="100"><span class="val" id="wiv">100</span></div>
      <div class="legend">Quality + Maturity set the base; <b>Review influence</b> scales how much the trust-gated review <b>sentiment</b> nudges it (±15% at 100). The raw star rating is <b>never scored</b>. Presets:
        <button class="btn" data-preset="balanced" type="button">Balanced</button>
        <button class="btn" data-preset="quality" type="button">Quality-only</button>
        <button class="btn" data-preset="reviews" type="button">Reviews-led</button>
      </div>
    </div>
  </div>
  <div class="toolbar">
    <div class="count">Showing <b id="shown">__SHOWN__</b> of __COUNT__ schools</div>
    <div class="js-only" style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
      <label class="small" for="sortSel">Sort by</label>
      <select id="sortSel" style="padding:6px 8px;border:1px solid var(--line);border-radius:7px;font-size:13px"></select>
      <button class="btn" id="sortDir" type="button" title="Toggle ascending/descending">▼</button>
      <button class="btn" id="reset" type="button">Reset filters</button>
    </div>
  </div>
</div>

<table id="tbl">
  <thead><tr id="hrow">__HEAD__</tr></thead>
  <tbody id="body">__BODY__</tbody>
</table>
<p class="legend">Quality = Wilson 95% lower bound on the first-exam pass rate. Reviews = authenticity (●●● strong … ○○○ insufficient) + OpenAI <b>sentiment</b> of real review text; the raw star is <b>not</b> scored. Availability is self-reported — verify by phone. <span class="b-unknown badge">unknown</span> English ≠ "no English".</p>

<h2 id="how">How the score works</h2>
<details open>
  <summary>The base, the review modifier, and the gate</summary>
  <div style="margin-top:8px">
    <p><b>decision_score</b> = base <code>(0.85·Quality + 0.15·Maturity)</code>, then nudged by a <b>trust-gated review modifier</b> (you control the weights + review influence above):</p>
    <ul>
      <li><b>Quality (CBR)</b> — Wilson 95% lower confidence bound on the first-exam pass rate, given the exam count. A 92%-from-30 and a 100%-from-1 are <em>not</em> the same bet. The trustworthy, outcome-based signal.</li>
      <li><b>Maturity</b> — years in business (estimated from KvK / website / domain / first review), capped at 20.</li>
      <li><b>Review modifier</b> — an OpenAI <b>sentiment</b> read of <em>real review text</em> ("how the school is"), <b>gated by authenticity</b> (●●● strong … ○○○ insufficient — how genuine the reviews look vs bought one-liners). Moves the score up to ±15%. The raw <b>star rating is deliberately NOT scored</b> — it's gameable, 5.0-inflated, and 0-correlated with the pass rate. Two models: Claude reads/judges authenticity, OpenAI scores sentiment.</li>
      <li><b>Availability</b> — self-reported (site/aggregators/reviews); shown as a filter/annotation, <b>weight 0</b> (Asro shows "geen wachtlijst" yet has a long wait — claims ≠ reality).</li>
    </ul>
    <p>The <b>Min. exams</b> slider is a hard gate: schools below it are hidden (set it to 0 to see everyone, including the 1–5 exam noise).</p>
  </div>
</details>
<h3>Consequences &amp; limitations</h3>
<details open>
  <summary>What to keep in mind before trusting a number</summary>
  <div style="margin-top:8px">
    <ul>
      <li><b>No per-school year-by-year history exists publicly</b> — CBR only ever shows the current rolling 12-month window. Your CSV is one such window (CBR showed ~Apr 2025 to Mar 2026 around the analysis date; the exact period is whatever CBR displayed when you extracted it). The Wilson interval is the substitute, not a trend.</li>
      <li><b>Website claims diverge from reality</b> — Asro advertises "geen wachtlijst" yet had no slots when contacted. Treat availability as a hint, confirm by phone.</li>
      <li><b>Founding years are estimates</b> — the KvK number (row detail) lets you verify a finalist officially.</li>
      <li><b>Reviews are gated, not trusted blindly</b> — a glowing sentiment from a wall of fake one-liners (low authenticity) barely moves the score; a positive sentiment from substantive, verified reviews moves it. Set Review influence to 0 to rank on CBR + maturity alone.</li>
    </ul>
  </div>
</details>

<footer class="provenance" data-provenance="true">
  <p>Generated by an automated enrichment pipeline on __GENERATED__ from <code>den_bosch_rijscholen_enriched.json</code>. Data sources: pass rates from CBR Rijschoolzoeker (rolling 12-month window, period as of CSV extraction) + public web research (school sites, aggregators, reviews) + LLM sentiment. Figures are estimates - verify finalists by phone.</p>
  <script type="application/ld+json" id="provenance">
  {"@context":"https://schema.org/","@type":"CreativeWork","@id":"urn:human-html:__GENERATED__:decision:den-bosch-rijschool-explorer","additionalType":"ai-generated-artifact","artifactKind":"decision","dateCreated":"__GENERATED__","creator":{"@type":"SoftwareApplication","name":"automated enrichment pipeline"},"promptHash":"redacted","reviewer":"independent Codex second-eye review","source":"CBR Rijschoolzoeker pass rates (rolling 12-month window) + public web research + LLM sentiment"}
  </script>
</footer>
</div>

<script id="data" type="application/json">__DATA__</script>
<script>
"use strict";
const DATA = JSON.parse(document.getElementById("data").textContent);
const PRESETS = {
  balanced:{q:85,m:15,i:100}, quality:{q:100,m:0,i:0}, reviews:{q:70,m:10,i:100}
};
const TRUST_W = {strong:1.0, moderate:0.6, weak:0.25, insufficient:0.0};
const state = {
  search:"", minN:25,
  eng:new Set(["yes","likely"]), trans:new Set(["automatic","both","manual","unknown"]),
  avail:new Set(["open","wait","closed","unknown"]),
  w:{q:85,m:15}, reviewInfluence:1.0, sort:{key:"decision", dir:-1}
};

const COLS = [
  {key:"name",        label:"School",        get:d=>d.name.toLowerCase(), num:false},
  {key:"eng",         label:"English",       get:d=>({yes:3,likely:2,unknown:1,no:0})[d.eng], num:true},
  {key:"trans",       label:"Trans.",        get:d=>d.trans, num:false},
  {key:"decision",    label:"Decision",      get:d=>decision(d), num:true},
  {key:"q",           label:"Reliability",   get:d=>d.q==null?-1:d.q, num:true},
  {key:"reviews",     label:"Reviews",       get:d=>(({strong:3,moderate:2,weak:1,insufficient:0})[d.trust]||0)*1000 + ((d.sent===""||d.sent==null)?-1:+d.sent), num:true},
  {key:"avail",       label:"Avail. (claimed)", get:d=>({open:3,wait:2,unknown:1,closed:0})[d.avail], num:true},
  {key:"years",       label:"Age (yrs)",     get:d=>d.years==null?-1:d.years, num:true},
  {key:"n",           label:"Exams n",       get:d=>d.n==null?-1:d.n, num:true},
  {key:"contact",     label:"Contact",       get:d=>"", num:false, nosort:true}
];

function maturityPts(years){ return years==null ? 50 : Math.min(years,20)/20*100; }
function decision(d){
  if(d.q==null) return null;
  const w=state.w, sum=(w.q+w.m)||1;
  const base=(w.q*d.q + w.m*maturityPts(d.years))/sum;
  const tw=TRUST_W[d.trust]||0;
  let s=(d.sent===""||d.sent==null)?50:+d.sent;
  s=Math.min(100,Math.max(0,s));                 // clamp out-of-range sentiment
  const mult=1 + state.reviewInfluence*tw*((s-50)/50)*0.15;
  return Math.min(100, Math.max(0, base*mult));  // clamp score to 0..100
}
function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));}
function barColor(v){ return v>=58?"var(--status-success)":v>=48?"var(--status-warning)":"var(--status-error)"; }

function filtered(){
  const q=state.search.trim().toLowerCase();
  return DATA.filter(d=>{
    if(state.minN>0 && (d.n==null || d.n<state.minN)) return false;
    if(!state.eng.has(d.eng)) return false;
    if(!state.trans.has(d.trans)) return false;
    if(!state.avail.has(d.avail)) return false;
    if(q && !(d.name.toLowerCase().includes(q) || d.town.toLowerCase().includes(q))) return false;
    return true;
  });
}
function sorted(rows){
  const c=COLS.find(c=>c.key===state.sort.key)||COLS[3], dir=state.sort.dir;
  return rows.slice().sort((a,b)=>{
    let x=c.key==="decision"?decision(a):c.get(a), y=c.key==="decision"?decision(b):c.get(b);
    if(x==null)x=-1; if(y==null)y=-1;
    if(c.num) return (x-y)*dir;
    return String(x).localeCompare(String(y))*dir;
  });
}

function badgeEng(d){
  const lbl={yes:"yes",likely:"likely",no:"no",unknown:"unknown"}[d.eng];
  return `<span class="badge b-${d.eng}">${lbl}${d.engConf?` · ${esc(d.engConf)}`:""}</span>`;
}
function availCell(d){
  const m={open:"✓ open",wait:"⏳ wait",closed:"✕ closed",unknown:"—"};
  return `<span class="av-${d.avail}">${m[d.avail]}</span>`;
}
function reviewsCell(d){
  const dots={strong:"●●●",moderate:"●●○",weak:"●○○",insufficient:"○○○"}[d.trust]||"○○○";
  const s=(d.sent===""||d.sent==null)?null:+d.sent;
  const stxt=s==null?"":` <span class="small">· sent ${s}</span>`;
  return `<span title="authenticity ${esc(d.trust)}; sentiment ${s==null?"n/a":s} via ${esc(d.sentSrc||"n/a")}">${dots} ${esc(d.trust)}${stxt}</span>`;
}
function contactCell(d){
  const bits=[];
  if(d.phone) bits.push(esc(d.phone));
  if(d.website) bits.push(`<a href="${esc(d.website)}" target="_blank" rel="noopener">site↗</a>`);
  return bits.join(" · ")||"—";
}

function renderHead(){
  document.getElementById("hrow").innerHTML = '<th></th>'+COLS.map(c=>{
    const arrow = state.sort.key===c.key ? `<span class="ar">${state.sort.dir<0?"▼":"▲"}</span>` : "";
    return `<th data-key="${c.key}" data-nosort="${!!c.nosort}">${c.label} ${arrow}</th>`;
  }).join("");
  syncSort();
}
function populateSort(){
  document.getElementById("sortSel").innerHTML = COLS.filter(c=>!c.nosort)
    .map(c=>`<option value="${c.key}">${c.label}</option>`).join("");
}
function syncSort(){
  const s=document.getElementById("sortSel"); if(s)s.value=state.sort.key;
  const b=document.getElementById("sortDir"); if(b)b.textContent=state.sort.dir<0?"▼":"▲";
}
function setSort(key, dir){ state.sort.key=key; if(dir!=null)state.sort.dir=dir; renderHead(); render(); }
function render(){
  const rows=sorted(filtered());
  document.getElementById("shown").textContent=rows.length;
  const body=document.getElementById("body");
  body.innerHTML = rows.map((d,i)=>{
    const dec=decision(d);
    const decTxt = dec==null?"n/a":dec.toFixed(1);
    const decBar = dec==null?"":`<div class="bar"><i style="width:${Math.max(2,Math.min(100,dec))}%;background:${barColor(dec)}"></i></div>`;
    const basisMark = d.basis==='all_exam_fallback' ? ' <span class="ci" title="all-exam rate used because first-exam rate was blank">*all-exam</span>' : '';
    const rel = d.q==null?'<span class="small">n/a</span>':`${d.q.toFixed(1)} <span class="ci">[${d.ciLow}–${d.ciHigh}] n=${d.n}${basisMark}</span>`;
    const age = d.years==null?'<span class="small">—</span>':`${d.years} <span class="small">${esc(d.maturity)}</span>`;
    const detail = `<tr class="detail" id="det${i}" hidden><td></td><td colspan="${COLS.length}">`+
      (d.engEvi?`<div class="kv"><b>English evidence:</b> ${esc(d.engEvi)} ${d.engSrc?`<a href="${esc(d.engSrc)}" target="_blank" rel="noopener">source↗</a>`:""}</div>`:"")+
      (d.waitlist?`<div class="kv"><b>Availability note (self-reported):</b> ${esc(d.waitlist)}</div>`:"")+
      ((d.reviewSummary||d.trust!=="insufficient")?`<div class="kv"><b>Reviews:</b> ${esc(d.trust)} trust · sentiment ${(d.sent===""||d.sent==null)?"n/a":esc(d.sent)} ${d.sentSrc?`(${esc(d.sentSrc)})`:""}${d.reviewSummary?` — ${esc(d.reviewSummary)}`:""}</div>`:"")+
      (d.themesPos?`<div class="kv"><b>Praised:</b> ${esc(d.themesPos)}</div>`:"")+
      (d.themesNeg?`<div class="kv"><b>Complaints:</b> ${esc(d.themesNeg)}</div>`:"")+
      (d.redFlags?`<div class="kv"><b>Review flags:</b> ${esc(d.redFlags)}</div>`:"")+
      ((d.rating!==""&&d.rating!=null)?`<div class="kv"><b>Raw star (not scored):</b> ${esc(d.rating)}★ / ${esc(d.reviews)} reviews</div>`:"")+
      `<div class="kv"><b>Founded:</b> ${esc(d.founded||"unknown")} ${d.foundedBasis?`(${esc(d.foundedBasis)})`:""} · <b>KvK:</b> ${esc(d.kvk||"—")} · <b>Locality:</b> ${esc(d.locality||"—")} · <b>Raw CBR rank:</b> ${esc(d.rawRank)}</div>`+
      (d.notes?`<div class="kv"><b>Notes:</b> ${esc(d.notes)}</div>`:"")+
      `</td></tr>`;
    return `<tr class="row" data-det="det${i}">
      <td class="expand" title="details">▸</td>
      <td class="namecell"><span class="name">${esc(d.name)}</span> <span class="town">${esc(d.town)}</span></td>
      <td data-label="English">${badgeEng(d)}</td>
      <td data-label="Transmission">${esc(d.trans==="unknown"?"—":d.trans)}</td>
      <td data-label="Decision"><span class="score">${decTxt}</span>${decBar}</td>
      <td data-label="Reliability">${rel}</td>
      <td data-label="Reviews">${reviewsCell(d)}</td>
      <td data-label="Avail (claimed)">${availCell(d)}</td>
      <td data-label="Age (yrs)">${age}</td>
      <td data-label="Exams (n)">${d.n==null?"—":d.n}</td>
      <td data-label="Contact" class="small">${contactCell(d)}</td>
    </tr>${detail}`;
  }).join("");
  saveUrl();
}

// ---- chips ----
function chip(group, val, label){
  const on=state[group].has(val);
  return `<label class="chip ${on?"on":""}"><input type="checkbox" data-group="${group}" value="${val}" ${on?"checked":""}>${label}</label>`;
}
function renderChips(){
  document.getElementById("engChips").innerHTML=["yes","likely","unknown","no"].map(v=>chip("eng",v,v)).join("");
  document.getElementById("transChips").innerHTML=["automatic","both","manual","unknown"].map(v=>chip("trans",v,v==="unknown"?"—":v)).join("");
  document.getElementById("availChips").innerHTML=["open","wait","closed","unknown"].map(v=>chip("avail",v,v)).join("");
}

// ---- URL state (shareable) ----
function saveUrl(){
  const s={v:1,q:state.search,n:state.minN,e:[...state.eng],t:[...state.trans],a:[...state.avail],w:state.w,i:state.reviewInfluence,s:state.sort};
  try{ history.replaceState(null,"","#"+encodeURIComponent(JSON.stringify(s))); }catch(_){}
}
function loadUrl(){
  const h=location.hash.slice(1); if(!h) return;
  try{
    const s=JSON.parse(decodeURIComponent(h)); if(s.v!==1) return;
    if(typeof s.q==="string")state.search=s.q;
    if(typeof s.n==="number")state.minN=s.n;
    if(Array.isArray(s.e))state.eng=new Set(s.e);
    if(Array.isArray(s.t))state.trans=new Set(s.t);
    if(Array.isArray(s.a))state.avail=new Set(s.a);
    if(s.w&&typeof s.w.q==="number")state.w={q:s.w.q, m:(typeof s.w.m==="number"?s.w.m:15)};
    if(typeof s.i==="number")state.reviewInfluence=s.i; if(s.s)state.sort=s.s;
  }catch(_){}
}
function syncInputs(){
  document.getElementById("search").value=state.search;
  document.getElementById("minN").value=state.minN; document.getElementById("minNval").textContent=state.minN;
  for(const k of ["q","m"]){ document.getElementById("w"+k).value=state.w[k]; document.getElementById("w"+k+"v").textContent=state.w[k]; }
  const ip=Math.round(state.reviewInfluence*100); document.getElementById("wi").value=ip; document.getElementById("wiv").textContent=ip;
}

// ---- wire up ----
function setWeights(p){ const pr=PRESETS[p]; state.w={q:pr.q,m:pr.m}; state.reviewInfluence=pr.i/100; syncInputs(); render(); }
// Coalesce the heavy 121-row re-render to one per animation frame. The value
// labels update synchronously below, so on a phone the number paints instantly
// while dragging instead of being blocked by a full re-render per input event.
let _raf=0;
function scheduleRender(){ if(_raf) return; _raf=requestAnimationFrame(()=>{ _raf=0; render(); }); }
document.addEventListener("input",e=>{
  const t=e.target;
  if(t.id==="search"){ state.search=t.value; scheduleRender(); }
  else if(t.id==="minN"){ state.minN=+t.value; document.getElementById("minNval").textContent=t.value; scheduleRender(); }
  else if(t.id==="wi"){ state.reviewInfluence=+t.value/100; document.getElementById("wiv").textContent=t.value; scheduleRender(); }
  else if(t.id&&t.id[0]==="w"&&t.id.length===2){ const k=t.id[1]; state.w[k]=+t.value; document.getElementById(t.id+"v").textContent=t.value; scheduleRender(); }
  else if(t.id==="sortSel"){ setSort(t.value, t.value==="name"?1:-1); }
  else if(t.dataset&&t.dataset.group){ const g=t.dataset.group; t.checked?state[g].add(t.value):state[g].delete(t.value); t.closest(".chip").classList.toggle("on",t.checked); render(); }
});
document.addEventListener("click",e=>{
  const th=e.target.closest("th[data-key]");
  if(th && th.dataset.nosort!=="true"){ const k=th.dataset.key; state.sort.dir = state.sort.key===k ? -state.sort.dir : (k==="name"?1:-1); state.sort.key=k; renderHead(); render(); return; }
  const row=e.target.closest("tr.row");
  if(row && e.target.classList.contains("expand")){ const det=document.getElementById(row.dataset.det); if(det){ det.hidden=!det.hidden; e.target.textContent=det.hidden?"▸":"▾"; } return; }
  if(e.target.id==="reset"){ state.search="";state.minN=25;state.eng=new Set(["yes","likely"]);state.trans=new Set(["automatic","both","manual","unknown"]);state.avail=new Set(["open","wait","closed","unknown"]);state.w={q:85,m:15};state.reviewInfluence=1.0;state.sort={key:"decision",dir:-1};renderChips();syncInputs();renderHead();render(); return; }
  if(e.target.dataset&&e.target.dataset.preset){ setWeights(e.target.dataset.preset); return; }
  if(e.target.id==="sortDir"){ state.sort.dir=-state.sort.dir; renderHead(); render(); return; }
});

loadUrl(); populateSort(); syncInputs(); renderChips(); renderHead(); render();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
