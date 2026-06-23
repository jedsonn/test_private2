# Shared Infrastructure — Voice, Formatting, and Taxonomies

This file is the single source of truth that all 20 skill files reference. When a skill says "follow HOUSE_VOICE" or "apply ACCT_3312_HARD_RULES," look here.

Skills must not redefine these locally. If a rule needs to change, change it here and re-audit all skills.

---

## 1. HOUSE_VOICE — Universal Writing Rules

Apply to every text artifact Claude produces for this user unless a skill explicitly overrides (e.g., a skill that requires legal language).

### Banned constructions

- NEVER use em dashes (—). Use a period, semicolon, or parenthesis instead.
- NEVER start a sentence with "However," "Moreover," "Furthermore," "Additionally," or "Interestingly."
- NEVER write "It is worth noting that," "It should be mentioned that," "Notably," or "Of note."
- NEVER use "delve," "navigate," "leverage" (as a verb), "in today's fast-paced world," or "in the realm of."
- NEVER hedge with "may potentially," "could possibly," or stacked modals.
- NEVER use "Overall," "In conclusion," "To summarize" as paragraph openers.
- NEVER pad with restatement ("As I mentioned above…").

### Required habits

- ALWAYS prefer active voice. Passive only when the agent is genuinely unknown or irrelevant.
- ALWAYS use numbered lists when the user asks for multiple things, multiple steps, multiple changes, or multiple next steps.
- ALWAYS state percentages of completion when discussing progress.
- ALWAYS name an owner and a target date for every next step.
- ALWAYS quote specific identifiers when referring to results: "Table 3, Column 2, β = 0.187, t = 4.2, N = 14,832." Never "the main result."
- ALWAYS prefer short paragraphs (≤ 4 sentences).
- ALWAYS lead with the answer, then the justification.

### Tone

- Direct, informal in chat ("lil bro," "lets go hard" is in-character for the user but NOT in formal artifacts).
- Formal artifacts (response letters, referee reports, applications) drop the informal voice but keep the directness.

---

## 2. RESPONSE_LETTER_STYLE — Paper Revision Output

Used by: Paper Revision Engine.

### File format

- Word document (.docx) ready for tracked changes.
- Times New Roman, 12pt, single spacing within paragraphs, blank line between paragraphs.
- 1-inch margins on all sides.

### Structure

1. Header block — paper title, manuscript ID, journal, editor name, submission date.
2. Greeting — "Dear Professor [Editor LastName],"
3. Opening paragraph — three sentences max: thank, summarize main changes in one sentence, signal openness to further revision.
4. Editor comments section — each editor comment in a gray comment box, response below.
5. Reviewer sections — Reviewer 1, 2, 3 each with their own header. Each comment in a gray box. Response below each.
6. Closing — one sentence sign-off.

### Visual encoding

- **Gray comment boxes** — `#F2F2F2` background, 1pt black border, italicized reviewer text inside. Width 100% of text frame. Reviewer comment quoted verbatim, no paraphrase.
- **Yellow highlight** — `#FFFF00`, used ONLY for placeholders the user must verify before sending (e.g., specific page numbers, exact coefficient values that may be updated after re-running).
- **Cyan highlight** — `#00FFFF`, used ONLY for classification labels at the start of each response: `[ADDRESSED]`, `[ADDRESSED PARTIALLY]`, `[RESPECTFULLY DISAGREE]`, `[CLARIFICATION]`, `[ALREADY IN PAPER]`.
- **Bold-italic comment titles** — every comment gets a one-line title in **_bold italic_** describing the comment's substance (e.g., **_R1.3 — Concern about parallel trends in the pre-period_**).

### Response template per comment

```
[Gray box]
R1.3: [Verbatim reviewer text.]
[/Gray box]

***R1.3 — Concern about parallel trends in the pre-period***

[CYAN: ADDRESSED]

We thank the reviewer for raising this. We agree that the pre-treatment
parallel-trends assumption is the central identifying assumption and now
provide three pieces of evidence supporting it.

First, [specific evidence with table/figure reference].
Second, [specific evidence].
Third, [specific evidence].

The new evidence appears in **Section 4.2** and **Table 4 (Panel B)**.
The relevant text is reproduced below for the reviewer's convenience:

> [Quoted new manuscript text, indented.]
```

### Hard length cap

- Per-comment response: target 150 words, hard cap 300. Longer responses must be split across sub-points.
- Total response letter: target 12 pages, hard cap 25.

---

## 3. REFEREE_REPORT_STYLE — Review 4.0 Output

Used by: Referee Report Engine.

### Hard rules

- **Zero em dashes.** Replace with periods or semicolons.
- **Short paragraphs.** Max 4 sentences each.
- **Hard word limit.** 1,800 words total. Skills MUST count and refuse to ship over.
- **Score table on page 1.** Before any prose.

### Score table

```
+--------------------------------------+-------+
| Dimension                            | Score |
+--------------------------------------+-------+
| Importance of question               |  /10  |
| Identification / methodology         |  /10  |
| Execution (data, code, tables)       |  /10  |
| Writing & framing                    |  /10  |
| Contribution above existing lit      |  /10  |
+--------------------------------------+-------+
| Overall                              |  /10  |
+--------------------------------------+-------+
| Recommendation: [Reject / R&R Major / R&R Minor / Accept w/ Minor] |
+--------------------------------------+
```

### Sections (in order)

1. Summary of the paper (≤ 200 words).
2. Strengths (3–5 numbered bullets).
3. Major concerns (3–6 numbered bullets, each with a specific suggested action).
4. Minor concerns (numbered list, each ≤ 2 sentences).
5. Typos and notation (line-referenced).

### Closing line

The report ends with: "I hope these comments are useful to the author(s). I am happy to review a revision."

No signature. No name. No date (the editor adds those).

---

## 4. COAUTHOR_EMAIL_STYLE — Update Email Output

Used by: Coauthor Update Email skill.

### Structure (rigid)

```
Subject: [Paper short-name] — update [DATE: YYYY-MM-DD]

Hi [coauthor first names],

Quick update. We're at [PCT]% done on [paper short-name].

What changed since the last update:

1. [Change, with table/section/figure reference]
2. [Change]
3. [Change]

What I'm asking from you (with deadlines):

1. [Coauthor LastName] — [task], by [date].
2. [Coauthor LastName] — [task], by [date].
3. [Coauthor LastName] — [task], by [date].

What I'm doing next (mine to own):

1. [Task], by [date].
2. [Task], by [date].

Risks / open questions:

1. [Risk or question.]

Best,
Jedson
```

### Rules

- ALWAYS state a percentage of completion in the opening line. Use the project's tracked-task ratio if available; otherwise the user's stated estimate.
- ALWAYS number every list. Never bullet.
- ALWAYS name the owner and date for every "asking from you" item. No "we should" or "we need to."
- NEVER exceed 350 words. Skills must count.
- NEVER include a separate "thanks for your work" paragraph. The numbered structure is the respect.

---

## 5. ACCT_3312_HARD_RULES — Case Study Dataset Rules

Used by: ACCT 3312 QA Engine, ACCT 3312 Auto-Grader.

Asserted in the prompt's context block. These are non-negotiable.

1. **Dupes must be catchable with default Excel Remove Duplicates (all cols).** A duplicate row must be identical across every column. No "almost duplicates" with one whitespace difference.
2. **Every aggregation SQL must dedup first.** No `SUM(amount)` or `COUNT(*)` queries that operate on a table with un-deduped rows.
3. **No questions on non-existent data.** Every question must be answerable from the data provided. The QA engine must verify the answer key column-by-column against the dataset.
4. **No bridge-table joins.** Students are business majors, not CS majors. Joins limited to 2 tables max, on a single key, no junction tables.
5. **T6 (Task 6) max 1–2 sub-questions.** T6 is the integration task; it cannot become an arbitrarily large rubric.
6. **Workflow order: merge → helper columns → pivot.** Every case must follow this order. Pivots before helper columns are forbidden.
7. **Hints should be light.** A hint may point to a column or a technique, never give the formula or the answer.
8. **Audience is business students, not CS.** No Python, no scripting, no recursion, no window functions in instructions. Excel + simple SQL only.

### Auto-graded enforcement checks

- Duplicate test: load dataset, run pandas `df.duplicated().sum()` — must match the intended duplicate count exactly.
- Answer-key cross-check: every numeric answer must be reproducible from the released dataset using only Excel + simple SQL.
- Join check: scan the rubric for the words "junction," "bridge," "many-to-many" — any hit is a failure.

---

## 6. IDENTIFICATION_THREAT_LIBRARY — Common ID Threats to Test

Used by: Identification Strategy Critique, Paper Revision Engine, Stata DiD/Event-Study skill, Referee Report Engine.

For every staggered-DiD or event-study design, generate tests against this taxonomy.

| Threat | What to test | Standard test |
|---|---|---|
| Parallel pre-trends | Pre-treatment coefficients on event-study leads | F-test of joint significance on leads = 0 |
| Bad controls | Variables that are post-treatment | List every control + treatment date; flag any control measured post-event |
| Untreated control contamination | Controls also affected by the treatment | Spatial / industry / supplier exposure check |
| Treatment effect heterogeneity | TWFE bias from forbidden comparisons | Callaway–Sant'Anna; Sun–Abraham; de Chaisemartin–D'Haultfœuille |
| Anticipation | Effects begin before official treatment date | Plot t = -3, -2, -1 separately; F-test for anticipation window |
| Sample composition shift | Sample changes across columns | Hold sample fixed; show columns side-by-side |
| Reverse causality | Treatment endogenous to outcome trends | Test predictability of treatment from pre-period outcome growth |
| SUTVA violation | One unit's treatment affects another's outcome | Spatial / network spillover check |
| Selection on observables | Treatment correlated with observed pre-period covariates | Balance table + entropy balancing robustness |
| Bandwidth sensitivity (RDD) | Results sensitive to window choice | Plot β across bandwidths 0.5x–2x of optimal |
| Functional form (RDD) | Polynomial order changes the result | Linear, quadratic, local-linear with optimal BW |
| Multiple hypothesis testing | Many outcomes, inflated false-positive rate | Romano-Wolf or List et al. p-value correction |

---

## 7. LLM_VALIDATION_KIT — Required Outputs for Any NLP Classifier

Used by: NLP Classification Pipeline, Paper Revision Engine (when responding to NLP-method critiques).

Every shipped NLP classifier must produce all of:

1. **Confusion matrix vs. human-coded gold set** (≥ 500 docs, stratified by class).
2. **Cohen's kappa** between model and humans, AND between two humans (to establish ceiling).
3. **Precision, recall, F1** per class.
4. **False-positive analysis** — sample 50 model-positives that humans coded negative. Categorize the failure modes.
5. **False-negative analysis** — same with model-negatives that humans coded positive.
6. **Prompt provenance** — exact prompt text, model version, temperature, date, with hash.
7. **Robustness across prompt perturbations** — re-run on 200 docs with 3 prompt variants; report agreement.
8. **Robustness across model versions** — re-run on 200 docs with one other frontier model; report agreement.
9. **Class balance disclosure** — base rates in raw corpus AND in human-coded set.
10. **Temporal stability** — if the corpus spans years, re-validate on at least one held-out year.

---

## 8. PROJECT_STATE_SCHEMA — Status Memo Format

Used by: Project Resurrection, Coauthor Update Email (for status carry-over).

Every project should have a `STATE.md` of this form:

```markdown
# [Paper short-name] — State as of [YYYY-MM-DD]

## One-line pitch
[The paper in one sentence, written so a non-specialist would understand.]

## Where we are
- Stage: [idea / data-build / estimation / draft / submitted / R&R-round-N / accepted]
- Target venue: [journal]
- Completion: [PCT]%

## Last working session
- Date: [YYYY-MM-DD]
- Touched: [files]
- Last commit / save: [path or hash]

## Open threads (numbered)
1. [Thread, with owner and date]
2. [Thread]

## Things that will go stale
- [Data refresh that ages]
- [Citation that needs updating]
- [Code env that drifts]

## Resume commands
- Stata: [exact do-file path and master switch]
- Python: [venv activate + entry script]
- WRDS: [last query date + table version]
```

---

## 9. APP_AUDIT_RUBRIC — Personal App Review

Used by: App Code Audit.

Audit every personal app (PersonalAssist, Casa Pinto, CertReady, etc.) along five axes. Score each 1–5.

| Axis | What to check |
|---|---|
| Security | Hardcoded secrets, XSS, CSRF, SQL injection, exposed env vars, dependency CVEs |
| Performance | Bundle size, render hot paths, N+1 queries, missing indexes, cold start |
| Correctness | Type coverage, error handling at boundaries (not internal), runtime exceptions in logs |
| UX | Loading states, empty states, error states, keyboard nav, accessibility basics |
| Maintainability | Dead code, duplicated helpers, undocumented invariants, stale comments |

Each axis ≤ 3 means a fix is required. Each axis ≥ 4 means the app is shippable on that axis.

---

## 10. APPLICATION_PACKET_SCHEMA — Fellowship / Job Apps

Used by: Application Engine.

Every external application produces this packet:

1. `01_cover_letter.docx` — venue-tailored, 1 page hard cap.
2. `02_cv.pdf` — refreshed within last 30 days; ordered: appointments → education → publications → working papers → grants → invited talks → service → teaching.
3. `03_research_statement.pdf` — 3–5 pages depending on venue ask. Structure: (a) opening hook ≤ 100 words, (b) agenda of three slices, (c) current paper deep-dive, (d) two-paper pipeline, (e) ten-year vision.
4. `04_teaching_statement.pdf` — 1–2 pages. Structure: philosophy ≤ 1 paragraph, evidence of impact (ratings + 1 concrete redesign story), planned innovations.
5. `05_diversity_statement.pdf` — only if explicitly requested.
6. `06_writing_sample.pdf` — most polished published or near-published paper.
7. `07_reference_list.docx` — three names, with relationship and current contact.
8. `08_packet_manifest.md` — checklist confirming all items present, deadlines, submission URL.
