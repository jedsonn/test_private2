---
name: nlp-classification-pipeline
description: >
  Build a production-grade LLM-based text classifier with full referee-defensible validation.
  Trigger phrases: "classify these 10-Ks for tone," "code this corpus for [construct]," "I need
  an NLP measure of X," "build a classifier for our earnings-call transcripts," "respond to the
  referee who said our text measure is not validated." Ships construct definition, prompt,
  batch script, human gold set, all 10 LLM_VALIDATION_KIT items, a RoBERTa fallback spec, and a
  1-page measure-validity memo. Use whenever a paper's contribution depends on a custom text
  measure that a referee will attack.
---

# NLP Classification Pipeline

## Purpose

Turn a fuzzy construct ("uncertainty," "litigation risk language," "forward-looking tone") into a
shipped, defensible measure. The pipeline is engineered so that, when a reviewer writes "how do
we know this LLM is measuring what you claim?", the answer is one PDF: the validity memo
generated in Phase 7, backed by the artifacts from Phases 1 through 6.

Every output of this skill must conform to `SHARED_INFRASTRUCTURE.md §7 LLM_VALIDATION_KIT`. The
ten items in that kit are not negotiable. If a phase cannot produce one of them, the skill halts
and reports which item is blocked.

## When to Use

1. The paper introduces or relies on a custom text-based measure of a latent construct.
2. A referee, AE, or coauthor has questioned whether the measure tracks the construct.
3. The corpus is large enough that human coding alone is infeasible (≥ 5,000 docs).
4. A robustness check requires re-coding with a different model or prompt.
5. Replacing a dictionary-based measure (e.g., LM uncertainty) with a context-aware classifier.

## When NOT to Use

1. The construct is already well-measured by a public dictionary and the marginal gain is small.
2. The corpus is < 1,000 docs. Code by hand. Two RAs, one weekend.
3. The user wants topic modeling (unsupervised). Use a topic-modeling skill, not this.
4. The construct is numerical extraction (e.g., "pull out the revenue number"). That is information
   extraction, not classification. Use a regex + LLM-verify pipeline instead.
5. The labels are not mutually exclusive AND the user has not specified multi-label evaluation.
   Stop and resolve the label schema before continuing.

## Prerequisites

1. A corpus path (directory of `.txt` or `.json` files, or a parquet with a `text` column).
2. An Anthropic API key in `$ANTHROPIC_API_KEY`. (See SHARED_INFRASTRUCTURE §1 banned constructions
   when writing any memo this skill produces.)
3. Budget cap stated in USD. Skill aborts if projected cost exceeds cap by > 10%.
4. At least one coauthor or RA willing to human-code 500 docs (≥ 2 humans, for kappa ceiling).
5. A target accuracy threshold and a kappa floor (defaults: F1 ≥ 0.80, kappa ≥ 0.70).

---

## Workflow

### Phase 1 — Construct Definition Workshop

**WHAT.** Convert the user's plain-English construct into a `CONSTRUCT.md` artifact that humans
and the LLM can both follow without ambiguity.

**HOW.**
1. Ask the user for the one-sentence definition. Do not invent it.
2. Ask for 5 positive exemplars (passages that clearly instantiate the construct).
3. Ask for 5 negative exemplars (passages that are close but do not instantiate it).
4. Ask for 5 hard cases (genuinely ambiguous passages where two experts could disagree).
5. Force a tie-break rule for each hard case ("if X is present but Y is absent, code as ___").
6. Write `CONSTRUCT.md` using the template below. Refuse to ship Phase 2 if any of the 15
   exemplars are missing.

**PRODUCE.** `CONSTRUCT.md` with sections: definition, scope, positive list, negative list, hard
list with tie-breaks, version, date, author.

**CHECK.** Read the file back to the user and ask: "are positives 3 and 5 actually positives, or
borderline?" Force a yes/no commit before continuing.

---

### Phase 2 — Prompt Design

**WHAT.** Produce a structured prompt that returns strictly-typed JSON with `label`, `confidence`
(0.0–1.0), and `evidence_quote` (verbatim span from the input that drove the label).

**HOW.**
1. Use a system/user split. System block holds the construct definition and rules. User block
   holds the document.
2. Include 3 of the 5 hard cases as few-shot examples (NOT the positives or negatives — they are
   too easy and waste tokens).
3. Force JSON output via the prompt and via the SDK's `tool_use` JSON-schema mode if available.
4. Set temperature = 0 for the production run. Set temperature = 0.7 ONLY for the prompt
   robustness re-run in Phase 5.
5. Cap input tokens. For 10-K MD&A, truncate at 8,000 tokens. Document the truncation rule in
   `CONSTRUCT.md`.
6. Reserve the other 2 hard cases for a "did the prompt actually learn" sanity check.

**PRODUCE.** `prompt_v1.txt` plus `prompt_meta.json` (model, temperature, max_tokens, truncation
rule, hash of prompt text).

**CHECK.** Run the prompt on the 2 held-out hard cases. If both come back wrong, return to
Phase 1 — the construct is underspecified.

---

### Phase 3 — Human-Coded Gold Set

**WHAT.** A 500-doc gold set, stratified by inferred class, double-coded by two humans.

**HOW.**
1. Run the LLM on a 5,000-doc sample first to estimate base rates.
2. Stratify: aim for ≈ 250 model-positive and ≈ 250 model-negative in the gold set. If base rate
   is < 10%, oversample positives 50/50 (with documented sampling weights for back-out).
3. Build a coding interface — either a Google Sheet with one doc per row, or a local Streamlit
   app. Show ONLY the doc and the construct definition. Hide the LLM label until both humans
   have committed.
4. Two humans (Jedson + RA, or two RAs) code independently. No discussion until both finish 100
   docs, then adjudicate.
5. Compute kappa between the two humans BEFORE comparing to the LLM. That kappa is the human
   ceiling.
6. For docs where humans disagreed, have a third human (or Jedson) adjudicate and record both
   the original codes and the adjudicated label.

**PRODUCE.** `gold_set.csv` with columns: `doc_id`, `human1_label`, `human1_confidence`,
`human2_label`, `human2_confidence`, `adjudicated_label`, `sampling_weight`, `coder_notes`.

**CHECK.** Human-human kappa must be ≥ 0.65. If lower, the construct is too fuzzy. Return to
Phase 1.

---

### Phase 4 — Batch Run

**WHAT.** A parallelized, cached, rate-limited, provenance-logged script that runs the prompt
across the full corpus.

**HOW.**
1. Use the Python template below (≥ 40 lines, production-shape).
2. Cache responses keyed by `(prompt_hash, doc_hash, model_version)`. If a row is already in the
   cache, skip the API call. Caching is non-negotiable. Without it, robustness re-runs cost 4×.
3. Use exponential backoff for `429` and `529` errors. Cap retries at 6.
4. Concurrency: start with 8 parallel workers. Tune upward only if the API tier allows.
5. Log every call to `runs/{run_id}/calls.jsonl`. One JSON object per call: `doc_id`, `prompt_hash`,
   `model`, `temperature`, `request_tokens`, `response_tokens`, `latency_ms`, `attempt`,
   `error`, `label`, `confidence`, `evidence_quote`.
6. After the run, write `runs/{run_id}/manifest.json` with: run start/end, total docs, total
   tokens in/out, total cost, mean confidence, label distribution.

**PRODUCE.** `runs/{run_id}/labels.parquet` (one row per doc) and `runs/{run_id}/manifest.json`.

**CHECK.** Spot-check 20 random rows by re-running them with the same prompt. Hash equality on
output is the test.

---

### Phase 5 — Validation Kit

**WHAT.** Produce all 10 items of `SHARED_INFRASTRUCTURE.md §7 LLM_VALIDATION_KIT` as a single
`VALIDATION.md`. This is the artifact that referees will read.

**HOW.**
1. **Item 1 — Confusion matrix.** Use `sklearn.metrics.confusion_matrix(adjudicated, model)`
   on the 500-doc gold set. Render as a 2×2 (or k×k) ASCII table AND save as PNG.
2. **Item 2 — Kappa.** Compute three kappas: human1-vs-human2, model-vs-human1, model-vs-human2.
   Report all three. Use Cohen's kappa for two-class; quadratic-weighted kappa for ordinal.
3. **Item 3 — Precision, recall, F1 per class.** `sklearn.metrics.classification_report` with
   `digits=3`.
4. **Item 4 — False positives.** Pull 50 docs where model=positive, human=negative. Read all 50.
   Cluster failure modes into ≤ 5 categories (e.g., "metaphorical use," "hypothetical / 'if'
   construction," "denied / negated"). Report counts.
5. **Item 5 — False negatives.** Same, the other direction.
6. **Item 6 — Prompt provenance.** SHA-256 of the prompt text, exact model string (e.g.,
   `claude-opus-4-7[1m]`), temperature, max_tokens, date in ISO-8601.
7. **Item 7 — Prompt-perturbation robustness.** Write 3 prompt variants: (a) reorder the few-shot
   examples, (b) paraphrase the construct definition, (c) tighten the tie-break rule. Re-run on
   the same 200 docs. Report pairwise agreement rates.
8. **Item 8 — Model-version robustness.** Re-run the same 200 docs with one other frontier model
   (GPT-4.1, Gemini 2.5 Pro, or another Claude family member). Report agreement.
9. **Item 9 — Class balance disclosure.** Base rate in the raw corpus (estimated from the 5,000
   sample) AND in the human-coded set (after stratification). Report sampling weights so the
   reader can back out unweighted base rates.
10. **Item 10 — Temporal stability.** If the corpus spans years, split off one year, re-run, and
    re-validate against a small (100-doc) gold set from that year. Report kappa drift.

**PRODUCE.** `VALIDATION.md` with all 10 sections in order. Plus the supporting CSVs and PNGs.

**CHECK.** The skill refuses to ship Phase 6 if any of items 1–10 are missing or marked TODO.

---

### Phase 6 — RoBERTa Fallback

**WHAT.** A fine-tuning spec for a RoBERTa-base classifier on the same gold set, in case the LLM
is too expensive at scale or its kappa misses the floor.

**HOW.**
1. Train/dev/test split of the gold set: 70/15/15, stratified by adjudicated label.
2. Tokenizer: `roberta-base`. Max length 512. Truncation: head-tail (first 256 + last 256 tokens).
3. Training config: 5 epochs, batch size 16, learning rate 2e-5, weight decay 0.01, warmup 10%,
   early stopping on dev F1 with patience 2.
4. Hardware: a single A100 or a Colab Pro session is sufficient for ≤ 5,000 gold docs.
5. Compare RoBERTa to LLM on the test split. If RoBERTa F1 is within 0.03 of the LLM AND inference
   is ≥ 100× cheaper, use RoBERTa for the full corpus and keep the LLM run for headline results.
6. Re-run Items 1–5 of Phase 5 for RoBERTa.

**PRODUCE.** `roberta_spec.md`, `roberta_train.py`, `roberta_results.md`.

**CHECK.** Cost-per-million-docs estimate must be in the spec. If RoBERTa loses by > 0.05 F1,
do not switch — disclose both and use the LLM.

---

### Phase 7 — Reviewer-Rebuttal Memo

**WHAT.** A 1-page memo titled "Why this measure is valid" that survives a hostile second-round
referee. This is the artifact you paste into the response letter (see RESPONSE_LETTER_STYLE).

**HOW.**
1. Lead with the answer (HOUSE_VOICE §1). One sentence: "The measure tracks [construct] with
   kappa = [X] against a 500-doc double-coded human gold set, and is robust to prompt
   perturbations (mean pairwise agreement = [Y]) and to model version (agreement = [Z])."
2. Three short paragraphs:
   - Construct definition + gold-set construction.
   - Headline metrics. Quote specific numbers (F1, kappa, N).
   - Robustness. Quote the three perturbation agreements and the cross-model agreement.
3. Closing paragraph: limitations. Name them. Do not hide them.
4. Hard cap: 1 page, 12pt Times New Roman, 1-inch margins.

**PRODUCE.** `measure_validity_memo.md` and `measure_validity_memo.docx`.

**CHECK.** Re-read it as a hostile reviewer. If the memo does not name (a) the kappa, (b) the
N of the gold set, (c) at least one limitation, redraft.

---

## Templates

### `CONSTRUCT.md`

```markdown
# Construct: {{CONSTRUCT_NAME}}

**Version:** {{VERSION}}
**Date:** {{YYYY-MM-DD}}
**Author:** {{AUTHOR}}

## One-sentence definition

{{ONE_SENTENCE_DEFINITION}}

## Scope

- **Unit of analysis:** {{e.g., sentence, paragraph, 10-K MD&A section, full transcript}}
- **Time window:** {{e.g., 2010–2024}}
- **Corpus source:** {{e.g., EDGAR 10-K MD&A, S&P Capital IQ transcripts}}
- **Truncation rule:** {{e.g., first 8,000 tokens, no exceptions}}

## Positive exemplars

1. **{{DOC_ID_1}}** — "{{VERBATIM_QUOTE}}" — why it counts: {{ONE_LINE_RATIONALE}}
2. **{{DOC_ID_2}}** — "..." — {{...}}
3. **{{DOC_ID_3}}** — "..." — {{...}}
4. **{{DOC_ID_4}}** — "..." — {{...}}
5. **{{DOC_ID_5}}** — "..." — {{...}}

## Negative exemplars (close but not the construct)

1. **{{DOC_ID_1}}** — "..." — why it does NOT count: {{ONE_LINE_RATIONALE}}
2. {{...}}
3. {{...}}
4. {{...}}
5. {{...}}

## Hard cases with tie-break rules

1. **{{DOC_ID_1}}** — "..." — tie-break: if {{CONDITION_A}} then POSITIVE, else NEGATIVE.
2. {{...}}
3. {{...}}
4. {{...}}
5. {{...}}

## Coder-disagreement adjudication policy

{{Who breaks ties? What is the time budget per disagreement?}}
```

### LLM Prompt (system + user)

```text
[SYSTEM]
You are an expert in {{DOMAIN}} text annotation. You will read one document and decide whether
it instantiates the construct defined below.

CONSTRUCT: {{ONE_SENTENCE_DEFINITION}}

SCOPE: {{SCOPE_BULLETS}}

RULES:
1. Use only the text provided. Do not use outside knowledge about the firm, date, or event.
2. If the construct appears anywhere in the document, label POSITIVE.
3. If the construct appears only as a denied or negated possibility, label NEGATIVE.
4. If the construct appears only in a hypothetical or "if X then Y" construction, label NEGATIVE
   unless the document also affirms X.
5. Return strict JSON: {"label": "POSITIVE" | "NEGATIVE", "confidence": <float 0-1>,
   "evidence_quote": "<verbatim span from the input, ≤ 50 words>"}.
6. The evidence_quote must be a literal substring of the input. No paraphrase.

EXAMPLES (hard cases):

INPUT: "{{HARD_CASE_1_TEXT}}"
OUTPUT: {"label": "{{LABEL_1}}", "confidence": {{CONF_1}}, "evidence_quote": "{{QUOTE_1}}"}

INPUT: "{{HARD_CASE_2_TEXT}}"
OUTPUT: {"label": "{{LABEL_2}}", "confidence": {{CONF_2}}, "evidence_quote": "{{QUOTE_2}}"}

INPUT: "{{HARD_CASE_3_TEXT}}"
OUTPUT: {"label": "{{LABEL_3}}", "confidence": {{CONF_3}}, "evidence_quote": "{{QUOTE_3}}"}

[USER]
Document ID: {{DOC_ID}}

Text:
{{DOC_TEXT}}
```

### Python Batch Script (`batch_classify.py`)

```python
import os, json, hashlib, time, pathlib, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import anthropic
import pandas as pd

MODEL = "claude-opus-4-7[1m]"
TEMPERATURE = 0.0
MAX_TOKENS = 400
CONCURRENCY = 8
MAX_RETRIES = 6
RUN_ID = time.strftime("%Y%m%d-%H%M%S")
RUN_DIR = pathlib.Path(f"runs/{RUN_ID}")
RUN_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = pathlib.Path("cache"); CACHE_DIR.mkdir(exist_ok=True)

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

with open("prompt_v1.txt") as f:
    PROMPT_TEXT = f.read()
PROMPT_HASH = hashlib.sha256(PROMPT_TEXT.encode()).hexdigest()[:16]
SYSTEM_BLOCK, USER_TEMPLATE = PROMPT_TEXT.split("[USER]", 1)
SYSTEM_BLOCK = SYSTEM_BLOCK.replace("[SYSTEM]", "").strip()

def doc_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]

def cache_key(doc_id: str, text: str) -> pathlib.Path:
    return CACHE_DIR / f"{PROMPT_HASH}_{MODEL}_{doc_hash(text)}.json"

def classify_one(row):
    doc_id, text = row["doc_id"], row["text"]
    ck = cache_key(doc_id, text)
    if ck.exists():
        return {"doc_id": doc_id, **json.loads(ck.read_text()), "cached": True}
    user_msg = USER_TEMPLATE.replace("{{DOC_ID}}", str(doc_id)).replace("{{DOC_TEXT}}", text[:32000])
    for attempt in range(MAX_RETRIES):
        try:
            t0 = time.time()
            resp = client.messages.create(
                model=MODEL, max_tokens=MAX_TOKENS, temperature=TEMPERATURE,
                system=SYSTEM_BLOCK, messages=[{"role": "user", "content": user_msg}],
            )
            latency_ms = int((time.time() - t0) * 1000)
            out = json.loads(resp.content[0].text)
            out.update({"latency_ms": latency_ms, "attempt": attempt, "model": MODEL,
                        "prompt_hash": PROMPT_HASH})
            ck.write_text(json.dumps(out))
            return {"doc_id": doc_id, **out, "cached": False}
        except (anthropic.RateLimitError, anthropic.APIStatusError) as e:
            time.sleep(min(2 ** attempt, 30))
        except Exception as e:
            return {"doc_id": doc_id, "error": str(e), "attempt": attempt}
    return {"doc_id": doc_id, "error": "max_retries", "attempt": MAX_RETRIES}

corpus = pd.read_parquet(sys.argv[1])
results, calls_path = [], RUN_DIR / "calls.jsonl"
with open(calls_path, "w") as fout, ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
    futures = {ex.submit(classify_one, r): r["doc_id"] for _, r in corpus.iterrows()}
    for fut in as_completed(futures):
        r = fut.result()
        fout.write(json.dumps(r) + "\n"); fout.flush()
        results.append(r)

pd.DataFrame(results).to_parquet(RUN_DIR / "labels.parquet")
manifest = {"run_id": RUN_ID, "model": MODEL, "prompt_hash": PROMPT_HASH,
            "n_docs": len(corpus), "n_errors": sum(1 for r in results if "error" in r)}
(RUN_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"Done. Run dir: {RUN_DIR}")
```

### `VALIDATION.md`

```markdown
# Validation kit — {{CONSTRUCT_NAME}}

**Run ID:** {{RUN_ID}}
**Model:** {{MODEL}}
**Prompt hash:** {{PROMPT_HASH}}
**Date:** {{YYYY-MM-DD}}

## 1. Confusion matrix (N = {{N_GOLD}})

```
                pred_pos  pred_neg
true_pos          {{TP}}      {{FN}}
true_neg          {{FP}}      {{TN}}
```

## 2. Cohen's kappa
- Human1 vs Human2: **{{K_HH}}** (ceiling)
- Model vs Human1:  **{{K_MH1}}**
- Model vs Human2:  **{{K_MH2}}**

## 3. Precision / Recall / F1 (per class)
| Class    | Precision | Recall | F1     | Support |
|----------|-----------|--------|--------|---------|
| POSITIVE | {{P_P}}   | {{R_P}}| {{F_P}}| {{S_P}} |
| NEGATIVE | {{P_N}}   | {{R_N}}| {{F_N}}| {{S_N}} |

## 4. False positives (sample of 50)
| Failure mode                          | Count |
|---------------------------------------|-------|
| {{MODE_1}}                            | {{N1}}|
| {{MODE_2}}                            | {{N2}}|
| {{MODE_3}}                            | {{N3}}|

## 5. False negatives (sample of 50)
| Failure mode                          | Count |
| ... | ... |

## 6. Prompt provenance
SHA-256: {{PROMPT_HASH_FULL}}
Model: {{MODEL}} | T = {{TEMP}} | max_tokens = {{MAX_TOKENS}}

## 7. Prompt-perturbation robustness (N = 200)
| Variant | Agreement with v1 |
|---------|-------------------|
| Reorder few-shot | {{A_R}} |
| Paraphrase definition | {{A_P}} |
| Tighten tie-break | {{A_T}} |

## 8. Model-version robustness (N = 200)
Agreement vs {{OTHER_MODEL}}: **{{A_X}}**

## 9. Class balance
- Raw corpus base rate: {{BR_RAW}}
- Gold set base rate: {{BR_GOLD}}
- Sampling weights: in `gold_set.csv`, column `sampling_weight`

## 10. Temporal stability
Held-out year: {{YEAR}} | Kappa on year-specific gold set: **{{K_YEAR}}**
```

---

## Examples

### Worked example: "Uncertainty in 10-K MD&A"

**`CONSTRUCT.md` (first 20 lines):**

```markdown
# Construct: MD&A Uncertainty (forward-looking)

**Version:** 1.0
**Date:** 2026-06-23
**Author:** Jedson Pinto

## One-sentence definition

A sentence in the MD&A is labeled POSITIVE if management expresses genuine uncertainty
about a future operating, financial, or strategic outcome — not boilerplate risk-factor
language and not historical uncertainty that has since been resolved.

## Scope

- **Unit of analysis:** sentence within the MD&A section of a 10-K.
- **Time window:** 2003–2024 (post-Sarbanes-Oxley).
- **Corpus source:** EDGAR 10-K filings parsed to MD&A.
- **Truncation rule:** if MD&A > 8,000 tokens, classify first 8,000 only and log truncation flag.

## Positive exemplars

1. **0001-AAPL-2019** — "We are unable to predict the duration or ultimate impact of these
```

**Sample classification (Doc 0042-XOM-2017):**

```json
{
  "doc_id": "0042-XOM-2017-MDA-s14",
  "label": "POSITIVE",
  "confidence": 0.91,
  "evidence_quote": "the timing and amount of any future impairment cannot be reasonably
  estimated given commodity price volatility",
  "latency_ms": 1342,
  "attempt": 0,
  "model": "claude-opus-4-7[1m]",
  "prompt_hash": "a3f9e1b2c4d5e6f7"
}
```

**Sample classification (Doc 0107-PG-2014, hard negative):**

```json
{
  "doc_id": "0107-PG-2014-MDA-s03",
  "label": "NEGATIVE",
  "confidence": 0.84,
  "evidence_quote": "while the macroeconomic environment remains challenging, we expect
  continued progress",
  "latency_ms": 1109,
  "attempt": 0,
  "model": "claude-opus-4-7[1m]",
  "prompt_hash": "a3f9e1b2c4d5e6f7"
}
```

**Confusion matrix on 500-doc gold set:**

```
                pred_pos  pred_neg
true_pos          218        32
true_neg          27         223
```

Precision (pos) = 0.889; Recall (pos) = 0.872; F1 (pos) = 0.880.
Kappa (model vs adjudicated human) = 0.776. Kappa (human1 vs human2) = 0.812.

---

## Edge Cases & Failure Modes

| # | Scenario | Behavior |
|---|---|---|
| 1 | Doc exceeds truncation cap | Classify head-only; set `truncated=true` in output; flag for manual spot-check at validation. |
| 2 | Model returns malformed JSON | Retry once with `temperature=0` and a "return JSON only" reminder; if still malformed, log as error and exclude from headline metrics. |
| 3 | Evidence quote not a substring of input | Mark as suspect; do NOT auto-correct; surface in false-positive analysis. |
| 4 | Human-human kappa < 0.65 | Halt. Construct is too fuzzy. Return to Phase 1, do not proceed. |
| 5 | Base rate < 5% | Switch to oversample-positives stratification; record weights; do not present unweighted accuracy. |
| 6 | Cross-model agreement < 0.70 | Disclose loudly in the memo. Do not hide. Add a robustness column in the paper. |
| 7 | Corpus spans > 10 years and temporal kappa drifts > 0.10 | Either restrict the sample or train a year-aware classifier; never present a stable-coefficient result. |
| 8 | RoBERTa beats LLM by > 0.05 F1 | Use RoBERTa for the full corpus; keep LLM as the robustness check; flip the framing in the memo. |
| 9 | API hits a hard outage mid-run | The cache means restart is safe. Resume the same `RUN_ID`; manifest will reconcile. |
| 10 | Coauthor objects to the construct definition after Phase 3 | Re-do Phase 1. Never patch Phase 1 without re-doing Phases 2 and 3. The skill refuses partial patches. |

---

## Hard Rules

1. NEVER ship a measure without all 10 LLM_VALIDATION_KIT items. The skill halts.
2. NEVER report unweighted metrics when the gold set is stratified. Always disclose weights.
3. NEVER omit the human-human kappa. It is the ceiling and the reviewer will ask for it.
4. NEVER paraphrase the reviewer's reviewer-rebuttal-relevant numbers; quote them in full.
5. NEVER set temperature > 0 for the production run. Robustness re-runs may use higher T.
6. NEVER cache across model-version changes. The cache key includes the model string.
7. NEVER hand-edit the gold set after the LLM has been run on it. That is contamination.
8. NEVER drop the limitations paragraph from the validity memo. Every measure has limits.
9. NEVER skip the false-positive and false-negative narrative analysis. Numbers alone are weak.
10. ALWAYS log the prompt hash, model string, and date in every artifact this skill produces.
11. ALWAYS produce both the LLM result and the RoBERTa fallback before declaring done.
12. ALWAYS apply HOUSE_VOICE (SHARED §1) to the validity memo.

---

## Quality Checklist

1. `CONSTRUCT.md` exists and contains 5+5+5 exemplars with tie-breaks.
2. Prompt JSON contract is enforced and tested on the 2 held-out hard cases.
3. Gold set has 500 docs, double-coded, with adjudicated labels and sampling weights.
4. Human-human kappa ≥ 0.65 reported.
5. Model-vs-human kappa ≥ floor reported, with both raters.
6. Confusion matrix is in both ASCII and PNG form.
7. False-positive narrative and false-negative narrative are written, not just counted.
8. Prompt-perturbation results on 3 variants, with agreement metrics.
9. Cross-model agreement metric on 200 docs, with named other model.
10. Temporal-stability check across at least one held-out year.
11. RoBERTa fallback trained and compared, with cost-per-million estimate.
12. Validity memo is 1 page, names kappa, N, and at least one limitation.
13. All artifacts are reproducible from a single `make all` or `bash run.sh`.
14. Cache and `manifest.json` allow a cold-start replay.

---

## ROI Estimate

| Activity | Manual hours | With skill | Savings |
|---|---|---|---|
| Construct definition workshop | 8 | 2 | 6h |
| Prompt design + iteration | 12 | 3 | 9h |
| Gold-set coding setup | 6 | 1 | 5h |
| Batch run engineering | 16 | 1 | 15h |
| Validation kit assembly | 20 | 2 | 18h |
| RoBERTa fallback | 24 | 4 | 20h |
| Validity memo for referees | 6 | 1 | 5h |
| **Total per construct** | **92h** | **14h** | **78h (~85%)** |

Annual: 4–6 constructs × 78h = 312–468h saved. Risk reduction (a referee-killed paper costs
~200h of rework) compounds further.
