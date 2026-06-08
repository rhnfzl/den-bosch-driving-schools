#!/usr/bin/env python3
"""Independent OpenAI sentiment pass over the review quotes gathered by the
Tavily review-reader workflow.

Two-model design: Claude agents gather the verbatim review quotes and judge
authenticity; OpenAI scores the *sentiment* of those quotes (a second model, so
neither one's bias dominates the "how is this school" read).

Reads:  research/reviews/school_<NNN>.json   (must contain representative_quotes)
Writes: research/sentiment/school_<NNN>.json

Stdlib only (urllib) — no openai package needed. Idempotent: skips schools that
already have a sentiment file. Reads the API key from $OPENAI_API_KEY (or a .env
file path in $SENTIMENT_ENV_FILE) -- no key or personal path is hardcoded.
"""
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REVIEWS = os.path.join(ROOT, "research", "reviews")
OUT = os.path.join(ROOT, "research", "sentiment")
MODEL = os.environ.get("SENTIMENT_MODEL", "gpt-5.4-mini")  # newest mini; SENTIMENT_MODEL=gpt-5.4-nano for cheaper
ENDPOINT = "https://api.openai.com/v1/chat/completions"

SYSTEM = (
    "You are a careful, skeptical sentiment analyst for Dutch driving schools. "
    "You are given verbatim customer review quotes (Dutch and/or English). Judge the "
    "OVERALL sentiment of these reviews about the school as a place to learn to drive, "
    "from the TEXT only — ignore any star numbers. Weigh substantive, specific reviews "
    "more than generic one-liners. Be balanced: do not inflate toward positive."
)

INSTR = (
    "Return ONLY a JSON object with keys:\n"
    '  "sentiment_index": integer 0-100 (0 very negative, 50 neutral/mixed, 100 very positive),\n'
    '  "sentiment": one of "very_negative","negative","mixed","positive","very_positive",\n'
    '  "themes_positive": array of short strings (what students praise),\n'
    '  "themes_negative": array of short strings (complaints; [] if none),\n'
    '  "confidence": one of "high","medium","low" (low if few/short quotes),\n'
    '  "rationale": one short sentence grounded in the quotes.\n'
    "With few or very short quotes, set confidence \"low\"."
    "  (The zero-quote case is handled in code and never reaches you.)"
)


def api_key():
    """OpenAI key from $OPENAI_API_KEY, or a .env file path in $SENTIMENT_ENV_FILE.
    Nothing is hardcoded."""
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key
    env_file = os.environ.get("SENTIMENT_ENV_FILE")
    if env_file and os.path.exists(env_file):
        m = re.search(r"OPENAI_API_KEY=(\S+)", open(env_file, encoding="utf-8").read())
        if m:
            return m.group(1)
    sys.exit("Set OPENAI_API_KEY in the environment, or SENTIMENT_ENV_FILE=/path/to/.env")


def _build_body(quotes):
    user = INSTR + "\n\nREVIEW QUOTES:\n" + "\n".join(f"- {q}" for q in quotes[:12])
    body = {
        "model": MODEL,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
    }
    if MODEL.startswith("gpt-5"):
        # Reasoning models reject `temperature` and need `max_completion_tokens` with
        # enough headroom past the (hidden) reasoning tokens — too small => empty content.
        body["max_completion_tokens"] = 2000
        body["reasoning_effort"] = "low"   # sentiment is simple; keep it fast + cheap
    else:
        body["temperature"] = 0
        body["max_tokens"] = 400
    return body


def score(quotes, key):
    body = json.dumps(_build_body(quotes)).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    last = None
    for attempt in range(4):
        try:
            resp = json.load(urllib.request.urlopen(req, timeout=90))
            content = resp["choices"][0]["message"]["content"]
            if not content.strip():
                raise ValueError("empty content from model")   # reasoning-budget exhaustion
            return json.loads(content)
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:   # connection / DNS / timeout before response
            last = e
            if attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            last = e
            if attempt < 3:
                time.sleep(1)
                continue
            raise
    raise last or RuntimeError("sentiment request failed")


def main():
    key = api_key()
    files = sorted(glob.glob(os.path.join(REVIEWS, "school_*.json")))
    done = skipped = scored = errors = 0
    for fp in files:
        slug = os.path.basename(fp).replace(".json", "")
        out_fp = os.path.join(OUT, f"{slug}.json")
        if os.path.exists(out_fp):
            skipped += 1
            continue
        try:
            rv = json.load(open(fp, encoding="utf-8"))
        except json.JSONDecodeError:
            errors += 1
            continue
        quotes = [q for q in (rv.get("representative_quotes") or []) if str(q).strip()]
        rec = {"row_index": rv.get("row_index"), "slug": slug, "rijschool": rv.get("rijschool"),
               "model": MODEL, "n_quotes": len(quotes)}
        if not quotes:
            rec.update({"sentiment_index": None, "sentiment": "insufficient",
                        "themes_positive": [], "themes_negative": [], "confidence": "low",
                        "rationale": "no review quotes available"})
        else:
            try:
                res = score(quotes, key)
                rec.update({
                    "sentiment_index": res.get("sentiment_index"),
                    "sentiment": res.get("sentiment"),
                    "themes_positive": res.get("themes_positive", []),
                    "themes_negative": res.get("themes_negative", []),
                    "confidence": res.get("confidence", "medium"),
                    "rationale": res.get("rationale", ""),
                })
                scored += 1
            except Exception as e:  # noqa: BLE001 — log and continue, don't lose the batch
                errors += 1
                print(f"  ! {slug}: {type(e).__name__} {e}")
                continue
        json.dump(rec, open(out_fp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        done += 1
    print(f"sentiment: wrote {done} (scored {scored} via {MODEL}, {done - scored} no-quotes), "
          f"skipped {skipped} existing, {errors} errors")


if __name__ == "__main__":
    main()
