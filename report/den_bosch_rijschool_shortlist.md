# Den Bosch driving schools — enriched shortlist for an English-speaking learner

> Pass rates are from the CBR Rijschoolzoeker — a **rolling 12-month window** whose exact period depends on when the CSV was extracted (CBR showed **~1 Apr 2025 to 31 Mar 2026** around the analysis date). Everything else (English, transmission, founding year, reviews, sentiment) is enriched via web research + LLM and re-scored. Ranked on a composite **`decision_score`** with an **n ≥ 25 hard gate** on the headline lists. Full data (all 121 schools, every column): `data/den_bosch_rijscholen_enriched.csv`.

## TL;DR — where to start

English is the hard filter; then ranked by `decision_score` among schools with **≥ 25 exams** (enough data to trust). Smaller English schools are listed separately in the appendix, not dropped.

**English + automatic available** (best fit if you want automaat):
  - **Autorijschool Amir** ('S-HERTOGENBOSCH) · ✅ yes (high) · decision **72.2** · reliability 58.1 (n=79) · both · — · ●●● strong · sent 95 · established (~19y, est. 2007) · 073 611 1535 · https://www.autorijschoolamir.nl
  - **M. van Heugten** (ROSMALEN) · 🟡 likely (med) · decision **64.5** · reliability 52.5 (n=87) · both · ✅ open · ●●○ moderate · sent 95 · established (~23y, est. 2003) · 06-43404288 · https://www.verkeersschoolmvanheugten.nl
  - **Jve Rijopleidingen B.V. t.h.o.d.n. ANWB Rijopleiding** ('S-HERTOGENBOSCH) · ✅ yes (med) · decision **59.4** · reliability 53.0 (n=264) · both · — · ●●○ moderate · sent 58 · established (~18y, est. 2008) · 073 623 2444 · https://www.anwb.nl/auto/rijbewijs/rijschool-den-bosch
  - **WeGo academy** ('S-HERTOGENBOSCH) · 🟡 likely (low) · decision **24.3** · reliability 18.9 (n=58) · both · — · ●○○ weak · sent 94 · unknown · 0616053413

**English + manual (schakel):**
  - **Time2drive** ('S-HERTOGENBOSCH) · ✅ yes (high) · decision **58.6** · reliability 43.4 (n=44) · manual · ⏳ wait · ●●● strong · sent 93 · established (~20y, est. 2006) · 06-30900960 · https://time2drive.nl
  - **Autorijschool Safe Away** ('S-HERTOGENBOSCH) · ✅ yes (high) · decision **23.7** · reliability 24.0 (n=109) · manual · — · ●●○ moderate · sent 96 · new (~2y, est. 2024) · 06 4555 5000 · https://safeaway.nl
  - **Autorijschool Driezeeg** (BERLICUM NB) · 🟡 likely (med) · decision **18.8** · reliability 20.3 (n=45) · manual · — · ○○○ insufficient · sent 88 · new (~2y, est. 2024) · 06-41730188 · https://driezeeg.nl

**English confirmed, transmission not published — ask whether they do automaat:**
  - **Pieters Rijopleidingen** (ROSMALEN) · ✅ yes (high) · decision **57.6** · reliability 54.5 (n=31) · — · — · ○○○ insufficient · sent 60 · established (~15y, est. 2011) · 06 45 57 43 09 · https://www.pietersrijopleidingen.nl
  - **rij-correct** ('S-HERTOGENBOSCH) · ✅ yes (med) · decision **43.7** · reliability 32.5 (n=46) · — · — · ●●○ moderate · sent 96 · established (~17y, est. 2009) · 06 26 93 97 18
  - **Motorrijles Max** ('S-HERTOGENBOSCH) · ✅ yes (high) · decision **43.6** · reliability 43.5 (n=86) · — · ✅ open · ●○○ weak · sent 94 · established (~7y, est. 2019) · 06 44303081 · https://motorrijlesmax.nl
  - **Autorijschool Heinsman** ('S-HERTOGENBOSCH) · ✅ yes (high) · decision **33.5** · reliability 26.1 (n=62) · — · — · ●●○ moderate · sent 92 · established (~12y, est. 2014) · 06 30142214 · https://www.autorijschoolheinsman.nl

**Strong schools where English is unconfirmed online — worth a phone call** (you did this with Asro/Time2drive):
  - **Rijschool Asro** ('S-HERTOGENBOSCH) · ❔ unknown (low) · decision **77.8** · reliability 76.9 (n=30) · manual · ✅ open · ●●○ moderate · sent 88 · unknown · 0658969123 · https://www.rijschoolasro.nl
  - **Autorijschool Eddy Kok** (NIEUWKUIJK) · ❔ unknown (low) · decision **70.4** · reliability 73.1 (n=34) · — · — · ○○○ insufficient · sent 70 · established (~11y, est. 2015) · 06-45089266 · https://autorijschooleddykok.nl
  - **Autorijschool Driss** ('S-HERTOGENBOSCH) · ❔ unknown (low) · decision **64.6** · reliability 57.9 (n=76) · — · — · ●○○ weak · sent 90 · established (~18y, est. 2008) · https://rijschooldriss.nl
  - **Verkeersschool Erico v.d. Broek** (ROSMALEN) · ❔ unknown (low) · decision **64.4** · reliability 55.0 (n=118) · — · — · ●●○ moderate · sent 74 · established (~61y, est. 1965) · (073) 521 03 06 · https://www.verkeersschoolvdbroek.com

## How the score works

- **Hard filters:** English instruction (the shortlist), and **n ≥ 25 exams** (the headline lists) — small samples are statistically meaningless, so they're gated out but kept in the appendix.
- **`decision_score`** = base **(`0.85·quality + 0.15·maturity`)**, then nudged by a **trust-gated review modifier** (tunable in `scripts/enrich.py → BASE_WEIGHTS / REVIEW_*`):
  - **quality** = Wilson 95% lower bound on the first-exam pass rate given the exam count (a 92%-from-30 and a 100%-from-1 are *not* the same bet) — the trustworthy CBR outcome.
  - **maturity** = years in business (capped at 20).
  - **review modifier** = an OpenAI **sentiment** read of *real review text* ("how the school is"), **gated by authenticity** (`review_trust` — how genuine the reviews look vs bought one-liners). Moves the score up to ±15%. The raw **star rating is deliberately NOT scored** — it's gameable, 5.0-inflated, and 0-correlated with the pass rate. Two models: Claude reads/judges authenticity, OpenAI scores sentiment.
  - **availability** = self-reported (site/aggregators/reviews); **weight 0**, annotation only (Asro advertises *"geen wachtlijst"* yet has a long wait — claims ≠ reality).

### ⚠️ The core lesson from your own example

Asro is **raw CBR rank #1** (92%), yet its site advertises *"geen wachtlijst"* — which **contradicts** your real experience that it had no slots — and we found **no English signal**. Website claims ≠ reality; that's why this enrichment, and a phone call, matter.

## 1. How the weighting changes the order (English, n ≥ 25)

Same pool, three different priorities — pick the column that matches how you want to decide:

| Rank | Balanced `decision_score` (default) | Quality-only (Wilson) | Best-reviewed (trust·sent) |
|--:|------------------------------------|-----------------------|----------------------------|
| 1 | Autorijschool Amir | Autorijschool Amir | Autorijschool Amir |
| 2 | M. van Heugten | Pieters Rijopleidingen | Time2drive |
| 3 | Jve Rijopleidingen B.V. t.h.o.d.n. ANWB Rijopleiding | Jve Rijopleidingen B.V. t.h.o.d.n. ANWB Rijopleiding | Autorijschool Safe Away |
| 4 | Time2drive | M. van Heugten | rij-correct |
| 5 | Pieters Rijopleidingen | Motorrijles Max | M. van Heugten |
| 6 | rij-correct | Time2drive | Autorijschool Reches |

## 2. English-capable shortlist — n ≥ 25 (13 schools)

Ranked by `decision_score`.

| # | School | Town | English | Trans | Decision | Reliability (95% CI, n) | Reviews (trust·sent) | Avail (claimed†) | Maturity | Contact |
|--:|--------|------|---------|-------|---------:|-------------------------|----------------------|------------------|----------|---------|
| 1 | Autorijschool Amir | 'S-HERTOGENBOSCH | ✅ yes (high) | both | **72.2** | 58.1 ([58.1–78.1], n=79) | ●●● strong · sent 95 | — | established (~19y, est. 2007) | 073 611 1535 · https://www.autorijschoolamir.nl |
| 2 | M. van Heugten | ROSMALEN | 🟡 likely (med) | both | **64.5** | 52.5 ([52.5–72.4], n=87) | ●●○ moderate · sent 95 | ✅ open | established (~23y, est. 2003) | 06-43404288 · https://www.verkeersschoolmvanheugten.nl |
| 3 | Jve Rijopleidingen B.V. t.h.o.d.n. ANWB Rijopleiding | 'S-HERTOGENBOSCH | ✅ yes (med) | both | **59.4** | 53.0 ([53.0–64.8], n=264) | ●●○ moderate · sent 58 | — | established (~18y, est. 2008) | 073 623 2444 · https://www.anwb.nl/auto/rijbewijs/rijschool-den-bosch |
| 4 | Time2drive | 'S-HERTOGENBOSCH | ✅ yes (high) | manual | **58.6** | 43.4 ([43.4–71.4], n=44) | ●●● strong · sent 93 | ⏳ wait | established (~20y, est. 2006) | 06-30900960 · https://time2drive.nl |
| 5 | Pieters Rijopleidingen | ROSMALEN | ✅ yes (high) | — | **57.6** | 54.5 ([54.5–84.7], n=31) | ○○○ insufficient · sent 60 | — | established (~15y, est. 2011) | 06 45 57 43 09 · https://www.pietersrijopleidingen.nl |
| 6 | rij-correct | 'S-HERTOGENBOSCH | ✅ yes (med) | — | **43.7** | 32.5 ([32.5–60.1], n=46) | ●●○ moderate · sent 96 | — | established (~17y, est. 2009) | 06 26 93 97 18 |
| 7 | Motorrijles Max | 'S-HERTOGENBOSCH | ✅ yes (high) | — | **43.6** | 43.5 ([43.5–64.1], n=86) | ●○○ weak · sent 94 | ✅ open | established (~7y, est. 2019) | 06 44303081 · https://motorrijlesmax.nl |
| 8 | Autorijschool Heinsman | 'S-HERTOGENBOSCH | ✅ yes (high) | — | **33.5** | 26.1 ([26.1–49.4], n=62) | ●●○ moderate · sent 92 | — | established (~12y, est. 2014) | 06 30142214 · https://www.autorijschoolheinsman.nl |
| 9 | Autorijschool Reches | VUGHT | ✅ yes (med) | — | **29.5** | 14.6 ([14.6–34.4], n=67) | ●●○ moderate · sent 93 | ✅ open | established (~36y, est. 1990) | 073-656 93 07 / 06-22 39 29 42 · https://www.reches.nl |
| 10 | Rijschool Henk van Heck | ROSSUM GLD | 🟡 likely (low) | — | **25.4** | 26.4 ([26.4–53.3], n=47) | ○○○ insufficient · sent 88 | — | establishing (~4y, est. 2022) | 06-52143468 · https://www.rijschoolhenkvanheck.nl |
| 11 | WeGo academy | 'S-HERTOGENBOSCH | 🟡 likely (low) | both | **24.3** | 18.9 ([18.9–41.7], n=58) | ●○○ weak · sent 94 | — | unknown | 0616053413 |
| 12 | Autorijschool Safe Away | 'S-HERTOGENBOSCH | ✅ yes (high) | manual | **23.7** | 24.0 ([24.0–41.2], n=109) | ●●○ moderate · sent 96 | — | new (~2y, est. 2024) | 06 4555 5000 · https://safeaway.nl |
| 13 | Autorijschool Driezeeg | BERLICUM NB | 🟡 likely (med) | manual | **18.8** | 20.3 ([20.3–46.6], n=45) | ○○○ insufficient · sent 88 | — | new (~2y, est. 2024) | 06-41730188 · https://driezeeg.nl |

### 2b. Appendix — English but small sample (n < 25, 8 schools)

Confirmed/likely English but too few exams to trust the pass rate — treat the score as a weak prior.

| # | School | Town | English | Trans | Decision | Reliability (95% CI, n) | Reviews (trust·sent) | Avail (claimed†) | Maturity | Contact |
|--:|--------|------|---------|-------|---------:|-------------------------|----------------------|------------------|----------|---------|
| 1 | Rijschool Story | ROSMALEN | 🟡 likely (low) | manual | **42.0** | 40.6 ([40.6–89.8], n=10) | ○○○ insufficient · sent 92 | — | unknown | 06-12121219 · https://rijschoolstory.nl |
| 2 | Rijschool Pip | ROSMALEN | ✅ yes (high) | manual | **30.1** | 33.6 ([33.6–94.7], n=5) | ○○○ insufficient · sent 88 | ⛔ closed | new (~2y, est. 2024) | 0612277311 · https://rijschoolpip.nl |
| 3 | M & S Rijopleidingen en Coaching V.O.F. | 'S-HERTOGENBOSCH | 🟡 likely (low) | — | **27.3** | 20.9 ([20.9–94.0], n=3) | ●●○ moderate · sent 94 | — | unknown | 06 18963711 · https://msrijco.nl |
| 4 | Rijschool Eigen-Wijs | VLIJMEN | 🟡 likely (med) | — | **15.6** | 15.2 ([15.2–71.3], n=8) | ●●○ moderate · sent 96 | — | new (~2y, est. 2024) | 06 20307101 · https://rijschooleigen-wijs.nl |
| 5 | Autorijschool Zainab | 'S-HERTOGENBOSCH | ✅ yes (high) | both | **15.0** | 16.8 ([16.8–68.7], n=10) | ○○○ insufficient · sent 60 | — | new (~1y, est. 2025) | 06 20896343 · https://autorijschoolamir.nl |
| 6 | Rijschool Sosan | 'S-HERTOGENBOSCH | ✅ yes (high) | automatic | **10.2** | 8.5 ([8.5–54.4], n=11) | ●●○ moderate · sent 92 | — | establishing (~3y, est. 2023) | 06 44303081 |
| 7 | Pass2Drive | 'S-HERTOGENBOSCH | ✅ yes (high) | manual | **7.5** | 7.1 ([7.1–59.1], n=8) | ○○○ insufficient · sent 87 | ✅ open | new (~2y, est. 2024) | 0624252591 · https://pass2drive.nl |
| 8 | RijbijSabah.nl | 'S-HERTOGENBOSCH | ✅ yes (high) | — | **3.8** | 0.0 ([0.0–79.3], n=1) | ○○○ insufficient · sent 50 | — | establishing (~5y, est. 2021) | 0621147109 · https://www.rijbijsabah.nl |

## 2c. What students actually say (top English picks)

OpenAI sentiment over real review quotes, gated by authenticity — read this, not the star.

- **Autorijschool Amir** — *strong* trust, sentiment 95: Students consistently describe Amir as a calm, patient, punctual instructor who explains clearly (even with an iPad), excels with nervous/faalangst learners, and gets many to pass first time; multiple expat/English-speaking and foreign-experienced learners praise him as language being no barrier. The few nuances (one over-a-year trajectory, an occasional first-time fail before a successful retake) keep it credible, but the corpus is overwhelmingly and uniformly positive.
- **M. van Heugten** — *moderate* trust, sentiment 95: Students consistently describe Michael (the owner) and instructors like Abid as calm, patient and clear, with quick exam scheduling and many 'passed first time' results, though the review corpus is heavily weighted toward one-day trailer/BE courses and short praise rather than detailed full car-licence (B) journeys. No negative reviews were found and reviews are Google/Trustoo only (no independent verified platform), so the uniformly 5-star picture should be read with some caution.
- **Jve Rijopleidingen B.V. t.h.o.d.n. ANWB Rijopleiding** — *moderate* trust, sentiment 58: Students are split: positive reviews praise clear instructors (Ahmed, Fatiha), a friendly and engaged office team, and passing first time, while a substantive minority of Google reviews complain about being upsold unnecessary lessons, treated as 'a number', long waits for (re)exams, and high costs without targeted coaching. The ANWB-owned verified platform (Tevreden.nl) skews more positive but with very short, survey-style comments.
- **Time2drive** — *strong* trust, sentiment 93: Students consistently describe Time2drive (one-man school run by instructor Peter) as calm, patient and methodical, tailoring lessons to the individual and being especially good with nervous learners and faalangst; multiple expats explicitly note lessons, mock exam and CBR exam were done fluently in English and several passed first time. The only mild negatives are a multi-week wait for a starting spot and that lessons are manual-transmission only.
- **Pieters Rijopleidingen** — *insufficient* trust, sentiment 60: No readable review text exists for Pieters Rijopleidingen anywhere; the only feedback is 7 star-only Google ratings (all 5-star, no written descriptions) and no verified-platform reviews, so student experience cannot be judged from actual review content. The school's own marketing describes one fixed instructor, patience, structured lessons, and specialisation in autism/ADHD/exam-anxiety, but this is unverified by any review body.
- **rij-correct** — *moderate* trust, sentiment 96: On Google (4.9, 170 reviews) students - many of them English-speaking expats - praise rij-correct's professional, patient instructors (Farlan, Els, Fabian, Nordin, Najiem), the personal approach, and strong exam preparation, with several reporting passing first time. No critical or mixed reviews were found, and there is no independent verified-review platform page for this specific school, so trust is capped at moderate.
- **Motorrijles Max** — *weak* trust, sentiment 94: Readable review text for Motorrijles Max is almost entirely curated marketing copy reused verbatim across its sibling brand sites (Rijschool Max, Rijschool Baron), plus brand-mixed aggregator snippets, so it cannot be independently verified. The available quotes are uniformly very positive - praising a patient, honest instructor who explains clearly, is flexible, helps nervous or previously-failed learners, and gets students passed (often first time), with lessons offered in NL/EN/AR - but the absence of any independent or critical reviews means the glowing picture should be treated with caution.
- **Autorijschool Heinsman** — *moderate* trust, sentiment 92: The handful of reviews for this one-man school (instructor Ronald Heinsman) are uniformly positive: students describe him as clear, critical, patient and pleasant, with several saying they passed in one go and were efficiently prepared for the exam. However, the corpus is thin (only ~4 distinct Google reviews, all old and two of them generic one-liners), so confidence is moderate at best.

## 3. Strong schools to verify for English by phone — n ≥ 25 (15)

Statistically solid and well-ranked, but **no English signal found online**. Best candidates for a quick call.

| # | School | Town | English | Trans | Decision | Reliability (95% CI, n) | Reviews (trust·sent) | Avail (claimed†) | Maturity | Contact |
|--:|--------|------|---------|-------|---------:|-------------------------|----------------------|------------------|----------|---------|
| 1 | Rijschool Asro | 'S-HERTOGENBOSCH | ❔ unknown (low) | manual | **77.8** | 76.9 ([76.9–97.5], n=30) | ●●○ moderate · sent 88 | ✅ open | unknown | 0658969123 · https://www.rijschoolasro.nl |
| 2 | Autorijschool Eddy Kok | NIEUWKUIJK | ❔ unknown (low) | — | **70.4** | 73.1 ([73.1–95.2], n=34) | ○○○ insufficient · sent 70 | — | established (~11y, est. 2015) | 06-45089266 · https://autorijschooleddykok.nl |
| 3 | Autorijschool Driss | 'S-HERTOGENBOSCH | ❔ unknown (low) | — | **64.6** | 57.9 ([57.9–78.3], n=76) | ●○○ weak · sent 90 | — | established (~18y, est. 2008) | https://rijschooldriss.nl |
| 4 | Verkeersschool Erico v.d. Broek | ROSMALEN | ❔ unknown (low) | — | **64.4** | 55.0 ([55.0–72.1], n=118) | ●●○ moderate · sent 74 | — | established (~61y, est. 1965) | (073) 521 03 06 · https://www.verkeersschoolvdbroek.com |
| 5 | NRV Autorijschool | 'S-HERTOGENBOSCH | ❔ unknown (low) | — | **64.2** | 57.9 ([57.9–84.2], n=41) | ○○○ insufficient · sent 5 | — | established (~26y, est. 2000) | +31 6 21710000 · https://autorijschoolnrv.nl |
| 6 | Verkeersschool Bakker V.O.F. | VLIJMEN | ❔ unknown (low) | both | **63.4** | 51.6 ([51.6–66.0], n=175) | ●●○ moderate · sent 93 | — | established (~35y, est. 1991) | (073) 888 99 00 / 06 51 43 42 79 · https://verkeersschool-bakker.nl |
| 7 | Autorijschool van Hoorn | 'S-HERTOGENBOSCH | ❔ unknown (low) | — | **62.6** | 51.5 ([51.5–66.1], n=172) | ●●○ moderate · sent 86 | — | established (~29y, est. 1997) | 06 18 94 25 44 · https://rijschoolvanhoorn.nl |
| 8 | Autorijschool de Gier | VUGHT | ❔ unknown (low) | — | **62.3** | 58.3 ([58.3–85.3], n=38) | ○○○ insufficient · sent 50 | — | established (~17y, est. 2009) | 06-20921891 · https://www.autorijschooldegier.nl |
| 9 | Rijschool van Venrooij | ROSMALEN | ❔ unknown (low) | — | **62.1** | 65.0 ([65.0–89.6], n=39) | ●●○ moderate · sent 94 | — | establishing (~3y, est. 2023) | 06-39482555 · https://rijschool-vanvenrooij.nl |
| 10 | Autorijschool Coenen | 'S-HERTOGENBOSCH | ❔ unknown (low) | both | **61.6** | 49.2 ([49.2–69.9], n=83) | ●●● strong · sent 78 | — | established (~55y, est. 1971) | 073-6480284 · https://autorijschoolcoenen.nl |
| 11 | Rijschool Van Dijk | HEDEL | ❔ unknown (low) | both | **59.0** | 51.7 ([51.7–79.4], n=41) | ●●○ moderate · sent 88 | — | established (~15y, est. 2011) | 073-599 6666 · https://www.rsvd.nl |
| 12 | Rijschool Arthur | VUGHT | ❔ unknown (low) | both | **58.8** | 55.9 ([55.9–86.5], n=29) | ○○○ insufficient · sent 50 | — | established (~15y, est. 2011) | 06-13420045 · https://www.rijschool-arthur.nl |
| 13 | Autorijschool van Grunderbeek | ROSMALEN | ❔ unknown (low) | both | **58.5** | 48.1 ([48.1–67.3], n=98) | ●●○ moderate · sent 92 | — | established (~18y, est. 2008) | 06 15 85 10 40 · https://www.vangrunderbeek.nl |
| 14 | Haarsteegse Autorijschool | HAARSTEEG | ❔ unknown (low) | — | **57.2** | 49.7 ([49.7–80.7], n=32) | ○○○ insufficient · sent 20 | — | established (~40y, est. 1986) | 073 511 6016 · https://ceesdevaan.nl |
| 15 | Rijschool De Draak | ROSMALEN | ❔ unknown (low) | manual | **54.9** | 57.0 ([57.0–87.2], n=29) | ●●○ moderate · sent 96 | — | establishing (~3y, est. 2023) | 06 29805240 · https://rijschooldedraak.nl |

## 4. Confirmed Dutch-only (19)

Positive evidence of no English instruction — skip unless something changes.

| # | School | Town | English | Trans | Decision | Reliability (95% CI, n) | Reviews (trust·sent) | Avail (claimed†) | Maturity | Contact |
|--:|--------|------|---------|-------|---------:|-------------------------|----------------------|------------------|----------|---------|
| 1 | Autorijschool Marcel van den Heuvel | ROSMALEN | ❌ no (low) | manual | **69.7** | 61.6 ([61.6–83.5], n=59) | ●○○ weak · sent 96 | — | established (~20y, est. 2006) | (073) 521 03 07 |
| 2 | Rijschool Jan Dekkers | AMMERZODEN | ❌ no (med) | manual | **68.6** | 63.1 ([63.1–95.7], n=17) | ○○○ insufficient · sent 62 | — | established (~21y, est. 2005) | 06-20914326 · https://jdekkers.nl |
| 3 | Auto en Motorrijschool Erik Barella | 'S-HERTOGENBOSCH | ❌ no (low) | — | **64.1** | 56.7 ([56.7–82.1], n=46) | ●●○ moderate · sent 58 | — | established (~28y, est. 1998) | 06 51518421 · https://rijschoolrosmalen.nl |
| 4 | Van der Ven Rijopleidingen | HEDEL | ❌ no (med) | both | **61.1** | 54.5 ([54.5–84.7], n=31) | ●○○ weak · sent 96 | ✅ open | established (~17y, est. 2009) | (073) 599 25 35 · https://www.vandervenrijopleidingen.nl |
| 5 | Autorijschool John Van Zuijdam | HEDEL | ❌ no (med) | manual | **59.5** | 51.4 ([51.4–97.3], n=8) | ●○○ weak · sent 68 | — | established (~47y, est. 1979) | 06-54655898 · https://www.zuijdam.nl/zuijdam |
| 6 | Verkeersschool Vlaspoel | ROSMALEN | ❌ no (low) | — | **55.5** | 47.2 ([47.2–74.8], n=44) | ●●○ moderate · sent 95 | — | established (~15y, est. 2011) | 06-16393895 · https://www.verkeersschoolvlaspoel.nl |
| 7 | Autorijschool M. Van Boxtel | SINT MICHIELSGESTEL | ❌ no (low) | — | **53.9** | 46.6 ([46.6–82.5], n=23) | ○○○ insufficient · sent 50 | — | established (~19y, est. 2007) | (073) 551 52 70 / 06 15623978 · https://www.autorijschoolmvanboxtel.nl |
| 8 | Rijles Mera | 'S-HERTOGENBOSCH | ❌ no (med) | — | **52.6** | 51.3 ([51.3–76.6], n=51) | ●●○ moderate · sent 93 | — | established (~7y, est. 2019) | 06 87 50 66 00 |
| 9 | Les & Slaag | SINT-MICHIELSGESTEL | ❌ no (med) | — | **50.7** | 46.4 ([46.4–63.3], n=130) | ●●○ moderate · sent 95 | ✅ open | established (~10y, est. 2016) | 06 55 37 30 92 · https://lesenslaag.nl |
| 10 | Auto- & Motorrijschool Signaal | VUGHT | ❌ no (low) | both | **49.5** | 37.1 ([37.1–73.3], n=25) | ●●○ moderate · sent 85 | — | established (~35y, est. 1991) | 073 657 0159 · https://www.rijschoolsignaal.nl |
| 11 | Autorijschool van de Sande | VLIJMEN | ❌ no (med) | — | **46.9** | 47.3 ([47.3–76.3], n=39) | ●○○ weak · sent 92 | — | established (~7y, est. 2019) | 06 23 88 02 84 · https://autorijschoolvandesande.nl |
| 12 | Autorijschool Thomassen | ROSMALEN | ❌ no (low) | manual | **45.6** | 40.2 ([40.2–69.0], n=42) | ●●○ moderate · sent 92 | — | established (~11y, est. 2015) | 06-42142499 · https://rijschoolthomassen.nl |
| 13 | Autorijschool Kwaks | NULAND | ❌ no (low) | — | **43.9** | 42.0 ([42.0–65.6], n=65) | ○○○ insufficient · sent 76 | — | established (~11y, est. 2015) | 073 850 09 98 |
| 14 | Autorijschool Johan Helvoirt | HELVOIRT | ❌ no (med) | — | **41.7** | 35.8 ([35.8–54.5], n=105) | ○○○ insufficient · sent 50 | — | established (~15y, est. 2011) | 06-23781131 · https://autorijschoolhelvoirt.nl |
| 15 | Autorijschool van Heeswijk | SINT-MICHIELSGESTEL | ❌ no (low) | — | **41.7** | 43.8 ([43.8–100.0], n=3) | ○○○ insufficient · sent 50 | — | established (~6y, est. 2020) | 073 5942 787 |
| 16 | Rijschool Azizi | 'S-HERTOGENBOSCH | ❌ no (low) | — | **32.4** | 25.5 ([25.5–45.9], n=80) | ●○○ weak · sent 93 | — | established (~13y, est. 2013) | 06 13 86 52 56 |
| 17 | Autorijschool J.P. Valentijn t.h.o.d.n. NXXT | VLIJMEN | ❌ no (low) | both | **23.3** | 11.5 ([11.5–38.1], n=35) | ○○○ insufficient · sent 50 | ✅ open | established (~18y, est. 2008) | (073) 511 70 57 · http://www.autorijschooljpvalentijn.nl |
| 18 | HalimRijschool | VUGHT | ❌ no (med) | both | **20.0** | 16.6 ([16.6–33.4], n=97) | ●●○ moderate · sent 92 | — | established (~6y, est. 2020) | 06 12727478 · https://halimrijschool.nl |
| 19 | G.J.C.J. Hanegraaf | ROSMALEN | ❌ no (low) | — | **16.8** | 1.6 ([1.6–9.7], n=103) | ●○○ weak · sent 84 | — | established (~42y, est. 1984) | 073 521 0410 · https://www.autorijschoolhanegraaf.nl |

## 5. Full ranking by decision_score (n ≥ 25, top 30)

Every school with every column is in the CSV; here are the top 30 that clear the sample gate.

| # | School | Town | Decision | Reliability (CI, n) | English | Avail (claimed†) | Maturity |
|--:|--------|------|---------:|---------------------|---------|------------------|----------|
| 1 | Rijschool Asro | 'S-HERTOGENBOSCH | **77.8** | 76.9 ([76.9–97.5], n=30) | ❔ unknown (low) | ✅ open | unknown |
| 2 | Autorijschool Amir | 'S-HERTOGENBOSCH | **72.2** | 58.1 ([58.1–78.1], n=79) | ✅ yes (high) | — | established (~19y, est. 2007) |
| 3 | Autorijschool Eddy Kok | NIEUWKUIJK | **70.4** | 73.1 ([73.1–95.2], n=34) | ❔ unknown (low) | — | established (~11y, est. 2015) |
| 4 | Autorijschool Marcel van den Heuvel | ROSMALEN | **69.7** | 61.6 ([61.6–83.5], n=59) | ❌ no (low) | — | established (~20y, est. 2006) |
| 5 | Autorijschool Driss | 'S-HERTOGENBOSCH | **64.6** | 57.9 ([57.9–78.3], n=76) | ❔ unknown (low) | — | established (~18y, est. 2008) |
| 6 | M. van Heugten | ROSMALEN | **64.5** | 52.5 ([52.5–72.4], n=87) | 🟡 likely (med) | ✅ open | established (~23y, est. 2003) |
| 7 | Verkeersschool Erico v.d. Broek | ROSMALEN | **64.4** | 55.0 ([55.0–72.1], n=118) | ❔ unknown (low) | — | established (~61y, est. 1965) |
| 8 | NRV Autorijschool | 'S-HERTOGENBOSCH | **64.2** | 57.9 ([57.9–84.2], n=41) | ❔ unknown (low) | — | established (~26y, est. 2000) |
| 9 | Auto en Motorrijschool Erik Barella | 'S-HERTOGENBOSCH | **64.1** | 56.7 ([56.7–82.1], n=46) | ❌ no (low) | — | established (~28y, est. 1998) |
| 10 | Verkeersschool Bakker V.O.F. | VLIJMEN | **63.4** | 51.6 ([51.6–66.0], n=175) | ❔ unknown (low) | — | established (~35y, est. 1991) |
| 11 | Autorijschool van Hoorn | 'S-HERTOGENBOSCH | **62.6** | 51.5 ([51.5–66.1], n=172) | ❔ unknown (low) | — | established (~29y, est. 1997) |
| 12 | Autorijschool de Gier | VUGHT | **62.3** | 58.3 ([58.3–85.3], n=38) | ❔ unknown (low) | — | established (~17y, est. 2009) |
| 13 | Rijschool van Venrooij | ROSMALEN | **62.1** | 65.0 ([65.0–89.6], n=39) | ❔ unknown (low) | — | establishing (~3y, est. 2023) |
| 14 | Autorijschool Coenen | 'S-HERTOGENBOSCH | **61.6** | 49.2 ([49.2–69.9], n=83) | ❔ unknown (low) | — | established (~55y, est. 1971) |
| 15 | Van der Ven Rijopleidingen | HEDEL | **61.1** | 54.5 ([54.5–84.7], n=31) | ❌ no (med) | ✅ open | established (~17y, est. 2009) |
| 16 | Jve Rijopleidingen B.V. t.h.o.d.n. ANWB Rijopleiding | 'S-HERTOGENBOSCH | **59.4** | 53.0 ([53.0–64.8], n=264) | ✅ yes (med) | — | established (~18y, est. 2008) |
| 17 | Rijschool Van Dijk | HEDEL | **59.0** | 51.7 ([51.7–79.4], n=41) | ❔ unknown (low) | — | established (~15y, est. 2011) |
| 18 | Rijschool Arthur | VUGHT | **58.8** | 55.9 ([55.9–86.5], n=29) | ❔ unknown (low) | — | established (~15y, est. 2011) |
| 19 | Time2drive | 'S-HERTOGENBOSCH | **58.6** | 43.4 ([43.4–71.4], n=44) | ✅ yes (high) | ⏳ wait | established (~20y, est. 2006) |
| 20 | Autorijschool van Grunderbeek | ROSMALEN | **58.5** | 48.1 ([48.1–67.3], n=98) | ❔ unknown (low) | — | established (~18y, est. 2008) |
| 21 | Pieters Rijopleidingen | ROSMALEN | **57.6** | 54.5 ([54.5–84.7], n=31) | ✅ yes (high) | — | established (~15y, est. 2011) |
| 22 | Haarsteegse Autorijschool | HAARSTEEG | **57.2** | 49.7 ([49.7–80.7], n=32) | ❔ unknown (low) | — | established (~40y, est. 1986) |
| 23 | Verkeersschool Vlaspoel | ROSMALEN | **55.5** | 47.2 ([47.2–74.8], n=44) | ❌ no (low) | — | established (~15y, est. 2011) |
| 24 | Rijschool De Draak | ROSMALEN | **54.9** | 57.0 ([57.0–87.2], n=29) | ❔ unknown (low) | — | establishing (~3y, est. 2023) |
| 25 | J.M. van Eijk | 'S-HERTOGENBOSCH | **54.6** | 46.6 ([46.6–68.6], n=74) | ❔ unknown (low) | — | established (~51y, est. 1975) |
| 26 | Rijschool Danny van den Bergh | ROSMALEN | **54.3** | 46.6 ([46.6–65.0], n=109) | ❔ unknown (low) | — | established (~15y, est. 2011) |
| 27 | Autorijschool Boone | BERLICUM | **52.8** | 48.9 ([48.9–78.3], n=37) | ❔ unknown (low) | ⏳ wait | established (~15y, est. 2011) |
| 28 | Rijles Mera | 'S-HERTOGENBOSCH | **52.6** | 51.3 ([51.3–76.6], n=51) | ❌ no (med) | — | established (~7y, est. 2019) |
| 29 | Rob Moggre | ROSMALEN | **51.6** | 50.1 ([50.1–74.3], n=58) | ❔ unknown (low) | — | established (~12y, est. 2014) |
| 30 | Anton Snelrijles | 'S-HERTOGENBOSCH | **51.4** | 51.4 ([51.4–81.0], n=35) | ❔ unknown (low) | — | established (~12y, est. 2014) |

## 6. What changed vs the raw CBR ranking

- **Raw CBR #1 Rijschool Asro** (92% on n=30) is **❔ unknown (low)** for English and `availability=open` — it leaves your usable set entirely.
- **Top English + automatic pick: Autorijschool Amir** — decision 72.2, reliability 58.1, reviews ●●● strong · sent 95, n=79, raw CBR rank 17.
- **English coverage across all 121 schools:** yes=14, likely=7, no=19, unknown=81 — only **21** usable without a phone call, of which **13** also clear the n ≥ 25 sample gate.

## 7. Limitations & how to tune

- **No per-school year-by-year history exists publicly** — CBR shows only the current rolling window. The Wilson interval is the substitute, not historical trend data.
- `english = unknown` means *no online evidence either way* — **not** "no English". Call them (section 3).
- **† Avail (claimed)** is self-reported (the school's own site, aggregators, or reviews) and is **not** weighted in the score by default — it routinely contradicts reality (Asro shows *"geen wachtlijst"* yet has a long wait). Treat it as a question to ask on the phone, not a fact.
- Founding years are estimates; `kvk_number` lets you confirm a finalist at kvk.nl.
- **Re-weight freely:** edit `WEIGHTS` / `MIN_N` in `scripts/enrich.py` and re-run `enrich.py` then `make_report.py`. Section 1 shows how sensitive the order is to the choice.
