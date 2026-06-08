#!/usr/bin/env python3
"""Merge per-school web research into the CBR CSV and add reliability statistics.

Reads:
  data/den_bosch_rijscholen_auto.csv   (original, untouched)
  research/school_<NNN>.json           (one per school, written by the workflow)

Writes:
  data/den_bosch_rijscholen_enriched.csv
  data/den_bosch_rijscholen_enriched.json

Stats added (computed here, NOT researched):
  - Wilson 95% confidence interval on the first-exam pass rate given the exam
    count, so small / new schools are correctly distrusted.
  - years_in_business, maturity_flag, low_volume, reliability_adjusted_score.
"""
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "den_bosch_rijscholen_auto.csv")
RESEARCH = os.path.join(ROOT, "research")
OUT_CSV = os.path.join(ROOT, "data", "den_bosch_rijscholen_enriched.csv")
OUT_JSON = os.path.join(ROOT, "data", "den_bosch_rijscholen_enriched.json")
# Canonical complete record: every computed field PLUS the full raw research,
# review (incl. verbatim quotes), and OpenAI-sentiment objects embedded per school.
# This is the source of truth to work from; the HTML is only a lossy view of it.
OUT_MASTER = os.path.join(ROOT, "data", "den_bosch_master.json")

CURRENT_YEAR = 2026          # CBR window ends 31 Mar 2026
LOW_VOLUME_N = 25            # CBR's own guidance: compare schools with >=25 exams
Z = 1.96                     # 95% confidence

RESEARCH_FIELDS = [
    "english_instruction", "english_confidence", "english_evidence", "english_source",
    "transmission", "transmission_source",
    "founding_year", "founding_year_basis", "founding_confidence",
    "website", "phone", "address", "postcode", "kvk_number", "cbr_rijschoolnummer",
    "google_rating", "review_count", "price_signal", "waitlist_signal", "notes",
]


def to_int(value):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None


def wilson(rate_pct, n):
    """Wilson score interval (low, high) as percentages, or (None, None)."""
    if rate_pct is None or not n:
        return None, None
    p = rate_pct / 100.0
    denom = 1 + Z * Z / n
    center = p + Z * Z / (2 * n)
    margin = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    low = max(0.0, (center - margin) / denom)
    high = min(1.0, (center + margin) / denom)
    return round(low * 100, 1), round(high * 100, 1)


def maturity(years):
    if years is None:
        return "unknown"
    if years < 3:
        return "new"
    if years <= 5:
        return "establishing"
    return "established"


def to_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


# ---- v2 decision scoring (TUNABLE) -------------------------------------------
# decision_score = weighted blend of four 0..100 components. Edit WEIGHTS to
# re-weight; they should sum to 1.0. The n>=25 gate is applied at ranking time
# (report), not here, so the raw score stays available for every school.
# NOTE: availability defaults to 0 weight on purpose — it is parsed from the
# school's OWN website ("geen wachtlijst" etc.), which is marketing, not fact
# (e.g. Asro claims no waitlist but has a long wait per direct contact). It is
# kept as an informational annotation/filter, not a trusted score driver.
# decision_score = base (CBR quality + maturity) nudged by trust-gated review sentiment.
# The raw star rating is intentionally NOT in the score (gameable, 5.0-inflated, and
# 0-correlated with pass rate). Reviews enter ONLY via content: an OpenAI sentiment read
# of real review quotes, GATED by how authentic the reviews look (review_trust), so bought
# praise from a wall of one-liners barely counts.
BASE_WEIGHTS = {"quality": 0.85, "maturity": 0.15}   # tunable; should sum to 1.0
TRUST_WEIGHT = {"strong": 1.0, "moderate": 0.6, "weak": 0.25, "insufficient": 0.0}
REVIEW_MAX_SWING = 0.15    # max fraction the review modifier can move the score (+/-)
REVIEW_INFLUENCE = 1.0     # 0..1 global dial on how much reviews matter (tunable)
IN_CITY = {"S-HERTOGENBOSCH", "ROSMALEN", "NULAND", "EMPEL", "ENGELEN", "VINKEL"}
REVIEW_DIR = os.path.join(ROOT, "research", "reviews")
SENT_DIR = os.path.join(ROOT, "research", "sentiment")
REVIEW_COLS = ["review_trust", "review_substance", "sentiment_index", "sentiment_label",
               "sentiment_source", "sentiment_confidence", "review_summary",
               "review_themes_pos", "review_themes_neg", "review_red_flags",
               "english_in_reviews", "review_verified", "reviews_read", "review_modifier"]
V2_COLS = ["meets_min_sample", "availability", "locality"] + REVIEW_COLS + ["decision_score"]

# Human-verified corrections that SUPERSEDE automated research (highest trust),
# keyed by row_index. The CBR car export only lists schools with car (B) exams,
# so "not a car school" research notes are unreliable; the user confirmed cases win.
USER_CORRECTIONS = {
    20: {"notes_append": "[User-verified: Motorrijles Max also offers car (B) lessons and gives instruction in English.]"},
}


def parse_availability(sig):
    """Turn a free-text waitlist_signal into open / wait / closed / unknown.

    Conservative: only assert 'wait' on an explicit, non-negated wait signal.
    Phrases like 'no explicit wait time stated' must NOT count as a wait.
    """
    if not sig:
        return "unknown"
    s = str(sig).lower()
    closed = ["geen nieuwe leerlingen", "momenteel tijdelijk geen", "tijdelijk geen nieuwe",
              "aanmeldstop", "neem ik momenteel", "wachtlijst vol", "not accepting", "geen aanmeldingen"]
    openk = ["geen wachtlijst", "geen wachttijd", "geen lange wacht", "geen wachttijden",
             "direct beginnen", "direct starten", "morgen al", "deze week nog", "snelste examendata",
             "kunt morgen beginnen", "morgen beginnen", "je start deze week"]
    # negated / absent wait -> NOT a wait signal (fixes "no explicit wait time stated")
    negated = ["no explicit wait", "no wait", "geen wacht", "not stated", "no waiting",
               "without wait", "niet vermeld", "no mention of a wait", "geen expliciete"]
    # explicit, positive wait evidence only: a stated duration or an actual waitlist
    waitk = ["wachttijd van", "wachtlijst van", "week wait", "weken wachttijd", "four-week wait",
             "-week wait", "weeks wait", "maand wachttijd", "op de wachtlijst",
             "currently has a wait", "there is a wait", "waiting list of", "wachttijd van ongeveer"]
    if any(k in s for k in closed):
        return "closed"
    if any(k in s for k in openk):       # check "geen wachtlijst" (open) before any wait token
        return "open"
    if any(k in s for k in negated):     # explicit "no wait" / "not stated" -> unknown, not wait
        return "unknown"
    if any(k in s for k in waitk):
        return "wait"
    return "unknown"


def load_side(dirpath, slug):
    """Load a side-channel JSON (review or sentiment) for a slug, or None."""
    path = os.path.join(dirpath, f"{slug}.json")
    if not os.path.exists(path):
        return None
    try:
        return json.loads(open(path, encoding="utf-8").read())
    except (json.JSONDecodeError, OSError):
        return None


def joinlist(x):
    if isinstance(x, list):
        return "; ".join(str(t).strip() for t in x if str(t).strip())
    return str(x) if x else ""


def maturity_points(years):
    if years is None:
        return 50.0                      # neutral when founding unknown
    return round(min(years, 20) / 20 * 100, 1)


def locality(plaats):
    p = str(plaats).upper().lstrip("'").strip()
    return "in_city" if p in IN_CITY else "nearby"


def load_research(slug):
    """Defensively load research/<slug>.json; tolerate code fences / stray text."""
    path = os.path.join(RESEARCH, f"{slug}.json")
    if not os.path.exists(path):
        return None
    raw = open(path, encoding="utf-8").read().strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.lstrip().startswith("json"):
            raw = raw.lstrip()[4:]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(raw[start:end + 1])
            except json.JSONDecodeError:
                return {"_parse_error": True}
        return {"_parse_error": True}


def main():
    with open(SRC, newline="", encoding="utf-8") as fh:
        base_rows = list(csv.DictReader(fh))

    new_cols = [
        "research_status", "sample_n", "pass_rate_basis",
        "pass_rate_ci_low", "pass_rate_ci_high", "ci_width",
        "years_in_business", "maturity_flag", "low_volume", "reliability_adjusted_score",
    ] + RESEARCH_FIELDS + V2_COLS

    enriched = []
    counts = {"english": {}, "research": {"ok": 0, "missing": 0, "parse_error": 0}, "founding_known": 0}

    for i, base in enumerate(base_rows, start=1):
        slug = f"school_{i:03d}"
        n = to_int(base.get("aantal_examens"))
        first = to_int(base.get("slagingspercentage_eerste_examens"))
        allr = to_int(base.get("slagingspercentage_alle_examens"))

        # Prefer first-exam rate; fall back to all-exam rate when first is blank.
        if first is not None:
            rate, basis = first, "first_exam"
        elif allr is not None:
            rate, basis = allr, "all_exam_fallback"
        else:
            rate, basis = None, "none"

        ci_low, ci_high = wilson(rate, n)
        row = dict(base)
        row["sample_n"] = n if n is not None else ""
        row["pass_rate_basis"] = basis
        row["pass_rate_ci_low"] = "" if ci_low is None else ci_low
        row["pass_rate_ci_high"] = "" if ci_high is None else ci_high
        row["ci_width"] = "" if (ci_low is None or ci_high is None) else round(ci_high - ci_low, 1)
        row["low_volume"] = "yes" if (n is not None and n < LOW_VOLUME_N) else "no"

        research = load_research(slug)
        if research is None:
            row["research_status"] = "missing"
            counts["research"]["missing"] += 1
            for f in RESEARCH_FIELDS:
                row[f] = ""
            row["english_instruction"] = "unknown"
            row["transmission"] = "unknown"
        elif research.get("_parse_error"):
            row["research_status"] = "parse_error"
            counts["research"]["parse_error"] += 1
            for f in RESEARCH_FIELDS:
                row[f] = ""
            row["english_instruction"] = "unknown"
            row["transmission"] = "unknown"
        else:
            row["research_status"] = "ok"
            counts["research"]["ok"] += 1
            for f in RESEARCH_FIELDS:
                val = research.get(f, "")
                row[f] = "" if val is None else val

        # Maturity from founding year (research) + computed reliability score.
        fy = to_int(row.get("founding_year"))
        years = (CURRENT_YEAR - fy) if fy else None
        row["years_in_business"] = years if years is not None else ""
        row["maturity_flag"] = maturity(years)
        if years is not None:
            counts["founding_known"] += 1

        # Reliability-adjusted score = the pure Wilson lower bound (quality only).
        # Maturity is NOT folded in here; it is a separate component of
        # decision_score, so age is counted exactly once (no double-count).
        row["reliability_adjusted_score"] = round(ci_low, 1) if ci_low is not None else ""

        eng = row.get("english_instruction") or "unknown"
        counts["english"][eng] = counts["english"].get(eng, 0) + 1

        enriched.append(row)

    # --- Second pass: v2 decision metrics + content-based review scoring ---
    avail_counts, trust_counts, sent_src_counts = {}, {}, {}
    for i, r in enumerate(enriched, start=1):
        slug = f"school_{i:03d}"
        # Apply any human-verified correction first (supersedes research notes).
        corr = USER_CORRECTIONS.get(i)
        if corr and corr.get("notes_append"):
            note = (r.get("notes") or "").strip()
            if corr["notes_append"] not in note:
                r["notes"] = (note + " " + corr["notes_append"]).strip()

        n = to_int(r.get("sample_n"))
        r["meets_min_sample"] = "yes" if (n is not None and n >= LOW_VOLUME_N) else "no"

        # Raw star kept as a reference column only (NOT scored). Hide out-of-scale
        # values (e.g. a 9.4/10 Trustoo score) so they don't render as bogus 5-star data.
        rating = to_float(r.get("google_rating"))
        if rating is not None and not (0 <= rating <= 5):
            note = (r.get("notes") or "").strip()
            r["notes"] = (note + " [Hid an out-of-scale rating (not a 5-star Google value).]").strip()
            r["google_rating"] = ""
            r["review_count"] = ""

        avail = parse_availability(r.get("waitlist_signal"))
        r["availability"] = avail
        avail_counts[avail] = avail_counts.get(avail, 0) + 1
        r["locality"] = locality(r.get("plaats"))

        # Review CONTENT: authenticity (Claude/Tavily) + sentiment (OpenAI, fallback agent).
        rv = load_side(REVIEW_DIR, slug) or {}
        se = load_side(SENT_DIR, slug) or {}
        trust = rv.get("review_trust") or "insufficient"
        r["review_trust"] = trust
        r["review_substance"] = rv.get("review_substance") or ""
        r["review_summary"] = rv.get("review_summary") or ""
        r["english_in_reviews"] = rv.get("english_in_reviews") or ""
        r["review_verified"] = ("yes" if rv.get("verified_reviews") else "no") if rv else ""
        r["reviews_read"] = rv.get("reviews_read") if rv.get("reviews_read") is not None else ""
        r["review_red_flags"] = joinlist(rv.get("red_flags"))
        trust_counts[trust] = trust_counts.get(trust, 0) + 1

        s_idx = se.get("sentiment_index")
        if s_idx is not None:
            s_src, s_lbl, s_conf = "openai", se.get("sentiment") or "", se.get("confidence") or ""
            pos, neg = se.get("themes_positive"), se.get("themes_negative")
        elif rv.get("sentiment_index") is not None:
            s_idx, s_src, s_lbl, s_conf = rv.get("sentiment_index"), "agent", rv.get("sentiment") or "", ""
            pos, neg = rv.get("themes_positive"), rv.get("themes_negative")
        else:
            s_src, s_lbl, s_conf, pos, neg = "none", "", "", None, None
        sv = to_float(s_idx)
        if sv is not None:
            sv = min(100.0, max(0.0, sv))            # clamp any out-of-range model output to 0..100
        r["sentiment_index"] = int(sv) if sv is not None else ""
        r["sentiment_label"] = s_lbl
        r["sentiment_source"] = s_src
        r["sentiment_confidence"] = s_conf
        r["review_themes_pos"] = joinlist(pos)
        r["review_themes_neg"] = joinlist(neg)
        sent_src_counts[s_src] = sent_src_counts.get(s_src, 0) + 1

        # decision_score = base(CBR quality + maturity) nudged by trust-gated sentiment.
        q = to_float(r.get("reliability_adjusted_score"))
        if q is None:
            r["decision_score"] = ""
            r["review_modifier"] = ""
        else:
            m_pts = maturity_points(to_int(r.get("years_in_business")))
            base = (BASE_WEIGHTS["quality"] * q + BASE_WEIGHTS["maturity"] * m_pts) / sum(BASE_WEIGHTS.values())
            eff = ((sv if sv is not None else 50.0) - 50.0) / 50.0           # -1..+1 (sv already clamped to 0..100)
            mult = 1 + REVIEW_INFLUENCE * TRUST_WEIGHT.get(trust, 0.0) * eff * REVIEW_MAX_SWING
            r["review_modifier"] = round(mult, 3)
            r["decision_score"] = round(min(100.0, max(0.0, base * mult)), 1)  # clamp 0..100

    assert len(enriched) == len(base_rows), "row count mismatch!"

    fieldnames = list(base_rows[0].keys()) + new_cols
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(enriched)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(enriched, fh, ensure_ascii=False, indent=2)

    # Canonical complete record: every computed field PLUS the full raw research,
    # review (incl. verbatim quotes) and OpenAI-sentiment objects, so we never have
    # to re-run the expensive Tavily/OpenAI processing to recover anything.
    master = []
    rev_have = sent_have = 0
    for i, r in enumerate(enriched, start=1):
        slug = f"school_{i:03d}"
        rv_raw = load_side(REVIEW_DIR, slug)
        se_raw = load_side(SENT_DIR, slug)
        rev_have += rv_raw is not None
        sent_have += se_raw is not None
        master.append({**r, "research_raw": load_research(slug),
                       "reviews_raw": rv_raw, "sentiment_raw": se_raw})
    with open(OUT_MASTER, "w", encoding="utf-8") as fh:
        json.dump(master, fh, ensure_ascii=False, indent=2)

    print(f"Wrote {len(enriched)} rows -> {OUT_CSV}")
    print(f"Wrote master (full raw record) -> {OUT_MASTER} "
          f"(reviews_raw {rev_have}/{len(enriched)}, sentiment_raw {sent_have}/{len(enriched)})")
    print(f"Research files: {counts['research']}")
    print(f"English breakdown: {counts['english']}")
    print(f"Founding year known: {counts['founding_known']}/{len(enriched)}")
    print(f"Availability breakdown: {avail_counts}")
    print(f"Review trust breakdown: {trust_counts}")
    print(f"Sentiment source: {sent_src_counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
