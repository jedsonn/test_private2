# Discovery Report — Jedson Pinto Skills & Agents Library

## Discovery Basis (Honesty Disclaimer)

The sandbox in which this discovery was performed had **no access** to:

- Dropbox or any cloud-synced folders
- Research project folders (paper drafts, response letters, Stata do-files, Python scripts)
- ACCT 3312 teaching materials (datasets, rubrics, answer keys, SQL files)
- App source trees (PersonalAssist, Casa Pinto, CertReady, ResearchRadar, SSRN Scout, ShockTracker)
- Cowork prompt libraries or scheduled-task configurations
- Administrative folders (tax, property, travel, fellowship)
- Any `CONTEXT.md`, `SKILLS.md`, `TASKS.md`, or equivalent prompt collection

The only file reachable was a 24-byte placeholder (`test_private2/test`).

Per the master prompt's instruction — "Do not hallucinate what might be there. Work with what you can actually see." — this discovery report is **derived exclusively from the CONTEXT ABOUT ME block in the master prompt**, not from scanning actual artifacts. Time-savings estimates are reasoned-from-first-principles given the workflow types described, not measured. Workflow frequencies are best-guess inferences from the seniority and activity profile implied by the context (active researcher with teaching load, multiple coauthored projects, side apps).

Where a workflow is named explicitly in the prompt's context block, it is treated as **asserted**. Where a workflow is inferred from common academic-life patterns, it is flagged as **inferred**.

---

## 1. Folder Map (Asserted vs. Inferred)

```
[ASSERTED — named in the prompt's context block]
~/Dropbox/                                  (location unknown — not reachable here)
├── Research/
│   ├── [Multiple paper projects]
│   │   ├── Drafts (Word, LaTeX)
│   │   ├── Response letters
│   │   ├── Stata do-files
│   │   ├── Python NLP scripts
│   │   ├── Data + results folders
│   │   └── Coauthor correspondence
│   └── Lit review / Idea docs / PDFs
├── Teaching/
│   └── ACCT 3312/
│       ├── Case study files (SQL, Excel, datasets)
│       ├── Answer keys + rubrics
│       ├── Auto-grader code
│       ├── Syllabi + Azure SQL info
│       └── MOS Excel Expert (MO-211) materials
├── Apps/
│   ├── PersonalAssist/            (React/Vite/TypeScript)
│   ├── Casa Pinto/                (HTML/CSS/JS)
│   ├── CertReady/                 (C#/.NET)
│   ├── ResearchRadar/             (prompt-based)
│   ├── SSRN Scout/                (prompt-based)
│   └── ShockTracker/              (prompt-based)
├── Cowork/
│   ├── Prompts/                   (.md files)
│   └── Scheduled tasks/
└── Admin/
    ├── Tax docs + property records
    ├── Travel + reimbursement
    ├── Fellowship / job apps
    └── Conference submissions + slides
```

---

## 2. Workflow Inventory

Each row is one identifiable workflow. Frequencies are estimated for an active accounting/finance academic with teaching load.

| # | Workflow | Frequency | Time/Occurrence | Automation Potential | Stakes |
|---|---|---|---|---|---|
| 1 | Revise paper in response to reviewer comments | 6–10×/yr | 30–60 hrs | High | Career-critical |
| 2 | Write referee report on submission | 8–15×/yr | 4–8 hrs | High | Reputation |
| 3 | Update coauthors after a work session | Weekly during active project | 30–60 min | High | Project velocity |
| 4 | Design ACCT 3312 case study + dataset | 6–10×/semester | 6–12 hrs | High | Student outcomes |
| 5 | Grade ACCT 3312 case submissions | Weekly in-semester | 4–10 hrs/batch | High | Student outcomes |
| 6 | Build Stata estimation file (DiD/event study) | 3–6×/yr per project | 4–8 hrs | High | Identification rigor |
| 7 | Build/validate LLM classification pipeline | 2–4×/yr per project | 10–30 hrs | High | Construct validity |
| 8 | Scan literature for new relevant papers | Weekly | 1–2 hrs | High | Research currency |
| 9 | Submit paper to a conference | 4–8×/yr | 2–4 hrs | Medium | Pipeline visibility |
| 10 | Triage editor decision letter and plan response | 4–8×/yr | 1–3 hrs | High | Strategic choice |
| 11 | Build slide deck for a research talk | 6–12×/yr | 8–16 hrs | Medium | Reputation |
| 12 | Spec a WRDS data pull and translate to SQL/Stata | 4–10×/yr | 1–4 hrs | High | Replicability |
| 13 | Critique an identification strategy (own or others') | Weekly | 30 min – 2 hrs | High | Rigor |
| 14 | Triage student inbox and draft replies | Daily in-semester | 30–60 min | High | Student support |
| 15 | Assemble fellowship / job market application | 1–5×/yr | 10–40 hrs | High | Career |
| 16 | Organize annual tax documents | 1×/yr | 6–10 hrs | High | Money + compliance |
| 17 | Package reimbursement after a trip | 6–15×/yr | 30–60 min | High | Money |
| 18 | Resurrect a stale paper after months away | 3–6×/yr | 4–8 hrs | High | Pipeline recovery |
| 19 | Audit / extend a personal app (PersonalAssist etc.) | Episodic | 4–20 hrs | Medium | Productivity |
| 20 | Track regulatory shocks for ID variation | Continuous | Hours/wk if manual | High | Pipeline of papers |

All twenty are asserted by — or directly inferable from — the prompt's context block. Frequencies are inferred.

---

## 3. Template Inventory

Pulled directly from "My Document Formatting Preferences" in the context block:

| Template | Specification | Used By |
|---|---|---|
| Response letter style | Times New Roman 12pt; gray comment boxes (#F2F2F2); yellow placeholders; cyan classification labels; bold-italic comment titles | Paper Revision Engine |
| Referee report style | Zero em dashes; short paragraphs; hard word limit; score table with recommendation | Referee Report Engine |
| Coauthor email | Numbered change summaries; numbered next-step assignments with named owners; percentage done; deadline | Coauthor Update |
| Academic prose | Active voice; no "it is worth noting that"; no "interestingly"; minimize hedging | All writing skills |
| ACCT 3312 dataset rules | 8 hard rules (dedup-clean, dedup-before-agg, no-phantom-data, no-bridge-joins, T6 ≤ 2 sub-Qs, workflow order, light hints, business-student audience) | ACCT 3312 QA + Auto-Grader |

These are externalized to `SHARED_INFRASTRUCTURE.md` so every skill cross-references one source of truth.

---

## 4. Pain Points (Inferred from Communication Style + Asserted Preferences)

1. **Filler and padding.** Claude over-generates, hedges, pads with "it is worth noting." Skills must produce surgical output with hard length caps.
2. **Vague next steps.** "Improve the analysis" is rejected. Every actionable output must specify table/column/variable, exact numeric target, deadline, and owner.
3. **Format drift.** Response letters, referee reports, and coauthor emails each have a distinct house style. Mixing them is a failure mode.
4. **Context loss.** Returning to a paper after weeks away costs hours of re-loading. Project Resurrection skill addresses this.
5. **Identification rigor in haste.** DiD/event study code written under deadline pressure ships with avoidable mistakes (untreated control contamination, parallel trends untested, sample composition shifting across columns).
6. **Construct validity in NLP.** LLM classifiers shipped without confusion matrices vs. human coders or false-positive analysis. Reviewers will demand this; better to ship it.
7. **Teaching dataset bugs.** Students filing "the question can't be answered with this data" tickets — the 8 dataset rules exist precisely to prevent these.
8. **Reimbursement / tax friction.** Receipts scattered across email, paper, photo roll. Low-stakes individually, high cumulative drag.
9. **Application overhead.** Tailoring a CV + research statement + teaching statement + cover letter for each fellowship/job is mechanical at the format level but stakes are career-shaping.
10. **Regulatory-shock harvesting.** New rules drop, ID-quality variation opens for ~3–18 months, then everyone piles in. Need a tracker.

---

## 5. Top 25 Candidate Skills (Ranked by frequency × time_saved × stakes)

| Rank | Candidate | One-line | ROI Logic | Status |
|---|---|---|---|---|
| 1 | Paper Revision Engine | Reviewer comments → response letter + tracked-change plan | 6–10×/yr × 30 hrs × career-critical | **BUILD T1-01** |
| 2 | Referee Report Engine (Review 4.0) | Submission → scored referee report with score table | 8–15×/yr × 6 hrs × reputation | **BUILD T1-02** |
| 3 | Coauthor Update Email | Session output → numbered email with %done + owned next steps | 40+×/yr × 45 min × velocity | **BUILD T1-03** |
| 4 | ACCT 3312 Case Study QA Engine | Dataset + Qs → 8-rule audit + fix list | 6–10×/semester × 4 hrs × student outcomes | **BUILD T1-04** |
| 5 | ACCT 3312 Auto-Grader | Submission batch → graded with rubric-mapped feedback | Weekly × 6 hrs × student outcomes | **BUILD T1-05** |
| 6 | Stata DiD/Event-Study Helper | Spec → estimation file using CS/SA + parallel-trends + robustness | 3–6×/project × 6 hrs × rigor | **BUILD T1-06** |
| 7 | NLP Classification Pipeline | Construct + corpus → LLM/RoBERTa classifier + validation kit | 2–4×/project × 20 hrs × validity | **BUILD T1-07** |
| 8 | Literature Triage (ResearchRadar) | Weekly scan → ranked relevance + 3-line summaries | Weekly × 90 min × currency | **BUILD T1-08** |
| 9 | Conference Submission Packager | Paper + venue → tailored cover letter + abstract + metadata | 4–8×/yr × 3 hrs × visibility | **BUILD T2-09** |
| 10 | Editor Decision Letter Triage | Decision letter → strategic recommendation + effort estimate | 4–8×/yr × 2 hrs × strategy | **BUILD T2-10** |
| 11 | Research Slide Deck Builder | Paper → 35-slide talk deck following house structure | 6–12×/yr × 12 hrs × reputation | **BUILD T2-11** |
| 12 | WRDS Query Spec → SQL/Stata | Plain-English data ask → executable query + sample-construction memo | 4–10×/yr × 2.5 hrs × replicability | **BUILD T2-12** |
| 13 | Identification Strategy Critique | Draft ID strategy → adversarial review with named threats + tests | Weekly × 90 min × rigor | **BUILD T2-13** |
| 14 | Student Inbox Triage | Email batch → categorized replies + escalation list | Daily in-sem × 45 min × support | **BUILD T2-14** |
| 15 | Application Engine (Fellowship/Job) | Job + CV + bio → tailored CV + research stmt + teach stmt + cover | 1–5×/yr × 25 hrs × career | **BUILD T2-15** |
| 16 | Tax Document Organizer | Receipt + statement dump → IRS-ready folder + summary | 1×/yr × 8 hrs × $ | **BUILD T3-16** |
| 17 | Travel & Reimbursement Packager | Trip → reimbursement packet + per-diem calc + email | 6–15×/yr × 45 min × $ | **BUILD T3-17** |
| 18 | Project Resurrection | Stale project folder → 1-page status memo + 5-task restart plan | 3–6×/yr × 6 hrs × pipeline | **BUILD T3-18** |
| 19 | App Code Audit | App repo → security/perf/UX issues + prioritized fix list | Episodic × 12 hrs × productivity | **BUILD T3-19** |
| 20 | Regulatory Shock Tracker | Reg landscape → calendar of shocks + ID-quality scoring | Continuous × hrs/wk × pipeline | **BUILD T3-20** |
| 21 | Reading Group Prep | Paper → 1-page summary + 5 discussion questions | Weekly × 60 min × low | Cut — covered by Lit Triage |
| 22 | PhD Student Advising Log | Meeting → memo + next steps + deadline tracker | Weekly × 30 min × medium | Cut — covered by Coauthor Update |
| 23 | Personal Finance Dashboard Update | Statements → net-worth + spending update | Monthly × 60 min × medium | Cut — out of skill-library scope |
| 24 | Personal Calendar Optimizer | Cal + commitments → weekly plan | Weekly × 30 min × medium | Cut — too generic for an LLM skill |
| 25 | Casa Pinto Household Operations | Vendor + repair tracking | Monthly × 60 min × low | Cut — better as the app itself |

**Cuts (21–25):** Three are subsumed by stronger skills, two are out of the skill-library frame (better served by tools they already have).

---

## 6. Final 20 — Confirmed List

### Tier 1 — Weekly Use / Career-Critical (8)

1. `TIER1_01_paper_revision_engine.md`
2. `TIER1_02_referee_report_engine.md`
3. `TIER1_03_coauthor_update_email.md`
4. `TIER1_04_acct3312_qa_engine.md`
5. `TIER1_05_acct3312_autograder.md`
6. `TIER1_06_stata_did_event_study.md`
7. `TIER1_07_nlp_classification_pipeline.md`
8. `TIER1_08_literature_triage.md`

### Tier 2 — Weekly-to-Monthly (7)

9. `TIER2_09_conference_packager.md`
10. `TIER2_10_decision_letter_triage.md`
11. `TIER2_11_research_slide_builder.md`
12. `TIER2_12_wrds_query_spec.md`
13. `TIER2_13_identification_critique.md`
14. `TIER2_14_student_inbox_triage.md`
15. `TIER2_15_application_engine.md`

### Tier 3 — Monthly-to-Episodic (5)

16. `TIER3_16_tax_organizer.md`
17. `TIER3_17_reimbursement_packager.md`
18. `TIER3_18_project_resurrection.md`
19. `TIER3_19_app_code_audit.md`
20. `TIER3_20_regulatory_shock_tracker.md`

Plus:

- `SHARED_INFRASTRUCTURE.md` — formatting taxonomies, voice rules, ACCT 3312 hard rules, ID-strategy threat library
- `MASTER_INDEX.md` — directory + load instructions
