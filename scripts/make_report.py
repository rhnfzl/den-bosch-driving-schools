#!/usr/bin/env python3
"""Generate the decision report from the enriched dataset (v2 scoring).

Reads:  data/den_bosch_rijscholen_enriched.json
Writes: report/den_bosch_rijschool_shortlist.md

Ranks on `decision_score` = base (CBR-quality + maturity) nudged by a trust-gated
review-sentiment modifier. The raw star rating is NOT scored. n>=25 hard gate on
the headline lists.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "data", "den_bosch_rijscholen_enriched.json")
OUT = os.path.join(ROOT, "report", "den_bosch_rijschool_shortlist.md")

MIN_N = 25  # hard sample-size gate for the headline lists


def num(v, default=-1.0):
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def meets(r):
    return r.get("meets_min_sample") == "yes"


def esc(s):
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ").strip()


def fmt_dec(r):
    d = r.get("decision_score", "")
    return f"**{d}**" if d != "" else "n/a"


def fmt_rel(r):
    lo, hi, n = r.get("pass_rate_ci_low", ""), r.get("pass_rate_ci_high", ""), r.get("sample_n", "")
    s = r.get("reliability_adjusted_score", "")
    return "n/a" if s == "" else f"{s} ([{lo}–{hi}], n={n})"


def fmt_reviews(r):
    """Trust-gated review signal: authenticity dots + content sentiment (not the star)."""
    t = r.get("review_trust", "insufficient")
    s = r.get("sentiment_index", "")
    dots = {"strong": "●●●", "moderate": "●●○", "weak": "●○○", "insufficient": "○○○"}.get(t, "")
    core = f"{dots} {t}"
    if s != "":
        return f"{core} · sent {s}"
    return core


def fmt_avail(r):
    a = r.get("availability", "unknown")
    return {"open": "✅ open", "wait": "⏳ wait", "closed": "⛔ closed", "unknown": "—"}.get(a, a)


def fmt_age(r):
    y, fy, flag = r.get("years_in_business", ""), r.get("founding_year", ""), r.get("maturity_flag", "unknown")
    return f"{flag} (~{y}y, est. {fy})" if (y != "" and fy != "") else flag


def fmt_eng(r):
    e, c = r.get("english_instruction", "unknown"), r.get("english_confidence", "")
    badge = {"yes": "✅ yes", "likely": "🟡 likely", "no": "❌ no", "unknown": "❔ unknown"}.get(e, e)
    return f"{badge} ({c})" if c else badge


def fmt_trans(r):
    return {"manual": "manual", "automatic": "automatic", "both": "both", "unknown": "—"}.get(
        r.get("transmission", "unknown"), "—")


def fmt_contact(r):
    bits = [str(r[k]) for k in ("phone", "website") if r.get(k)]
    return " · ".join(bits) if bits else "—"


def table(rows):
    out = ["| # | School | Town | English | Trans | Decision | Reliability (95% CI, n) | Reviews (trust·sent) | Avail (claimed†) | Maturity | Contact |",
           "|--:|--------|------|---------|-------|---------:|-------------------------|----------------------|------------------|----------|---------|"]
    for i, r in enumerate(rows, 1):
        out.append(
            f"| {i} | {esc(r['rijschool'])} | {esc(r['plaats'])} | {fmt_eng(r)} | {fmt_trans(r)} "
            f"| {fmt_dec(r)} | {fmt_rel(r)} | {esc(fmt_reviews(r))} | {fmt_avail(r)} | {esc(fmt_age(r))} | {esc(fmt_contact(r))} |"
        )
    return "\n".join(out)


def by_dec(rows):
    return sorted(rows, key=lambda r: (num(r.get("decision_score")), num(r.get("years_in_business"))), reverse=True)


def main():
    rows = json.load(open(SRC, encoding="utf-8"))

    english = [r for r in rows if r.get("english_instruction") in ("yes", "likely")]

    eng_big = by_dec([r for r in english if meets(r)])
    eng_small = by_dec([r for r in english if not meets(r)])

    eng_auto = by_dec([r for r in english if meets(r) and r.get("transmission") in ("both", "automatic")])
    eng_manual = by_dec([r for r in english if meets(r) and r.get("transmission") == "manual"])
    eng_ask = by_dec([r for r in english if meets(r) and r.get("transmission") in ("unknown", "")])

    verify = by_dec([r for r in rows if r.get("english_instruction") == "unknown" and meets(r)])[:15]
    no_english = by_dec([r for r in rows if r.get("english_instruction") == "no"])

    full = by_dec([r for r in rows if meets(r) and r.get("decision_score") != ""])

    # Profile sensitivity: same English n>=25 pool, three different sort keys.
    def review_effect(r):
        tw = {"strong": 1.0, "moderate": 0.6, "weak": 0.25, "insufficient": 0.0}.get(r.get("review_trust"), 0.0)
        s = r.get("sentiment_index")
        s = float(s) if s not in ("", None) else 50.0
        return tw * (s - 50.0)
    pool = [r for r in english if meets(r)]
    by_balanced = by_dec(pool)[:6]
    by_quality = sorted(pool, key=lambda r: num(r.get("reliability_adjusted_score")), reverse=True)[:6]
    by_reviews = sorted(pool, key=review_effect, reverse=True)[:6]

    counts = {}
    for r in rows:
        counts[r.get("english_instruction", "unknown")] = counts.get(r.get("english_instruction", "unknown"), 0) + 1

    def reco(r):
        nm = f"**{esc(r['rijschool'])}** ({esc(r['plaats'])})"
        bits = [nm, fmt_eng(r),
                f"decision **{r.get('decision_score')}**",
                f"reliability {r.get('reliability_adjusted_score')} (n={esc(r.get('sample_n'))})",
                fmt_trans(r), fmt_avail(r), esc(fmt_reviews(r)), esc(fmt_age(r))]
        if fmt_contact(r) != "—":
            bits.append(esc(fmt_contact(r)))
        return "  - " + " · ".join(bits)

    L = []
    L.append("# Den Bosch driving schools — enriched shortlist for an English-speaking learner\n")
    L.append("> Pass rates are from the CBR Rijschoolzoeker — a **rolling 12-month window** whose exact period depends "
             "on when the CSV was extracted (CBR showed **~1 Apr 2025 to 31 Mar 2026** around the analysis date). "
             "Everything else (English, transmission, founding year, reviews, sentiment) is enriched via web research + "
             "LLM and re-scored. Ranked on a composite **`decision_score`** with an **n ≥ 25 hard gate** on the "
             "headline lists. Full data (all 121 schools, every column): "
             "`data/den_bosch_rijscholen_enriched.csv`.\n")

    L.append("## TL;DR — where to start\n")
    L.append(f"English is the hard filter; then ranked by `decision_score` among schools with **≥ {MIN_N} exams** "
             "(enough data to trust). Smaller English schools are listed separately in the appendix, not dropped.\n")
    if eng_auto:
        L.append("**English + automatic available** (best fit if you want automaat):")
        L.extend(reco(r) for r in eng_auto[:4])
        L.append("")
    if eng_manual:
        L.append("**English + manual (schakel):**")
        L.extend(reco(r) for r in eng_manual[:4])
        L.append("")
    if eng_ask:
        L.append("**English confirmed, transmission not published — ask whether they do automaat:**")
        L.extend(reco(r) for r in eng_ask[:4])
        L.append("")
    if verify:
        L.append("**Strong schools where English is unconfirmed online — worth a phone call** (you did this with Asro/Time2drive):")
        L.extend(reco(r) for r in verify[:4])
        L.append("")

    L.append("## How the score works\n")
    L.append("- **Hard filters:** English instruction (the shortlist), and **n ≥ 25 exams** (the headline lists) — "
             "small samples are statistically meaningless, so they're gated out but kept in the appendix.")
    L.append("- **`decision_score`** = base **(`0.85·quality + 0.15·maturity`)**, then nudged by a "
             "**trust-gated review modifier** (tunable in `scripts/enrich.py → BASE_WEIGHTS / REVIEW_*`):")
    L.append("  - **quality** = Wilson 95% lower bound on the first-exam pass rate given the exam count "
             "(a 92%-from-30 and a 100%-from-1 are *not* the same bet) — the trustworthy CBR outcome.")
    L.append("  - **maturity** = years in business (capped at 20).")
    L.append("  - **review modifier** = an OpenAI **sentiment** read of *real review text* (\"how the school is\"), "
             "**gated by authenticity** (`review_trust` — how genuine the reviews look vs bought one-liners). Moves the "
             "score up to ±15%. The raw **star rating is deliberately NOT scored** — it's gameable, 5.0-inflated, and "
             "0-correlated with the pass rate. Two models: Claude reads/judges authenticity, OpenAI scores sentiment.")
    L.append("  - **availability** = self-reported (site/aggregators/reviews); **weight 0**, annotation only "
             "(Asro advertises *\"geen wachtlijst\"* yet has a long wait — claims ≠ reality).")
    L.append("")

    L.append("### ⚠️ The core lesson from your own example\n")
    L.append("Asro is **raw CBR rank #1** (92%), yet its site advertises *\"geen wachtlijst\"* — which **contradicts** "
             "your real experience that it had no slots — and we found **no English signal**. Website claims ≠ reality; "
             "that's why this enrichment, and a phone call, matter.\n")

    L.append("## 1. How the weighting changes the order (English, n ≥ 25)\n")
    L.append("Same pool, three different priorities — pick the column that matches how you want to decide:\n")
    cmp = ["| Rank | Balanced `decision_score` (default) | Quality-only (Wilson) | Best-reviewed (trust·sent) |",
           "|--:|------------------------------------|-----------------------|----------------------------|"]
    for i in range(6):
        a = esc(by_balanced[i]["rijschool"]) if i < len(by_balanced) else ""
        b = esc(by_quality[i]["rijschool"]) if i < len(by_quality) else ""
        c = esc(by_reviews[i]["rijschool"]) if i < len(by_reviews) else ""
        cmp.append(f"| {i+1} | {a} | {b} | {c} |")
    L.append("\n".join(cmp))
    L.append("")

    L.append(f"## 2. English-capable shortlist — n ≥ {MIN_N} ({len(eng_big)} schools)\n")
    L.append("Ranked by `decision_score`.\n")
    L.append(table(eng_big) if eng_big else "_None._")
    L.append("")
    L.append(f"### 2b. Appendix — English but small sample (n < {MIN_N}, {len(eng_small)} schools)\n")
    L.append("Confirmed/likely English but too few exams to trust the pass rate — treat the score as a weak prior.\n")
    L.append(table(eng_small) if eng_small else "_None._")
    L.append("")

    L.append("## 2c. What students actually say (top English picks)\n")
    L.append("OpenAI sentiment over real review quotes, gated by authenticity — read this, not the star.\n")
    said = False
    for r in eng_big[:8]:
        summ = esc(r.get("review_summary") or "")
        if not summ:
            continue
        said = True
        L.append(f"- **{esc(r['rijschool'])}** — *{r.get('review_trust')}* trust, sentiment {r.get('sentiment_index')}: {summ}")
    if not said:
        L.append("_Review analysis still running._")
    L.append("")
    L.append(f"## 3. Strong schools to verify for English by phone — n ≥ {MIN_N} ({len(verify)})\n")
    L.append("Statistically solid and well-ranked, but **no English signal found online**. Best candidates for a quick call.\n")
    L.append(table(verify) if verify else "_None._")
    L.append("")

    if no_english:
        L.append(f"## 4. Confirmed Dutch-only ({len(no_english)})\n")
        L.append("Positive evidence of no English instruction — skip unless something changes.\n")
        L.append(table(no_english))
        L.append("")

    L.append(f"## 5. Full ranking by decision_score (n ≥ {MIN_N}, top 30)\n")
    L.append("Every school with every column is in the CSV; here are the top 30 that clear the sample gate.\n")
    top = ["| # | School | Town | Decision | Reliability (CI, n) | English | Avail (claimed†) | Maturity |",
           "|--:|--------|------|---------:|---------------------|---------|------------------|----------|"]
    for i, r in enumerate(full[:30], 1):
        top.append(
            f"| {i} | {esc(r['rijschool'])} | {esc(r['plaats'])} | {fmt_dec(r)} | {fmt_rel(r)} "
            f"| {fmt_eng(r)} | {fmt_avail(r)} | {esc(fmt_age(r))} |"
        )
    L.append("\n".join(top))
    L.append("")

    L.append("## 6. What changed vs the raw CBR ranking\n")
    cov = ", ".join(f"{k}={counts.get(k, 0)}" for k in ["yes", "likely", "no", "unknown"])
    raw1 = min(rows, key=lambda r: num(r.get("rank_first_weighted"), 9999))
    L.append(f"- **Raw CBR #1 {esc(raw1['rijschool'])}** ({esc(raw1.get('slagingspercentage_eerste_examens'))}% on "
             f"n={esc(raw1.get('sample_n'))}) is **{fmt_eng(raw1)}** for English and `availability={raw1.get('availability')}` "
             f"— it leaves your usable set entirely.")
    if eng_auto:
        te = eng_auto[0]
        L.append(f"- **Top English + automatic pick: {esc(te['rijschool'])}** — decision {te.get('decision_score')}, "
                 f"reliability {te.get('reliability_adjusted_score')}, reviews {esc(fmt_reviews(te))}, n={esc(te.get('sample_n'))}, "
                 f"raw CBR rank {esc(te.get('rank_first_weighted'))}.")
    usable = counts.get("yes", 0) + counts.get("likely", 0)
    L.append(f"- **English coverage across all {len(rows)} schools:** {cov} — only **{usable}** usable without a phone call, "
             f"of which **{len(eng_big)}** also clear the n ≥ {MIN_N} sample gate.")
    L.append("")

    L.append("## 7. Limitations & how to tune\n")
    L.append("- **No per-school year-by-year history exists publicly** — CBR shows only the current rolling window. "
             "The Wilson interval is the substitute, not historical trend data.")
    L.append("- `english = unknown` means *no online evidence either way* — **not** \"no English\". Call them (section 3).")
    L.append("- **† Avail (claimed)** is self-reported (the school's own site, aggregators, or reviews) and is **not** "
             "weighted in the score by default — it routinely contradicts reality (Asro shows *\"geen wachtlijst\"* yet "
             "has a long wait). Treat it as a question to ask on the phone, not a fact.")
    L.append("- Founding years are estimates; `kvk_number` lets you confirm a finalist at kvk.nl.")
    L.append("- **Re-weight freely:** edit `WEIGHTS` / `MIN_N` in `scripts/enrich.py` and re-run "
             "`enrich.py` then `make_report.py`. Section 1 shows how sensitive the order is to the choice.\n")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"Wrote report -> {OUT}")
    print(f"English n>={MIN_N}: {len(eng_big)} | English small-sample: {len(eng_small)} | "
          f"verify-by-call: {len(verify)} | dutch-only: {len(no_english)}")


if __name__ == "__main__":
    main()
