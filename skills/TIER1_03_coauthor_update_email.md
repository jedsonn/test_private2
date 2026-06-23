---
name: coauthor-update-email
description: >
  Produces a numbered, deadline-tagged coauthor update email from a session
  summary and the project STATE.md. Activates on any of: "email my coauthors,"
  "write the coauthor update," "send the weekly update to [name]," "draft an
  R&R-progress email," "ping the coauthors on [paper short-name]," "status
  email," "update [coauthor first names] on where we are," "tell the team where
  we are on [paper]," and any time the user asks for an outbound message to
  collaborators about a working paper. Err on the side of activating whenever
  the user is preparing an email aimed at coauthors about academic-paper
  progress.
---

# Coauthor Update Email Engine

## Purpose
Convert a working session's deltas plus a project's STATE.md into a tight, numbered, deadline-tagged update email that respects coauthor attention and forces accountability on every ask. The email is in COAUTHOR_EMAIL_STYLE (SHARED_INFRASTRUCTURE.md §4) and obeys HOUSE_VOICE (§1). Output is paste-ready into Gmail.

## When to Use
- User says: "Email my coauthors on [paper]."
- User says: "Write the weekly update for [paper short-name]."
- User says: "Tell [coauthor first name] where we are on [paper]."
- User says: "Send the R&R status to the team."
- User says: "Ping the coauthors with what changed today."
- User says: "Draft the coauthor email."
- User says: "Status email."
- User says: "Update the team on [paper]."
- User just finished a working session and a STATE.md exists.

## When NOT to Use
- Outbound to editors, referees, or program officers (use Paper Revision Engine or Application Engine).
- Internal note-to-self or scratchpad updates (use Project State / Resurrection skill).
- A reply to an existing coauthor thread that has its own structure (do not impose this template on top of a thread already in motion).
- Non-paper projects (apps, teaching, ACCT 3312) — wrong template, wrong tone.

## Prerequisites
- A session summary (the user gives this in chat, or you have it from the current session).
- The project's `STATE.md` following PROJECT_STATE_SCHEMA (SHARED_INFRASTRUCTURE.md §8). Must include `Stage`, `Completion`, `Open threads`.
- Coauthor list with first and last names (read from STATE.md header or ask once).
- Today's date (use current session date).

---

## Workflow

### Phase 1 — Compute completion percentage
**WHAT:** Recompute the headline `PCT` from closed-vs-open tasks in `STATE.md`.
**HOW:**
1. Open `STATE.md`. Read the `## Open threads` list.
2. Count `N_open` = unchecked items. Count `N_closed_in_session` = items the user closed in this session.
3. If a `## Closed threads` archive exists, read `N_closed_total`. Otherwise treat the prior `Completion` line as the baseline and add `N_closed_in_session / (N_open + N_closed_in_session)` of remaining ground.
4. If the user gives a manual override ("we're at 70%"), use the manual number but state the source bluntly.
**PRODUCE:** Single integer `PCT` in `[0, 100]`.
**CHECK:** `PCT` must be greater than or equal to the prior `STATE.md` `Completion` value unless a thread re-opened (note that in the Risks block).

### Phase 2 — Bucket session changes
**WHAT:** Reduce the session diff to 1-line bullets ordered by importance to coauthors.
**HOW:**
1. List every deliverable touched: tables, figures, sections, code, data builds, referee responses.
2. Apply the coauthor-importance ordering:
   1. Headline result changes (new column in main table, new sample, new identification check).
   2. New tables or figures.
   3. New robustness or appendix material.
   4. Writing improvements (intro, framing, abstract).
   5. Plumbing (file moves, version bumps, code refactors). Drop unless a coauthor needs to act on them.
3. Compress each into one line, with a specific identifier (`Table 3`, `Figure 2`, `Section 4.2`, `Appendix A`, `do-file 04_event_study.do`).
**PRODUCE:** Numbered list, 3 to 6 items. Never more than 6.
**CHECK:** No bullet is longer than 20 words. Every bullet names a specific manuscript or code artifact.

### Phase 3 — Identify coauthor-action items
**WHAT:** Extract every task the user cannot do alone and assign each to a named coauthor with a date.
**HOW:**
1. Scan the session and the `Open threads` list for any item flagged as needing coauthor input: theory derivations, data access only one coauthor has (e.g., WRDS subscription, Compustat extract), domain reads (institutional context, prior literature in coauthor's wheelhouse), Stata code only a coauthor has written, signoff on framing.
2. Match each item to a specific coauthor LastName using STATE.md's "owner" annotations. If no owner is annotated, infer from prior `STATE.md` entries or ask once.
3. Assign a date: default is 7 calendar days from today for "read and react," 14 days for "produce material," 21 days for "rewrite a section." If the project has an R&R deadline within 30 days, compress to half these intervals.
**PRODUCE:** Numbered list of 1 to 4 ask items. Each item is `[Coauthor LastName] — [task], by [YYYY-MM-DD].`
**CHECK:** Every ask has an owner. Every ask has a date. No "we should" or "we need to."

### Phase 4 — Write the email
**WHAT:** Fill the COAUTHOR_EMAIL_STYLE (§4) template exactly.
**HOW:**
1. Subject line: `Subject: [Paper short-name] — update [YYYY-MM-DD]`.
2. Greeting: `Hi [coauthor first names],` comma-separated, Oxford-comma style.
3. Opening sentence is fixed: `Quick update. We're at [PCT]% done on [paper short-name].`
4. Insert Phase 2 numbered list under `What changed since the last update:`.
5. Insert Phase 3 numbered list under `What I'm asking from you (with deadlines):`.
6. Add 1 to 3 self-owned items under `What I'm doing next (mine to own):` with dates.
7. Add 0 to 2 risks/questions under `Risks / open questions:`.
8. Sign off with `Best,\nJedson`.

### Phase 5 — Length audit
**WHAT:** Enforce the 350-word cap.
**HOW:**
1. Word-count the body from `Hi` through `Jedson`. Subject and signature counted.
2. If above 350, compress in this order: (a) drop Risks; (b) trim self-owned next steps to top 2; (c) merge two Phase 2 bullets if they touch the same section; (d) drop the lowest-importance Phase 2 bullet.
3. Never trim the asks list to make the cap. The asks are the point of the email.
**CHECK:** Final word count ≤ 350. State the final count in a comment line above the draft for the user.

### Phase 6 — Ask-item verification
**WHAT:** Confirm every "asking from you" item has a named owner and a real ISO date.
**HOW:**
1. Regex the asks list for the pattern `^[0-9]+\. [A-Z][a-z]+( [A-Z][a-z]+)? — .+, by [0-9]{4}-[0-9]{2}-[0-9]{2}\.$`.
2. Any line that fails the regex is rewritten until it passes.
3. Dates: confirm each date is a real future date and not a weekend (shift to next Monday if it lands on Sat/Sun).
**CHECK:** Regex passes on every line.

---

## Templates

### Email scaffold (exact)
```
Subject: {{PAPER_SHORTNAME}} — update {{TODAY_ISO}}

Hi {{COAUTHOR_FIRST_NAMES_CSV}},

Quick update. We're at {{PCT}}% done on {{PAPER_SHORTNAME}}.

What changed since the last update:

1. {{CHANGE_1_WITH_ARTIFACT_REF}}
2. {{CHANGE_2_WITH_ARTIFACT_REF}}
3. {{CHANGE_3_WITH_ARTIFACT_REF}}

What I'm asking from you (with deadlines):

1. {{COAUTHOR_LASTNAME_A}} — {{TASK_A}}, by {{DATE_A_ISO}}.
2. {{COAUTHOR_LASTNAME_B}} — {{TASK_B}}, by {{DATE_B_ISO}}.

What I'm doing next (mine to own):

1. {{SELF_TASK_1}}, by {{SELF_DATE_1_ISO}}.
2. {{SELF_TASK_2}}, by {{SELF_DATE_2_ISO}}.

Risks / open questions:

1. {{RISK_OR_QUESTION_1}}

Best,
Jedson
```

### Pre-flight comment block (above the draft, for the user only)
```
# Word count: {{WC}} / 350
# Coauthors addressed: {{COAUTHOR_LIST}}
# Asks regex check: PASS
# Pulled from STATE.md as of: {{STATE_LAST_MODIFIED}}
```

### Subject-line alternates (only if main subject is ambiguous)
- `Subject: {{PAPER_SHORTNAME}} — R&R update {{TODAY_ISO}}`
- `Subject: {{PAPER_SHORTNAME}} — pre-submission update {{TODAY_ISO}}`
- `Subject: {{PAPER_SHORTNAME}} — post-conference update {{TODAY_ISO}}`

---

## Examples

### Example 1: Mid-project status update
**Input:**
- Paper short-name: `bank-disclosure`
- Coauthors: Maria Alvarez, Tom Chen
- Today: 2026-06-23
- STATE.md PCT: 55%. Session closed 2 threads (a robustness check and an intro rewrite).
- Session deltas: added Callaway–Sant'Anna estimator to Table 5; rewrote the intro's contribution paragraph; added Appendix C on alternative event windows; flagged the WRDS Compustat extract is from 2024Q4 and needs refresh.

**Output:**
```
# Word count: 248 / 350
# Coauthors addressed: Alvarez, Chen
# Asks regex check: PASS
# Pulled from STATE.md as of: 2026-06-22

Subject: bank-disclosure — update 2026-06-23

Hi Maria, Tom,

Quick update. We're at 62% done on bank-disclosure.

What changed since the last update:

1. Added Callaway–Sant'Anna estimator as Column 4 of Table 5; β = 0.143, t = 3.8.
2. Rewrote the intro contribution paragraph (Section 1, paragraphs 3–4).
3. Added Appendix C with alternative event windows (±3, ±5, ±7 years).
4. Flagged the Compustat extract is stale (2024Q4); needs refresh before resubmission.

What I'm asking from you (with deadlines):

1. Alvarez — read the new intro contribution paragraph and react, by 2026-06-30.
2. Chen — pull a fresh Compustat extract through 2026Q1 from WRDS, by 2026-07-07.

What I'm doing next (mine to own):

1. Re-run the full Table 5 with the new extract, by 2026-07-10.
2. Draft the response to R2.4 on parallel trends, by 2026-07-03.

Risks / open questions:

1. The Callaway–Sant'Anna point estimate is 18% smaller than TWFE. Is that
   a story we own in the text or a footnote?

Best,
Jedson
```

### Example 2: Urgent R&R deadline in 3 weeks
**Input:**
- Paper short-name: `audit-fees-AI`
- Coauthors: Priya Rao, Ben Mueller
- Today: 2026-06-23
- R&R deadline: 2026-07-14 (3 weeks out)
- STATE.md PCT: 70%. Two big open threads (NLP robustness + a new sample-selection control).
- Session deltas: finished prompt-perturbation robustness for the NLP classifier (LLM_VALIDATION_KIT items 6 and 7); started entropy balancing as the new identification check; rewrote the abstract.

**Output:**
```
# Word count: 289 / 350
# Coauthors addressed: Rao, Mueller
# Asks regex check: PASS
# Pulled from STATE.md as of: 2026-06-23

Subject: audit-fees-AI — R&R update 2026-06-23

Hi Priya, Ben,

Quick update. We're at 76% done on audit-fees-AI. R&R is due 2026-07-14, 3 weeks out.

What changed since the last update:

1. Finished prompt-perturbation robustness for the NLP classifier; agreement = 0.91 across 3 prompt variants on 200 docs (new Appendix D, Table D2).
2. Started entropy balancing for the new identification check requested by R1; first pass in `code/07_entropy_balance.do`, results not yet in the paper.
3. Rewrote the abstract to lead with the disclosure-quality channel.
4. Confirmed Cohen's kappa human-vs-model = 0.78 and human-vs-human = 0.82 (LLM_VALIDATION_KIT items 1–3 complete).

What I'm asking from you (with deadlines):

1. Rao — read the rewritten abstract and react, by 2026-06-27.
2. Rao — produce 50-doc false-negative analysis for the NLP classifier, by 2026-07-01.
3. Mueller — review the entropy balancing setup in `07_entropy_balance.do` and sign off on the weighting choice, by 2026-06-30.

What I'm doing next (mine to own):

1. Drop entropy-balanced columns into Table 4, by 2026-07-02.
2. Draft the full response letter, by 2026-07-08.
3. Final read-through and submit, by 2026-07-13.

Risks / open questions:

1. If entropy balancing kills the result, we need a Plan B before 2026-07-08.
2. R3 has not been heard from since the original review. Do we expect a third reviewer on resubmission?

Best,
Jedson
```

---

## Edge Cases & Failure Modes
| Situation | How to Handle |
|---|---|
| STATE.md missing | Ask user for `Stage`, `Completion`, coauthor list once. Do not proceed without these three. |
| No session deltas (zero meaningful changes) | Refuse to ship the email. Tell user: "No meaningful changes since last update. Skip this week or send a 1-line note instead." |
| Word count exceeds 350 after all compression rules | Drop the Risks block first, then the lowest-importance Phase 2 bullet. Never compress asks. |
| Coauthor first name unknown | Use full name once; ask user to confirm short form for future use. |
| Date lands on weekend | Shift to next Monday. Note the shift in a comment but not in the email body. |
| User asks for the email but project is stage `idea` | Refuse. The skill is for projects past `data-build`. Suggest the Project Resurrection skill instead. |
| Completion percentage went down | Add a Risks line explaining the regression. Do not silently lower the number. |
| R&R deadline is < 7 days out | Compress all default deadlines by 50%. Add a Risks line naming the deadline. |
| Sole-author paper (no coauthors) | Refuse. Suggest the Project Resurrection skill or a self-directed checklist. |
| Coauthor list > 4 | Allow but warn user; emails to large groups historically get worse response rates. Tag the 2 most senior in the subject. |
| Same ask sent to coauthor in last update | Flag it visibly; mark the ask as `[FOLLOW-UP]` in the email. |
| Conflicting STATE.md and session ("STATE says 55%, user says 80%") | Use user's stated number; insert a Risks line noting the STATE.md discrepancy and propose updating STATE.md as a self-owned next step. |

---

## Hard Rules
1. Total body must be ≤ 350 words (HOUSE_VOICE §1, COAUTHOR_EMAIL_STYLE §4).
2. Opening sentence MUST be exactly: `Quick update. We're at [PCT]% done on [paper short-name].`
3. Every list MUST be numbered, never bulleted.
4. Every "asking from you" item MUST have a named owner LastName and an ISO date.
5. No em dashes anywhere. Use periods or semicolons.
6. No banned openers ("However," "Moreover," "Furthermore," "Additionally," "Interestingly," "Overall," "In conclusion").
7. No "thanks for your work" paragraph. The numbered structure is the respect.
8. No "we should," "we need to," "we might consider." Asks are owned and dated, or they are not asks.
9. Signature is exactly `Best,\nJedson`. No title block, no email signature, no quotes.
10. Subject line is exactly `Subject: [Paper short-name] — update [YYYY-MM-DD]` (no em dash; ASCII hyphen).
11. Specific artifact references required in every Phase 2 bullet (Table N, Figure N, Section N.N, Appendix X, or filename).
12. If `Completion` percentage decreased, add a Risks bullet explaining; never silently lower.
13. Self-owned next steps section may have at most 3 items.
14. Risks block may have at most 2 items.
15. The skill output to the user MUST start with the `# Word count: ...` comment block.

---

## Quality Checklist
- [ ] Word count ≤ 350 (verified by count, not estimate).
- [ ] Subject line matches the exact template, no em dashes, ISO date.
- [ ] Greeting uses first names of every coauthor, comma-separated.
- [ ] Opening sentence is the fixed string, with `PCT` and `paper short-name` substituted.
- [ ] PCT is an integer; not a range, not a decimal.
- [ ] Every Phase 2 bullet names a specific artifact (Table, Figure, Section, Appendix, file).
- [ ] Every "asking from you" item has LastName + task + ISO date.
- [ ] No "asking" item uses passive or hedged language ("could you," "would you mind").
- [ ] Self-owned next steps have ISO dates.
- [ ] No banned constructions from HOUSE_VOICE §1.
- [ ] No em dashes; ASCII hyphens only.
- [ ] Signature is exactly `Best,\nJedson`.
- [ ] Pre-flight comment block shows word count and PASS on regex check.
- [ ] STATE.md `Completion` reconciled (either matches new PCT or Risk noted).
- [ ] Numbered (not bulleted) lists throughout.

---

## ROI Estimate
| Metric | Value |
|---|---|
| Manual time per use | 0.75 hrs |
| Time with skill | 0.10 hrs |
| Time saved per use | 0.65 hrs |
| Estimated uses per year | 80 |
| Annual time savings | 52 hrs |
| Stakes | Coauthor goodwill, R&R turnaround speed, clarity of who-owes-what (project-finishing rate). |
