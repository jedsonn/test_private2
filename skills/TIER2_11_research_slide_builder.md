---
name: research-slide-builder
description: >
  Use when the user needs a conference, seminar, brown-bag, or job-talk slide deck built from an existing paper draft.
  Trigger phrases: "build slides for my paper," "make a 45-minute deck," "I'm presenting at AAA next week,"
  "turn this paper into slides," "I have a job talk in two weeks." Produces a slide-by-slide outline with
  speaker notes, three candidate hooks, scripted talking points per result slide, and a Q&A prep card with
  ten anticipated questions. Follows the user's house deck structure (hook, setting, data, identification,
  main result, mechanism, external validity, implications) with slide budgets allocated by slot length
  (20, 45, 60, or 90 minutes). Honors HOUSE_VOICE (SHARED_INFRASTRUCTURE.md §1).
---

# Research Slide Builder

## Purpose

Take a finished or near-finished paper draft and a venue slot length, and return a production-ready slide outline that the user can hand to a designer or paste straight into Keynote/Beamer. The outline includes per-slide content notes, a 60-word speaker script per result slide, three candidate hooks ranked by fit, and ten anticipated Q&A items with two-sentence answers.

The output is not slides themselves. It is a structured outline and speaker plan that any reasonable presenter can execute. The user maintains aesthetic control. Claude does the structural and rhetorical work.

## When to Use

1. The user has a draft paper (working draft or submitted) and a known venue and slot length.
2. The user names a specific slot: 20 minutes (concurrent session), 45 minutes (seminar), 60 minutes (extended seminar), or 90 minutes (job talk).
3. The user wants the outline before they start designing in Keynote / PowerPoint / Beamer.
4. The user is rebuilding a deck after a major revision and the old outline is stale.
5. The user is prepping a job talk and needs Q&A practice questions in addition to slides.

## When NOT to Use

1. The user does NOT have a draft yet. Use the writing skills first. A slide deck cannot be built from a one-paragraph idea.
2. The user has a slot length outside the supported set (20 / 45 / 60 / 90). Ask which bucket to round to before proceeding.
3. The user wants slide visual design (colors, fonts, layout). This skill produces structure and speaker plan, not graphic design.
4. The user wants poster format. Posters follow a different structure; this skill is for talk decks.
5. The user wants a teaching deck (lecture). Use a teaching skill, not this one.

## Prerequisites

1. Paper draft (PDF, .tex, or .docx) accessible to Claude.
2. Slot length explicitly stated: 20, 45, 60, or 90 minutes.
3. Venue type confirmed: concurrent / seminar / job-talk. Job-talk gets extra mechanism and pipeline slides.
4. List of the paper's main tables and figures (at minimum: which table holds the main result, which holds the mechanism, which holds the heterogeneity).
5. Audience composition note ("mostly accounting," "mostly finance," "mixed acct+fin," "general business"). Affects hook choice.

---

## Workflow

### Phase 1 — Load paper and compute slide budget

1. Read the paper. Locate the seven structural anchors: hook material, institutional setting, data section, identification section, main results table, mechanism section, robustness section.
2. Confirm the slot length. If missing, ask. Do not guess.
3. Compute the slide budget from `SLIDE_BUDGET_TABLE`:

```
SLIDE_BUDGET_TABLE
+-----------+-------+---------+------+--------+----------+----------+-----------+-------+
| Slot (min)| Total | Hook    | Stng | Data   | Ident.   | Result   | Mech+EV   | Impl. |
+-----------+-------+---------+------+--------+----------+----------+-----------+-------+
| 20        | 12    | 1       | 1    | 1      | 1        | 3        | 3         | 2     |
| 45        | 22    | 2       | 2    | 2      | 2        | 5        | 6         | 3     |
| 60        | 28    | 2       | 3    | 2      | 3        | 6        | 8         | 4     |
| 90 (job)  | 38    | 2       | 4    | 3      | 4        | 8        | 12        | 5     |
+-----------+-------+---------+------+--------+----------+----------+-----------+-------+
```

4. Confirm that the identification phase has at least one dedicated slide. The identification slide is non-optional in this user's house style.
5. Record the budget. Every later phase must respect it.

### Phase 2 — Slide-by-slide outline

1. For each slide in the budget, produce a row in `SLIDE_OUTLINE_SCHEMA`:

```
SLIDE_OUTLINE_SCHEMA
+-----+---------------+--------------------------+----------------------------------+
| #   | Section       | Title                    | Content note (one sentence)      |
+-----+---------------+--------------------------+----------------------------------+
| 01  | Hook          | {{TITLE}}                | {{ONE-LINE CONTENT}}             |
| ... | ...           | ...                      | ...                              |
+-----+---------------+--------------------------+----------------------------------+
```

2. Title rule. Every title is a complete declarative sentence stating the slide's punchline ("Auditor changes spike 38% after the rule," not "Auditor changes after the rule"). The audience should be able to skim titles only and reconstruct the argument.
3. Content note rule. One sentence describing what goes on the slide. If the slide is a chart, name the variable on each axis. If the slide is a table, name the columns being shown.
4. Identification slide must include the specific design name (staggered DiD, 2x2 DiD, sharp RDD, fuzzy RDD, IV, matching, synthetic control). Vague "we use a quasi-experiment" titles are forbidden.
5. Do not stack two tables on one slide. Tables get their own slide. Figures may share a slide only if they are panels of the same figure.

### Phase 3 — Hook design

1. Produce three candidate hooks using the templates in `HOOK_TEMPLATES`. One anecdote-led, one number-led, one puzzle-led.
2. For each, write the slide title and the speaker script (≤ 60 words).
3. Rank them by fit to the audience composition note from Prerequisites step 5. Accounting-heavy audiences prefer number-led; finance-heavy audiences prefer puzzle-led; general business audiences prefer anecdote-led. State the ranking and the reasoning.
4. Mark the recommended pick. The user can override.

### Phase 4 — Result slide speaker scripts

1. For every slide tagged "Result" in the outline, write the speaker script in ≤ 60 words.
2. Script structure: (a) name what the audience is looking at in one sentence, (b) state the punchline number with a specific identifier, (c) state what the next slide will do.
3. Script rule. Every script quotes a specific identifier ("Column 2, β = 0.187, t = 4.2, N = 14,832"). Vague references ("the main coefficient") are banned per HOUSE_VOICE.
4. Script must read aloud in 25–30 seconds at normal pace. Time it.
5. Skip filler ("As you can see," "Importantly," "Of note"). These are HOUSE_VOICE-banned anyway.

### Phase 5 — Q&A prep

1. Produce ten anticipated questions using `QA_PREP_CARD`. Questions must be specific to this paper, not generic.
2. Distribute the ten across categories: 3 identification, 2 data/sample, 2 mechanism, 2 external validity, 1 implications. If the design is RDD, swap one identification slot for bandwidth/functional-form.
3. For each, write a two-sentence answer. First sentence concedes or reframes; second sentence delivers the substantive response with a specific table or test reference.
4. Mark the three hardest with `[HOT]`. These are the ones the user should rehearse out loud.
5. Cross-check against IDENTIFICATION_THREAT_LIBRARY (SHARED_INFRASTRUCTURE.md §6). Every design-appropriate threat must appear as at least one anticipated question.

---

## Templates

### HOOK_TEMPLATES (three styles)

**Anecdote-led**

```
Slide title: {{ONE-SENTENCE SCENE THAT IMPLIES THE PUZZLE}}.
Speaker script (≤ 60 words):
"In {{YEAR}}, {{NAMED ACTOR}} did {{SPECIFIC ACT}}. The market reaction was {{SPECIFIC NUMBER}}.
What's surprising is that {{REASON THIS IS WEIRD}}. That puzzle is what this paper is about.
By the end of the talk I'll have shown you {{ONE-SENTENCE PUNCHLINE}}."
```

**Number-led**

```
Slide title: {{HEADLINE STAT AS A SENTENCE}}.
Speaker script (≤ 60 words):
"{{HEADLINE STAT}}. That number comes from {{DATA SOURCE}}, covering {{YEAR RANGE}} and
{{N OBSERVATIONS}}. The standard story would predict {{CONTRARY PREDICTION}}, and the gap
between those is what this paper explains. I'll show you {{ONE-SENTENCE PUNCHLINE}}."
```

**Puzzle-led**

```
Slide title: {{QUESTION AS A SENTENCE, ENDING IN A PERIOD NOT A QUESTION MARK}}.
Speaker script (≤ 60 words):
"Consider two firms. Firm A {{CONDITION A}}; Firm B {{CONDITION B}}. The textbook says they
should behave the same way on {{OUTCOME}}. They don't. The wedge is {{SPECIFIC NUMBER}}.
Today I'll show you {{ONE-SENTENCE PUNCHLINE}} explaining the wedge."
```

### SLIDE_OUTLINE_ROW

```
+-----+----------+----------------------------------+----------------------------------+
| #   | Section  | Title                            | Content note                     |
+-----+----------+----------------------------------+----------------------------------+
| 14  | Result   | Treatment raises restatements    | Table 3, Col 2. Coefficient on   |
|     |          | by 38% over three years.         | Treat x Post = 0.38, t = 4.2.    |
+-----+----------+----------------------------------+----------------------------------+
```

### SPEAKER_SCRIPT (per result slide)

```
Slide {{NN}} — {{TITLE}}
[Show: {{TABLE OR FIGURE REFERENCE}}]
Script (≤ 60 words):
"{{ONE SENTENCE: WHAT THEY ARE LOOKING AT}}.
{{ONE SENTENCE: PUNCHLINE WITH SPECIFIC IDENTIFIER}}.
{{ONE SENTENCE: WHAT'S NEXT}}."

Transition cue: "{{NEXT SLIDE TITLE}}."
```

### QA_PREP_CARD

```
Q{{NN}} [{{CATEGORY}}] {{HOT?}}
Question: {{VERBATIM ANTICIPATED QUESTION}}
Answer (2 sentences):
1. {{CONCEDE OR REFRAME}}.
2. {{SUBSTANTIVE RESPONSE WITH SPECIFIC TABLE / TEST REFERENCE}}.
```

### DECK_MANIFEST

```
Deck manifest — {{PAPER SHORT NAME}} — {{VENUE}} — {{SLOT MIN}}
- Total slides: {{NN}}
- Hook style chosen: {{anecdote / number / puzzle}}
- Result slides with scripts: {{NN}} / {{NN}}
- Q&A items: {{NN}} of which {{NN}} marked HOT
- Identification slide present: yes / no
- Build owner: Jedson
- Rehearsal target date: {{YYYY-MM-DD}}
```

---

## Examples

### Example 1 — A 45-minute deck for a stylized staggered-DiD paper

Paper short name: `AUDIT_RULE`. Hypothesis: a 2014 PCAOB rule change caused auditor turnover to spike. Design: staggered DiD using PCAOB inspection waves as the treatment timing instrument. Audience: mixed accounting + finance seminar.

**Slide budget (45 min): 22 slides total.**

Outline (abbreviated; full version would list all 22 rows):

```
+-----+----------------+-------------------------------------------+-------------------------+
| #   | Section        | Title                                     | Content note            |
+-----+----------------+-------------------------------------------+-------------------------+
| 01  | Hook           | Auditor turnover jumped 38% after 2014.   | Headline stat slide.    |
| 02  | Hook           | Standard models predict no change.        | Theory contrast slide.  |
| 03  | Setting        | The 2014 PCAOB rule, in one paragraph.    | Quote the rule text.    |
| 04  | Setting        | Inspection waves staggered 2014–2018.     | Timeline figure.        |
| 05  | Data           | Audit Analytics + Compustat, 2010–2020.   | Sample funnel.          |
| 06  | Data           | Final sample: 14,832 firm-years, 2,118 f. | Descriptives table.     |
| 07  | Identification | Staggered DiD with C–S estimator.         | Design statement.       |
| 08  | Identification | Pre-trends flat (F = 0.31, p = 0.94).     | Event-study figure.     |
| 09  | Result         | Treatment raises turnover by 38%.         | Table 3, Col 2.         |
| 10  | Result         | Effect concentrates in years +1 and +2.   | Event-study coefficient.|
| 11  | Result         | Robust to TWFE, C–S, S–A estimators.      | Table 4, all panels.    |
| 12  | Result         | No effect on Big 4 to Big 4 transitions.  | Heterogeneity table.    |
| 13  | Result         | Effect doubles for high-risk inspections. | Heterogeneity figure.   |
| 14  | Mechanism      | Channel 1: inspection findings disclosed. | Mechanism table A.      |
| 15  | Mechanism      | Channel 2: client-side cost recalc.       | Mechanism table B.      |
| 16  | Mechanism      | Channel 3 (ruled out): fee renegotiation. | Null result table.      |
| 17  | Mechanism      | Channel ranking: 1 > 2 > 3.               | Decomposition figure.   |
| 18  | Mechanism      | Implication for theory of audit demand.   | Theory tie-back slide.  |
| 19  | Mechanism      | Implication for SEC oversight model.      | Policy tie-back slide.  |
| 20  | Implications   | Two follow-up papers in this pipeline.    | Pipeline slide.         |
| 21  | Implications   | Open questions we cannot answer here.     | Caveats slide.          |
| 22  | Implications   | Thank-you slide with one-line summary.    | Standard close.         |
+-----+----------------+-------------------------------------------+-------------------------+
```

**Hook chosen.** Mixed audience leans toward number-led. Recommended hook:

```
Slide 01 — "Auditor turnover jumped 38% after 2014."
Script (54 words):
"Auditor turnover among US public firms jumped 38% in the three years after the 2014 PCAOB
rule change. That number comes from Audit Analytics, 2010 to 2020, 14,832 firm-years. The
standard model of audit demand predicts no shift. Today I'll show you that PCAOB inspection
disclosures are the mechanism behind the gap."
```

**Sample result slide script.**

```
Slide 09 — "Treatment raises turnover by 38%."
[Show: Table 3, Column 2]
Script (52 words):
"You're looking at the main DiD specification with firm and year fixed effects, clustered
at the auditor level. The coefficient on Treat x Post is 0.38, t = 4.2, N = 14,832. That's a
38% increase relative to the pre-period base rate of 8%. Next I'll show the event-study form."

Transition cue: "Effect concentrates in years +1 and +2."
```

**Sample Q&A item.**

```
Q03 [identification] [HOT]
Question: "How do you know this isn't just SOX-related churn that happens to be timed near 2014?"
Answer:
1. We can separate the two because PCAOB inspection waves stagger across 2014–2018, while SOX
   is a single 2002 shock.
2. The placebo test in Table 6, Panel C, restricts to firms with no SOX exposure changes; the
   coefficient is 0.36 (t = 3.9), essentially unchanged from the full-sample 0.38.
```

---

## Edge Cases & Failure Modes

| # | Edge case | Failure mode | Required handling |
|---|---|---|---|
| 1 | Paper has no clear identification strategy | Outline would be missing the mandatory ID slide | Halt. Ask the user to specify the design before building slides. |
| 2 | Slot length is 30 minutes (not in standard set) | Budget table has no row | Ask whether to round to 20 or 45. Default rounds down to 20. |
| 3 | Paper has two main hypotheses with separate results | Result phase too crowded | Split the result section into H1 and H2; reduce mechanism slides by the difference. |
| 4 | Job talk request for paper that's still draft 1 | Q&A prep will lack robustness ammunition | Flag in the manifest; recommend the user lock in robustness checks before talk. |
| 5 | Audience composition note missing | Hook ranking cannot resolve | Ask. Do not guess based on venue name. |
| 6 | User submits two papers and asks for combined deck | This skill is single-paper | Refuse. Offer to build two separate decks and a 5-slide bridge. |
| 7 | Paper has no robustness section | External-validity slides have nothing to fill | Flag. Replace those slots with limitations + future-work slides. |
| 8 | RDD paper, but user did not pre-register bandwidth | Q&A will have a deadly question we cannot answer | Mark Q&A item as [HOT BUT UNANSWERED] and tell the user to choose a defensible response. |
| 9 | Speaker scripts exceed 60 words | Violates time budget | Reject and re-cut. Hard rule, not a suggestion. |
| 10 | User wants Beamer code | Out of scope | Refuse. This skill produces an outline; Beamer code is a separate generation task. |

---

## Hard Rules

1. Every deck has exactly one or more slide tagged "Identification." Zero identification slides is a failure.
2. Every slide title is a declarative sentence stating the punchline, not a topic label.
3. Every speaker script is ≤ 60 words. Count words; do not eyeball.
4. Every result-slide script quotes a specific identifier (table number, column, coefficient, t-stat, N).
5. Three hooks must be produced, ranked, and recommended. Not one. Not two.
6. Q&A items count is exactly ten. Three marked [HOT].
7. Slide budget per phase comes from `SLIDE_BUDGET_TABLE`. Do not freelance.
8. HOUSE_VOICE applies. No em dashes. No "However" sentence starts. No "delve" / "leverage" / "navigate."
9. No vague "main result" references. Always quote the table and column.
10. Hooks never end with a question mark. Period instead, even for the puzzle-led version.
11. Tables and figures: at most one of each per slide. Stacking is banned.
12. The closing slide ("thank-you") repeats the one-line punchline. Not a generic "thanks for your time."

---

## Quality Checklist

1. Slide count equals the budget for the chosen slot length, exact.
2. The identification slide names the specific design (staggered DiD, RDD, IV, etc.), not a category.
3. Every slide title is a complete declarative sentence.
4. Three hooks present, one anecdote-led, one number-led, one puzzle-led.
5. Hook ranking matches audience composition rule (number for accounting, puzzle for finance, anecdote for general business).
6. Recommended hook is marked explicitly.
7. Every result slide has a speaker script ≤ 60 words.
8. Every result-slide script cites a specific table/column/coefficient/t-stat/N.
9. Q&A card has exactly 10 items.
10. Q&A categories are distributed: 3 identification, 2 data, 2 mechanism, 2 EV, 1 implications.
11. Exactly 3 Q&A items marked [HOT].
12. IDENTIFICATION_THREAT_LIBRARY threats relevant to this design each appear in Q&A.
13. No HOUSE_VOICE-banned phrases in any artifact.
14. Closing slide repeats the one-line pitch.
15. Manifest produced with build owner (Jedson) and rehearsal target date.

---

## ROI Estimate

Building a job-talk deck outline from scratch takes the user roughly 8 hours of staring at the wall, plus 4 hours of iteration with coauthors. This skill compresses the staring-at-the-wall portion to roughly 30 minutes of review and edits. Net time saved per job-talk deck: 6–7 hours. Across a hiring season with 8 talks, that's roughly 50 hours.

For seminar decks (45 min), the user typically spends 4 hours on outline. This skill compresses that to 20 minutes of review. Net saved: 3.5 hours per seminar deck. The user gives roughly 6 external seminars per year; total saved: 21 hours.

Combined annual ROI in a hiring + seminar year: roughly 70 hours. Combined ROI in a non-hiring year: roughly 21 hours.

Quality gain is separate from time gain. The structural completeness check (every deck has an identification slide, every result slide has a script with a specific identifier) catches the most common mistake the user makes under time pressure, which is shipping a deck with a vague "main result" slide that the discussant then shreds.
