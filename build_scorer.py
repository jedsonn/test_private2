"""Parse the EAA 2026 programme, score every paper, emit interactive HTML."""
from __future__ import annotations
import json
import re
from pathlib import Path
from html import escape

ROOT = Path(__file__).parent
RAW = ROOT / "programme_raw.txt"
OUT = ROOT / "eaa_2026_scored.html"

TRACKS = {
    "AU": "Auditing",
    "ED": "Accounting Education",
    "FA": "Financial Analysis",
    "FR": "Financial Reporting",
    "GV": "Accounting and Governance",
    "HI": "History",
    "IC": "Interdisciplinary / Critical",
    "IS": "Accounting and Information Systems",
    "MA": "Management Accounting",
    "PSNP": "Public Sector / Not-For-Profit",
    "SEE": "Social and Environmental",
    "TX": "Taxation",
}

TRACK_HEADER_RE = re.compile(
    r"^(AU|ED|FA|FR|GV|HI|IC|IS|MA|PSNP|SEE|TX) [-–] "
)
DAY_RE = re.compile(
    r"^(Wednesday|Thursday|Friday), May (\d+), (\d{2}:\d{2}-\d{2}:\d{2})$"
)
SESSION_RE = re.compile(
    r"^(AU|ED|FA|FR|GV|HI|IC|IS|MA|PSNP|SEE|TX) (PSD?\d+|PS\d+|PSD\d+).*?chaired by: (.+?)(?:\(.*\))?\s*$"
)
SESSION_RE_LOOSE = re.compile(
    r"^(AU|ED|FA|FR|GV|HI|IC|IS|MA|PSNP|SEE|TX)\s+(PSD?\d+|PS\d+|PSD\d+).*?room\s+(\S+(?:\s+\d+)?)"
)
SESSION_CHAIR_RE = re.compile(r"chaired by:\s*(.+?)\s*$")
PAPER_RE = re.compile(r"^(\d+)\.\s+(.+)$")
AUTHOR_RE = re.compile(r"^(.+?)\s*\((.+?)\)(P)?\s*$")
DISCUSSANT_RE = re.compile(r"^Discussant:\s*(.+?)\s*$")


def parse_programme(text: str):
    lines = text.split("\n")
    papers = []
    cur_track = None
    cur_day = None
    cur_session = None
    cur_room = None
    cur_chair = None
    cur_paper = None

    def commit():
        nonlocal cur_paper
        if cur_paper and cur_paper.get("title"):
            cur_paper["title"] = cur_paper["title"].strip().rstrip(".").strip()
            papers.append(cur_paper)
        cur_paper = None

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Track header (e.g. "AU – Auditing")
        m = TRACK_HEADER_RE.match(line)
        if m and len(line) < 80:
            commit()
            cur_track = m.group(1)
            i += 1
            continue

        # Day-time header
        m = DAY_RE.match(line)
        if m:
            commit()
            cur_day = f"{m.group(1)} May {m.group(2)} {m.group(3)}"
            i += 1
            continue

        # Session header (look for PS / PSD pattern + "chaired by" possibly on same line)
        # Pattern: "AU PSD03 room RB 211 . . . . . . . chaired by: Aymen Abbadi (IAE Lille University)"
        m = re.match(
            r"^(AU|ED|FA|FR|GV|HI|IC|IS|MA|PSNP|SEE|TX)\s+(PSD?\d+|PS\d+)\s+room\s+(\S+(?:\s+\S+)?)",
            line,
        )
        if m:
            commit()
            cur_track = m.group(1)
            cur_session = f"{m.group(1)} {m.group(2)}"
            cur_room = m.group(3).strip(" .")
            chair_m = SESSION_CHAIR_RE.search(line)
            cur_chair = chair_m.group(1).strip() if chair_m else None
            i += 1
            continue

        # Sometimes the chair line wraps to next line
        if line.startswith("chaired by:") and cur_session:
            chair_m = SESSION_CHAIR_RE.match(line)
            if chair_m:
                cur_chair = chair_m.group(1).strip()
            i += 1
            continue

        # Paper line: "1. Title..."
        m = PAPER_RE.match(line)
        if m:
            commit()
            cur_paper = {
                "track": cur_track,
                "track_name": TRACKS.get(cur_track, cur_track),
                "day": cur_day,
                "session": cur_session,
                "room": cur_room,
                "chair": cur_chair,
                "number": int(m.group(1)),
                "title": m.group(2).strip(),
                "authors": [],
                "presenter": None,
                "presenter_aff": None,
                "discussant": None,
                "discussant_aff": None,
            }
            # Titles can wrap over 1+ lines; consume continuations until we hit a structural marker
            j = i + 1
            while j < len(lines):
                nxt = lines[j].strip()
                if not nxt:
                    j += 1
                    continue
                # Stop if next line looks like author / discussant / new paper / new session / day header
                if DISCUSSANT_RE.match(nxt):
                    break
                if PAPER_RE.match(nxt):
                    break
                if DAY_RE.match(nxt):
                    break
                if TRACK_HEADER_RE.match(nxt):
                    break
                if re.match(r"^(AU|ED|FA|FR|GV|HI|IC|IS|MA|PSNP|SEE|TX)\s+(PSD?\d+|PS\d+)\s+room", nxt):
                    break
                if nxt.startswith("chaired by:"):
                    break
                # Author lines look like "Name (Affiliation)" with optional trailing P
                if AUTHOR_RE.match(nxt):
                    break
                # Title continuation
                cur_paper["title"] += " " + nxt
                i = j
                j += 1
            i += 1
            continue

        # Discussant FIRST (otherwise AUTHOR_RE swallows "Discussant: Name (Aff)")
        if cur_paper:
            m = DISCUSSANT_RE.match(line)
            if m:
                disc = m.group(1).strip()
                aff_m = re.match(r"^(.+?)\s*\((.+?)\)\s*$", disc)
                if aff_m:
                    cur_paper["discussant"] = aff_m.group(1).strip()
                    cur_paper["discussant_aff"] = aff_m.group(2).strip()
                else:
                    cur_paper["discussant"] = disc
                i += 1
                continue

            # Author line: "Name (Affiliation)" possibly with trailing P
            m = AUTHOR_RE.match(line)
            if m:
                name = m.group(1).strip()
                aff = m.group(2).strip()
                is_pres = m.group(3) == "P"
                cur_paper["authors"].append({"name": name, "affiliation": aff, "presenter": is_pres})
                if is_pres:
                    cur_paper["presenter"] = name
                    cur_paper["presenter_aff"] = aff
                i += 1
                continue

        i += 1

    commit()
    return papers


# ---------- Scoring ---------------------------------------------------------

KEY_AI = re.compile(
    r"\b(AI|artificial intelligence|machine learning|deep learning|"
    r"large language model|LLM|GPT|ChatGPT|generative AI|"
    r"natural language processing|NLP|neural network|"
    r"text(?:-| )based|textual analysis|algorithm|algorithmic|"
    r"BERT|transformer|video analytics|computer vision)\b",
    re.I,
)
KEY_DISCLOSURE = re.compile(
    r"\b(disclosure|disclosed|disclos\w*|reporting|report\b|narrative|"
    r"comment letter|10-K|8-K|filing|annual report|conference call|"
    r"earnings call|management forecast|guidance|press release|"
    r"transparency|narrative disclosure|risk factor|sustainability report|"
    r"CSR report|ESG report)\b",
    re.I,
)
KEY_DID = re.compile(
    r"\b(difference[- ]in[- ]differences|diff[- ]in[- ]diff|DiD|DID|"
    r"two[- ]way fixed effects|2WFE|staggered|event study|"
    r"spillover|spillovers)\b",
    re.I,
)
# Implicit DiD signals: "after the X" / "introduction of" / "before-after" / etc.
# Used to bump the exogenous-shock score, not the explicit DiD flag
KEY_IMPLICIT_DID = re.compile(
    r"\b(after the|adoption of|introduction of|implementation of|"
    r"following the|in response to|since the|"
    r"pre[- ]post|before[- ]after|"
    r"reform|mandate|act\b|directive|enactment)\b",
    re.I,
)
KEY_RDD = re.compile(
    r"\b(regression discontinuity|RDD|RD design|threshold|sharp cutoff|"
    r"running variable|kink|bandwidth)\b",
    re.I,
)
KEY_EXOGENOUS = re.compile(
    r"\b(natural experiment|quasi[- ]natural|quasi[- ]experiment|"
    r"randomized field experiment|RCT|exogenous shock|"
    r"shock\b|reform|regulation|regulatory|act\b|directive|mandate|"
    r"mandatory|enacted|implementation of|introduction of|adoption of|"
    r"PCAOB|SEC rule|EU\b|GDPR|CSRD|SFDR|IFRS \d+|ASC \d+|FRC|JOBS Act|"
    r"Sarbanes[- ]Oxley|SOX|Reg SHO|TCFD|CECL|PACTE|Solvency|"
    r"COVID|pandemic|war|invasion|sanctions?|election|crisis|"
    r"scandal|Wirecard|Carillion|Volkswagen|emissions scandal|"
    r"Fukushima|disaster|withdrawal|closure|bankruptcy|merger|acquisition|"
    r"executive order|policy shift|deregulation|enforcement|"
    r"newspaper closure|prison closure|trade war)\b",
    re.I,
)
KEY_IDENTIFICATION = re.compile(
    r"\b(causal|identification|instrumental variable|IV\b|"
    r"propensity score|matched|matching|synthetic control|"
    r"placebo|exogenous|natural experiment|"
    r"randomized|randomly assigned|random allocation|field experiment|"
    r"quasi[- ]natural|quasi[- ]experiment|"
    r"difference[- ]in[- ]differences|DiD|DID|"
    r"regression discontinuity|RDD|"
    r"staggered|two[- ]way fixed effects|2WFE)\b",
    re.I,
)
KEY_NOVELTY = re.compile(
    r"\b(novel|new measure|new evidence|first|introduce|construct|"
    r"propose a new|original|unprecedented|emerging|generative|"
    r"large language model|LLM|adversarial|multimodal|video analytics|"
    r"satellite verification|biodiversity)\b",
    re.I,
)
KEY_RELEVANCE = re.compile(
    r"\b(real effects|cost of capital|cost of debt|investment|"
    r"capital structure|firm value|market reaction|stock price|"
    r"liquidity|credit rating|loan|debt|fee|earnings management|"
    r"audit quality|disclosure quality|reporting quality|"
    r"analyst forecast|forecast accuracy|productivity|"
    r"compensation|incentive|governance|regulation|standard|"
    r"comply|compliance)\b",
    re.I,
)
KEY_TIMELY = re.compile(
    r"\b(AI|generative|LLM|GPT|ChatGPT|machine learning|"
    r"climate|carbon|biodiversity|net zero|net[- ]zero|"
    r"ESG|CSRD|SFDR|TCFD|sustainability|greenwash|green\b|"
    r"crypto|blockchain|cybersecurity|cyber|data breach|"
    r"COVID|pandemic|war|invasion|geopolit|sanction)\b",
    re.I,
)
KEY_POLICY = re.compile(
    r"\b(regulator|regulation|standard[- ]setter|policy|policymaker|"
    r"comment letter|SEC|PCAOB|FASB|IASB|EU|directive|mandate|"
    r"reform|enforcement|supervision|standard\b|public input|"
    r"rulemaking|implication for)\b",
    re.I,
)
KEY_MECHANISM = re.compile(
    r"\b(mechanism|channel|moderating|moderator|mediating|mediator|"
    r"role of|how does|why|drivers|determinant|the effect of|"
    r"the impact of)\b",
    re.I,
)
# Core accounting topics: financial reporting, audit, tax, MA, governance, disclosure
KEY_ACCOUNTING_CORE = re.compile(
    r"\b(audit|auditor|auditing|disclosure|reporting|GAAP|IFRS|"
    r"earnings|accrual|impairment|goodwill|fair value|impair|"
    r"compensation|tax|taxation|pricing|fee|"
    r"internal control|SOX|KAM|critical audit matter|"
    r"comment letter|misstatement|restatement|cost stickiness|"
    r"non-GAAP|XBRL|going concern|leverage|covenant|"
    r"loan loss provision|management forecast|management control|"
    r"performance measure|budget|incentive)\b",
    re.I,
)


def score_paper(p: dict) -> dict:
    title = p["title"]
    title_l = title.lower()

    def hits(rx) -> int:
        return len(rx.findall(title))

    # Calibrated 0-5 baselines: 2 = average paper, 3+ = positive signal, 5 = strongly hits criterion
    # AI: 0 = no AI; 3 = AI used as method; 5 = LLM/generative core to design
    ai_h = hits(KEY_AI)
    ai = 0
    if ai_h >= 1: ai = 3
    if ai_h >= 2: ai = 4
    if re.search(r"\b(generative AI|large language|LLM|GPT|ChatGPT|multimodal)\b", title, re.I):
        ai = max(ai, 5)

    # Disclosure: 0 = no disclosure mention; baseline 2 if disclosure-adjacent;
    # 4 = focal disclosure paper; 5 = disclosure regulation/mandate
    disc_h = hits(KEY_DISCLOSURE)
    disclosure = 0
    if disc_h >= 1: disclosure = 3
    if disc_h >= 2: disclosure = 4
    if re.search(r"\b(mandatory disclosure|disclosure regulation|disclosure mandate|"
                 r"non-financial disclosure|sustainability disclosure)\b", title, re.I):
        disclosure = max(disclosure, 5)

    # DiD / RDD: binary indicators, 5 if explicit
    did = 5 if hits(KEY_DID) else 0
    rdd = 5 if hits(KEY_RDD) else 0

    # Exogenous shock: regulation/event/disaster/scandal etc.
    exo_h = hits(KEY_EXOGENOUS)
    implicit_did_h = hits(KEY_IMPLICIT_DID)
    exogenous = 0
    if exo_h >= 1: exogenous = 3
    if exo_h >= 2: exogenous = 4
    if exo_h >= 3: exogenous = 5
    # Implicit DiD signals also count as exogenous-shock hints (additive)
    if implicit_did_h >= 1 and exogenous < 3:
        exogenous = max(exogenous, 2)
    if implicit_did_h >= 2:
        exogenous = max(exogenous, 4)

    # Identification: clean causal language
    ident_h = hits(KEY_IDENTIFICATION)
    identification = 1  # baseline (most papers have some identification effort)
    if ident_h >= 1: identification = 3
    if ident_h >= 2: identification = 4
    if did or rdd: identification = 5
    if re.search(r"\b(natural experiment|randomized field experiment|RCT|"
                 r"propensity score|matching|synthetic control|placebo)\b",
                 title, re.I):
        identification = max(identification, 4)

    # Novelty: baseline 2 (every paper claims some)
    novelty = 2
    novelty += hits(KEY_NOVELTY)
    if ai >= 4: novelty = max(novelty, 4)
    if re.search(r"\b(satellite|biodiversity|crypto|blockchain|video analytics|"
                 r"speculative design|quantum|adversarial|prompt|"
                 r"machine[- ]readable|multimodal)\b", title, re.I):
        novelty = max(novelty, 4)
    novelty = min(5, novelty)

    # Relevance: baseline 3 (every accounting paper is relevant to someone)
    relevance = 3
    if hits(KEY_RELEVANCE) >= 1: relevance = 4
    if hits(KEY_RELEVANCE) >= 2: relevance = 5
    if "real effect" in title_l or "real effects" in title_l:
        relevance = 5
    relevance = min(5, relevance)

    # Timeliness: baseline 2 (most accounting research is on durable topics)
    timeliness = 2
    timely_h = hits(KEY_TIMELY)
    if timely_h >= 1: timeliness = 4
    if timely_h >= 2: timeliness = 5
    if ai >= 4: timeliness = 5

    # Policy relevance: baseline 2
    policy = 2
    pol_h = hits(KEY_POLICY)
    if pol_h >= 1: policy = 3
    if pol_h >= 2: policy = 4
    if re.search(r"\b(comment letter|standard[- ]setter|public input|rulemaking)\b",
                 title, re.I):
        policy = max(policy, 4)
    policy = min(5, policy)

    # Mechanism: baseline 2
    mechanism = 2
    mech_h = hits(KEY_MECHANISM)
    if mech_h >= 1: mechanism = 3
    if mech_h >= 2: mechanism = 4
    if re.search(r"\b(channel|mechanism|moderating|mediating)\b", title, re.I):
        mechanism = max(mechanism, 4)
    mechanism = min(5, mechanism)

    # Accounting fit: baseline 4 (it's an EAA paper). 5 if hits core terms; lower if peripheral
    acc_h = hits(KEY_ACCOUNTING_CORE)
    accounting_fit = 4
    if acc_h >= 1: accounting_fit = 5
    # Penalize generic non-accounting topics
    if re.search(r"\b(walking|pedagogy|cultural|moral judgment|education)\b", title, re.I):
        accounting_fit = min(accounting_fit, 3)

    # Causal rigor: roll-up
    causal_rigor = 2
    if identification >= 4: causal_rigor = 4
    if did or rdd: causal_rigor = 5
    if exogenous >= 4 and identification >= 3: causal_rigor = max(causal_rigor, 4)

    # Penalty: title is very short or very generic
    if len(title) < 25:
        novelty = max(0, novelty - 1)

    # Qualitative / review papers: lower identification & causal rigor, but mechanism stays
    if re.search(
        r"\b(qualitative|ethnographic|systematic literature review|"
        r"systematic review|literature review|conceptual|"
        r"foundational reflection|theoretical model|case study|"
        r"interview|reflections?)\b",
        title, re.I):
        identification = min(identification, 2)
        causal_rigor = min(causal_rigor, 2)
        novelty = max(novelty, 2)
        mechanism = max(mechanism, 3)

    # Theory / analytical papers
    if re.search(r"\b(strategic disclosure when|optimal frequency|"
                 r"public information and market coordination|"
                 r"information design|signal\w*|theoretical|model|"
                 r"equilibrium)\b", title, re.I) and "evidence" not in title_l:
        # likely theory paper
        identification = min(identification, 2)
        causal_rigor = min(causal_rigor, 2)
        novelty = max(novelty, 3)

    # Experimental / RCT bumps identification
    if re.search(r"\b(experimental|experiment\b|randomized|"
                 r"field experiment|randomly assigned)\b", title, re.I):
        identification = max(identification, 4)
        causal_rigor = max(causal_rigor, 4)

    # Composite — weighted blend. Sum of weights = 10 so composite is on 0–5 scale
    weights = {
        "novelty": 1.6,
        "identification": 1.6,
        "exogenous": 1.0,
        "relevance": 1.2,
        "accounting_fit": 1.0,
        "timeliness": 0.8,
        "causal_rigor": 1.0,
        "mechanism": 0.6,
        "policy": 0.6,
        "disclosure": 0.3,
        "ai": 0.3,
    }
    raw_scores = {
        "novelty": novelty,
        "identification": identification,
        "exogenous": exogenous,
        "relevance": relevance,
        "accounting_fit": accounting_fit,
        "timeliness": timeliness,
        "causal_rigor": causal_rigor,
        "mechanism": mechanism,
        "policy": policy,
        "disclosure": disclosure,
        "ai": ai,
    }
    composite = sum(weights[k] * raw_scores[k] for k in weights) / sum(weights.values())
    composite = round(composite * 10) / 10  # one decimal

    return {
        "novelty": novelty,
        "exogenous_shock": exogenous,
        "identification": identification,
        "relevance": relevance,
        "timeliness": timeliness,
        "accounting_fit": accounting_fit,
        "ai": ai,
        "disclosure": disclosure,
        "rdd": rdd,
        "did": did,
        "causal_rigor": causal_rigor,
        "mechanism": mechanism,
        "policy_relevance": policy,
        "composite": composite,
    }


def main():
    text = RAW.read_text(encoding="utf-8")
    papers = parse_programme(text)

    # Score everything
    for p in papers:
        p["scores"] = score_paper(p)

    print(f"Parsed {len(papers)} papers across {len({p['track'] for p in papers})} tracks.")
    by_track = {}
    for p in papers:
        by_track.setdefault(p["track"], 0)
        by_track[p["track"]] += 1
    for t, n in sorted(by_track.items()):
        print(f"  {t}: {n}")

    # Render HTML
    html = render_html(papers)
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({len(html)/1024:.0f} KB)")


def render_html(papers: list[dict]) -> str:
    payload = json.dumps(papers, ensure_ascii=False)
    payload_b64 = payload.replace("\\", "\\\\").replace("`", "\\`").replace("</", "<\\/")
    track_options = "".join(
        f'<label class="chip"><input type="checkbox" value="{k}" checked> '
        f'<span class="chip-label" data-track="{k}">{k} · {escape(v)}</span></label>'
        for k, v in TRACKS.items()
    )
    days = sorted({p["day"] for p in papers if p["day"]})
    day_options = "".join(
        f'<label class="chip"><input type="checkbox" value="{escape(d)}" checked> '
        f'<span class="chip-label">{escape(d)}</span></label>'
        for d in days
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EAA 2026 — Scored Programme</title>
<style>
* {{ box-sizing: border-box; }}
:root {{
  --bg: #0b0d12;
  --bg-2: #131722;
  --bg-3: #1a2032;
  --fg: #e6e8ee;
  --fg-dim: #9aa3b8;
  --fg-faint: #5b6478;
  --accent: #6ea8fe;
  --accent-2: #b78dff;
  --good: #3ddc97;
  --warn: #ffb454;
  --bad: #ff6b6b;
  --border: #232838;
  --row-hover: #1d2435;
  --shadow: 0 1px 0 rgba(255,255,255,0.04), 0 8px 24px rgba(0,0,0,0.5);
}}
body {{
  margin: 0; padding: 0;
  background: var(--bg); color: var(--fg);
  font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif;
  font-size: 14px; line-height: 1.5;
}}
header {{
  position: sticky; top: 0; z-index: 100;
  background: linear-gradient(180deg, var(--bg-2) 0%, var(--bg-2) 80%, transparent);
  border-bottom: 1px solid var(--border);
  padding: 12px 18px;
  backdrop-filter: blur(8px);
}}
.title-row {{
  display: flex; align-items: baseline; justify-content: space-between; flex-wrap: wrap; gap: 12px;
}}
h1 {{ margin: 0; font-size: 17px; font-weight: 600; letter-spacing: -0.01em; }}
h1 .accent {{ color: var(--accent); }}
.subtitle {{ color: var(--fg-dim); font-size: 12px; }}
.controls {{
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 10px;
}}
@media (max-width: 900px) {{ .controls {{ grid-template-columns: 1fr; }} }}
.control-block {{
  background: var(--bg-3); border: 1px solid var(--border);
  border-radius: 8px; padding: 8px 10px;
  max-height: 110px; overflow-y: auto;
}}
.control-block-title {{
  font-size: 11px; color: var(--fg-faint); text-transform: uppercase; letter-spacing: 0.05em;
  margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;
}}
.control-block-title button {{
  background: transparent; border: 1px solid var(--border); color: var(--fg-dim);
  padding: 2px 8px; font-size: 10px; border-radius: 4px; cursor: pointer;
}}
.control-block-title button:hover {{ color: var(--fg); border-color: var(--fg-dim); }}
.chips {{ display: flex; flex-wrap: wrap; gap: 4px; }}
.chip {{
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 7px; border-radius: 999px;
  background: var(--bg-2); border: 1px solid var(--border);
  font-size: 11px; cursor: pointer; user-select: none;
}}
.chip input {{ accent-color: var(--accent); margin: 0; cursor: pointer; }}
.chip:hover {{ border-color: var(--accent); }}
.chip-label[data-track="AU"] {{ color: #ffb454; }}
.chip-label[data-track="ED"] {{ color: #c9a3ff; }}
.chip-label[data-track="FA"] {{ color: #6ea8fe; }}
.chip-label[data-track="FR"] {{ color: #3ddc97; }}
.chip-label[data-track="GV"] {{ color: #ff8fa3; }}
.chip-label[data-track="HI"] {{ color: #ffd56b; }}
.chip-label[data-track="IC"] {{ color: #b78dff; }}
.chip-label[data-track="IS"] {{ color: #5cd6ff; }}
.chip-label[data-track="MA"] {{ color: #f1948a; }}
.chip-label[data-track="PSNP"] {{ color: #82e0aa; }}
.chip-label[data-track="SEE"] {{ color: #58d68d; }}
.chip-label[data-track="TX"] {{ color: #f7dc6f; }}
.search-row {{
  display: flex; gap: 8px; margin-top: 10px; align-items: center;
}}
input[type=search], input[type=text] {{
  flex: 1; padding: 8px 12px; border-radius: 8px;
  background: var(--bg-3); border: 1px solid var(--border); color: var(--fg);
  font-size: 13px;
}}
input[type=search]:focus, input[type=text]:focus {{ outline: none; border-color: var(--accent); }}
.summary {{ font-size: 12px; color: var(--fg-dim); margin-top: 8px; }}
.summary b {{ color: var(--fg); font-weight: 600; }}
.legend {{ font-size: 11px; color: var(--fg-faint); margin-top: 4px; }}
main {{ padding: 12px 18px 60px; }}
table {{
  width: 100%; border-collapse: collapse;
  font-size: 12.5px;
  background: var(--bg-2); border-radius: 8px; overflow: hidden;
  box-shadow: var(--shadow);
}}
th {{
  background: var(--bg-3); color: var(--fg-dim);
  font-weight: 600; text-align: left; padding: 8px 10px;
  font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em;
  position: sticky; top: 0;
  border-bottom: 1px solid var(--border);
  cursor: pointer; user-select: none;
}}
th:hover {{ color: var(--fg); }}
th.sorted-asc::after {{ content: " ↑"; color: var(--accent); }}
th.sorted-desc::after {{ content: " ↓"; color: var(--accent); }}
td {{
  padding: 8px 10px; border-bottom: 1px solid var(--border);
  vertical-align: top;
}}
tr:hover td {{ background: var(--row-hover); }}
.title-cell {{ font-weight: 500; max-width: 480px; }}
.title-cell .meta {{ color: var(--fg-faint); font-size: 11px; margin-top: 2px; }}
.author-cell {{ font-size: 11.5px; color: var(--fg-dim); max-width: 200px; }}
.author-cell .pres {{ color: var(--fg); font-weight: 600; }}
.track-tag {{
  display: inline-block; padding: 1px 6px; border-radius: 4px;
  font-size: 10px; font-weight: 700; letter-spacing: 0.04em;
  background: var(--bg-3); border: 1px solid var(--border);
}}
.track-tag.AU {{ color: #ffb454; }}
.track-tag.ED {{ color: #c9a3ff; }}
.track-tag.FA {{ color: #6ea8fe; }}
.track-tag.FR {{ color: #3ddc97; }}
.track-tag.GV {{ color: #ff8fa3; }}
.track-tag.HI {{ color: #ffd56b; }}
.track-tag.IC {{ color: #b78dff; }}
.track-tag.IS {{ color: #5cd6ff; }}
.track-tag.MA {{ color: #f1948a; }}
.track-tag.PSNP {{ color: #82e0aa; }}
.track-tag.SEE {{ color: #58d68d; }}
.track-tag.TX {{ color: #f7dc6f; }}
.score {{
  display: inline-block; min-width: 22px; padding: 1px 5px;
  border-radius: 4px; text-align: center; font-weight: 600; font-size: 11px;
  font-variant-numeric: tabular-nums;
}}
.score-cell {{ text-align: center; font-variant-numeric: tabular-nums; }}
.composite-cell {{
  font-weight: 700; font-size: 14px; text-align: center;
  font-variant-numeric: tabular-nums;
}}
.badges {{ display: flex; flex-wrap: wrap; gap: 3px; }}
.badge {{
  display: inline-block; padding: 1px 5px; font-size: 10px; font-weight: 600;
  border-radius: 3px; letter-spacing: 0.02em;
  background: rgba(110,168,254,0.12); color: var(--accent); border: 1px solid rgba(110,168,254,0.3);
}}
.badge.ai {{ background: rgba(183,141,255,0.12); color: var(--accent-2); border-color: rgba(183,141,255,0.3); }}
.badge.disc {{ background: rgba(61,220,151,0.12); color: var(--good); border-color: rgba(61,220,151,0.3); }}
.badge.did {{ background: rgba(255,180,84,0.12); color: var(--warn); border-color: rgba(255,180,84,0.3); }}
.badge.rdd {{ background: rgba(255,107,107,0.12); color: var(--bad); border-color: rgba(255,107,107,0.3); }}
.badge.exo {{ background: rgba(92,214,255,0.12); color: #5cd6ff; border-color: rgba(92,214,255,0.3); }}
.expanded-row {{ background: var(--bg-3); }}
.expanded-row td {{ padding: 12px 16px 14px; }}
.detail-grid {{
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px;
  margin-bottom: 8px;
}}
@media (max-width: 800px) {{ .detail-grid {{ grid-template-columns: 1fr; }} }}
.detail-block h4 {{ margin: 0 0 6px; font-size: 11px; color: var(--fg-faint);
  text-transform: uppercase; letter-spacing: 0.05em; }}
.detail-block ul {{ margin: 0; padding-left: 16px; font-size: 12px; color: var(--fg-dim); }}
.detail-block ul li.pres {{ color: var(--fg); font-weight: 500; }}
.score-grid {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 6px;
  margin-top: 6px;
}}
.score-item {{
  background: var(--bg-2); border: 1px solid var(--border); padding: 6px 8px;
  border-radius: 6px; font-size: 11px;
}}
.score-item .label {{ color: var(--fg-faint); font-size: 10px;
  text-transform: uppercase; letter-spacing: 0.04em; }}
.score-item .val {{ font-weight: 700; font-size: 16px; font-variant-numeric: tabular-nums; }}
.score-item.s5 .val {{ color: #3ddc97; }}
.score-item.s4 .val {{ color: #6ea8fe; }}
.score-item.s3 .val {{ color: #ffd56b; }}
.score-item.s2 .val {{ color: #ffb454; }}
.score-item.s1 .val {{ color: #ff8fa3; }}
.score-item.s0 .val {{ color: var(--fg-faint); }}
.row-clickable {{ cursor: pointer; }}
.row-clickable .expand-icon::before {{
  content: "▶"; font-size: 9px; margin-right: 4px; color: var(--fg-faint);
  transition: transform 0.15s;
  display: inline-block;
}}
.row-clickable.expanded .expand-icon::before {{ transform: rotate(90deg); color: var(--accent); }}
footer {{
  text-align: center; padding: 24px 18px; color: var(--fg-faint); font-size: 11px;
}}
.no-results {{
  text-align: center; padding: 40px; color: var(--fg-faint);
  background: var(--bg-2); border-radius: 8px;
}}
</style>
</head>
<body>
<header>
  <div class="title-row">
    <div>
      <h1>EAA <span class="accent">2026</span> — Scored Programme</h1>
      <div class="subtitle">48th EAA Annual Congress · Prague · May 27–29, 2026</div>
    </div>
    <div class="summary" id="summary"></div>
  </div>

  <div class="controls">
    <div class="control-block">
      <div class="control-block-title">
        Tracks
        <span><button onclick="setAll('track', true)">all</button>
              <button onclick="setAll('track', false)">none</button></span>
      </div>
      <div class="chips" id="track-chips">{track_options}</div>
    </div>
    <div class="control-block">
      <div class="control-block-title">
        Day · Slot
        <span><button onclick="setAll('day', true)">all</button>
              <button onclick="setAll('day', false)">none</button></span>
      </div>
      <div class="chips" id="day-chips">{day_options}</div>
    </div>
    <div class="control-block">
      <div class="control-block-title">Quick filters</div>
      <div class="chips">
        <label class="chip"><input type="checkbox" id="f-ai"> <span>AI / LLM</span></label>
        <label class="chip"><input type="checkbox" id="f-did"> <span>DiD</span></label>
        <label class="chip"><input type="checkbox" id="f-rdd"> <span>RDD</span></label>
        <label class="chip"><input type="checkbox" id="f-exo"> <span>Exogenous shock ≥3</span></label>
        <label class="chip"><input type="checkbox" id="f-ident"> <span>Identification ≥4</span></label>
        <label class="chip"><input type="checkbox" id="f-disc"> <span>Disclosure ≥3</span></label>
        <label class="chip"><input type="checkbox" id="f-comp"> <span>Composite ≥3.5</span></label>
      </div>
    </div>
  </div>
  <div class="search-row">
    <input type="search" id="search" placeholder="Search title, author, affiliation, session…">
  </div>
  <div class="legend">
    Click any row to expand · Click headers to sort · Scoring on title heuristics (no abstracts in programme)
  </div>
</header>
<main>
<table id="tbl">
<thead>
  <tr>
    <th data-sort="composite" data-numeric="1" class="sorted-desc">Score</th>
    <th data-sort="track">Track</th>
    <th data-sort="title">Paper</th>
    <th data-sort="presenter">Presenter</th>
    <th data-sort="day">Day · Slot</th>
    <th data-sort="badges">Tags</th>
    <th data-sort="novelty" data-numeric="1">Nov</th>
    <th data-sort="identification" data-numeric="1">Ident</th>
    <th data-sort="exogenous_shock" data-numeric="1">Exo</th>
    <th data-sort="ai" data-numeric="1">AI</th>
    <th data-sort="disclosure" data-numeric="1">Disc</th>
    <th data-sort="timeliness" data-numeric="1">Time</th>
    <th data-sort="relevance" data-numeric="1">Rel</th>
  </tr>
</thead>
<tbody id="tbody"></tbody>
</table>
<div id="no-results" class="no-results" style="display:none">No papers match current filters.</div>
</main>
<footer>
  Sources: <a href="https://eaa-online.org/app/uploads/sites/80/2026/05/scientific_programme-open.pdf"
   style="color:var(--accent)">EAA 2026 Scientific Programme PDF</a>
  · Heuristic scoring on titles (programme has no abstracts)
  · 0–5 scale per dimension · Composite weighted toward novelty + identification + relevance
</footer>

<script>
const PAPERS = {payload};

const SCORE_KEYS = [
  ["novelty","Novelty"],
  ["identification","Identification"],
  ["exogenous_shock","Exogenous shock"],
  ["causal_rigor","Causal rigor"],
  ["mechanism","Mechanism"],
  ["relevance","Relevance"],
  ["timeliness","Timeliness"],
  ["accounting_fit","Accounting fit"],
  ["ai","AI / ML"],
  ["disclosure","Disclosure"],
  ["did","DiD"],
  ["rdd","RDD"],
  ["policy_relevance","Policy relevance"],
];

let sortKey = "composite";
let sortDir = -1; // -1 desc, 1 asc

function getSelected(prefix) {{
  return Array.from(document.querySelectorAll('#'+prefix+'-chips input:checked'))
    .map(i => i.value);
}}

function setAll(prefix, val) {{
  document.querySelectorAll('#'+prefix+'-chips input').forEach(i => i.checked = val);
  render();
}}

function scoreClass(v) {{
  if (v >= 5) return 's5';
  if (v >= 4) return 's4';
  if (v >= 3) return 's3';
  if (v >= 2) return 's2';
  if (v >= 1) return 's1';
  return 's0';
}}

function colorForScore(v) {{
  // Composite uses smoother color
  if (v >= 4.0) return 'background:rgba(61,220,151,0.18);color:#3ddc97';
  if (v >= 3.5) return 'background:rgba(110,168,254,0.18);color:#6ea8fe';
  if (v >= 3.0) return 'background:rgba(255,213,107,0.16);color:#ffd56b';
  if (v >= 2.5) return 'background:rgba(255,180,84,0.16);color:#ffb454';
  if (v >= 2.0) return 'background:rgba(255,143,163,0.14);color:#ff8fa3';
  return 'background:rgba(155,164,184,0.10);color:#9aa3b8';
}}

function badgesFor(p) {{
  const s = p.scores;
  const bs = [];
  if (s.ai >= 3) bs.push('<span class="badge ai">AI</span>');
  if (s.disclosure >= 3) bs.push('<span class="badge disc">Disc</span>');
  if (s.did) bs.push('<span class="badge did">DiD</span>');
  if (s.rdd) bs.push('<span class="badge rdd">RDD</span>');
  if (s.exogenous_shock >= 3) bs.push('<span class="badge exo">Shock</span>');
  if (s.identification >= 4) bs.push('<span class="badge">Causal</span>');
  return bs.join('');
}}

function escapeHtml(s) {{
  if (s === null || s === undefined) return '';
  return String(s).replace(/[&<>"']/g, c => ({{
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }}[c]));
}}

function authorList(p) {{
  if (!p.authors || !p.authors.length) return '';
  return p.authors.map(a => {{
    const cls = a.presenter ? 'class="pres"' : '';
    return '<li ' + cls + '>' + escapeHtml(a.name) +
      ' <span style="color:var(--fg-faint)">— ' + escapeHtml(a.affiliation) + '</span>' +
      (a.presenter ? ' <span style="color:var(--accent);font-size:10px">[presenter]</span>' : '') +
      '</li>';
  }}).join('');
}}

function render() {{
  const tracks = new Set(getSelected('track'));
  const days = new Set(getSelected('day'));
  const q = document.getElementById('search').value.trim().toLowerCase();
  const fAI = document.getElementById('f-ai').checked;
  const fDID = document.getElementById('f-did').checked;
  const fRDD = document.getElementById('f-rdd').checked;
  const fExo = document.getElementById('f-exo').checked;
  const fIdent = document.getElementById('f-ident').checked;
  const fDisc = document.getElementById('f-disc').checked;
  const fComp = document.getElementById('f-comp').checked;

  let rows = PAPERS.filter(p => {{
    if (p.track && !tracks.has(p.track)) return false;
    if (p.day && !days.has(p.day)) return false;
    if (fAI && p.scores.ai < 3) return false;
    if (fDID && !p.scores.did) return false;
    if (fRDD && !p.scores.rdd) return false;
    if (fExo && p.scores.exogenous_shock < 3) return false;
    if (fIdent && p.scores.identification < 4) return false;
    if (fDisc && p.scores.disclosure < 3) return false;
    if (fComp && p.scores.composite < 3.5) return false;
    if (q) {{
      const hay = (
        (p.title||'') + ' ' +
        (p.authors||[]).map(a => a.name + ' ' + a.affiliation).join(' ') + ' ' +
        (p.session||'') + ' ' + (p.day||'') + ' ' + (p.chair||'')
      ).toLowerCase();
      if (!hay.includes(q)) return false;
    }}
    return true;
  }});

  // sort
  rows.sort((a, b) => {{
    let av, bv;
    if (sortKey === 'composite' || sortKey in a.scores) {{
      av = sortKey === 'composite' ? a.scores.composite : a.scores[sortKey];
      bv = sortKey === 'composite' ? b.scores.composite : b.scores[sortKey];
    }} else {{
      av = (a[sortKey] || '').toString().toLowerCase();
      bv = (b[sortKey] || '').toString().toLowerCase();
    }}
    if (av < bv) return -1 * sortDir;
    if (av > bv) return 1 * sortDir;
    return 0;
  }});

  const tbody = document.getElementById('tbody');
  tbody.innerHTML = rows.map((p, idx) => {{
    const s = p.scores;
    const presenter = p.presenter ? escapeHtml(p.presenter) +
      ' <span style="color:var(--fg-faint);font-size:10px;display:block">' +
      escapeHtml(p.presenter_aff || '') + '</span>' : '<span style="color:var(--fg-faint)">—</span>';
    return (
      '<tr class="row-clickable" data-idx="' + idx + '">' +
        '<td class="composite-cell"><span class="score" style="' + colorForScore(s.composite) + '">' +
          s.composite.toFixed(1) + '</span></td>' +
        '<td><span class="track-tag ' + p.track + '">' + p.track + '</span></td>' +
        '<td class="title-cell"><span class="expand-icon"></span>' + escapeHtml(p.title) +
          '<div class="meta">' + escapeHtml(p.session || '') +
          (p.room ? ' · room ' + escapeHtml(p.room) : '') +
          (p.chair ? ' · chair: ' + escapeHtml(p.chair) : '') + '</div></td>' +
        '<td class="author-cell">' + presenter + '</td>' +
        '<td style="white-space:nowrap;font-size:11px;color:var(--fg-dim)">' +
          escapeHtml(p.day || '') + '</td>' +
        '<td><div class="badges">' + badgesFor(p) + '</div></td>' +
        '<td class="score-cell"><span class="score ' + scoreClass(s.novelty) + '">' + s.novelty + '</span></td>' +
        '<td class="score-cell"><span class="score ' + scoreClass(s.identification) + '">' + s.identification + '</span></td>' +
        '<td class="score-cell"><span class="score ' + scoreClass(s.exogenous_shock) + '">' + s.exogenous_shock + '</span></td>' +
        '<td class="score-cell"><span class="score ' + scoreClass(s.ai) + '">' + s.ai + '</span></td>' +
        '<td class="score-cell"><span class="score ' + scoreClass(s.disclosure) + '">' + s.disclosure + '</span></td>' +
        '<td class="score-cell"><span class="score ' + scoreClass(s.timeliness) + '">' + s.timeliness + '</span></td>' +
        '<td class="score-cell"><span class="score ' + scoreClass(s.relevance) + '">' + s.relevance + '</span></td>' +
      '</tr>'
    );
  }}).join('');

  document.getElementById('no-results').style.display = rows.length ? 'none' : 'block';

  // Summary line
  const total = PAPERS.length;
  const showing = rows.length;
  const meanComp = rows.length ? (rows.reduce((a,b) => a + b.scores.composite, 0) / rows.length).toFixed(2) : '—';
  const aiCount = rows.filter(r => r.scores.ai >= 3).length;
  const didCount = rows.filter(r => r.scores.did).length;
  const exoCount = rows.filter(r => r.scores.exogenous_shock >= 3).length;
  document.getElementById('summary').innerHTML =
    '<b>' + showing + '</b> / ' + total + ' papers · ' +
    'mean composite <b>' + meanComp + '</b> · ' +
    'AI <b>' + aiCount + '</b> · DiD <b>' + didCount + '</b> · shock <b>' + exoCount + '</b>';

  // attach row click
  tbody.querySelectorAll('tr.row-clickable').forEach(tr => {{
    tr.addEventListener('click', () => {{
      const idx = +tr.dataset.idx;
      const p = rows[idx];
      const next = tr.nextElementSibling;
      if (next && next.classList.contains('expanded-row')) {{
        next.remove();
        tr.classList.remove('expanded');
        return;
      }}
      // Close any other open row
      tbody.querySelectorAll('tr.expanded-row').forEach(r => r.remove());
      tbody.querySelectorAll('tr.row-clickable.expanded').forEach(r => r.classList.remove('expanded'));
      tr.classList.add('expanded');
      const expanded = document.createElement('tr');
      expanded.className = 'expanded-row';
      const s = p.scores;
      expanded.innerHTML =
        '<td colspan="13">' +
        '<div class="detail-grid">' +
          '<div class="detail-block">' +
            '<h4>Authors</h4>' +
            '<ul>' + authorList(p) + '</ul>' +
          '</div>' +
          '<div class="detail-block">' +
            '<h4>Session</h4>' +
            '<ul style="list-style:none;padding-left:0">' +
              '<li><b>' + escapeHtml(p.session || '') + '</b></li>' +
              '<li>' + escapeHtml(p.day || '') + '</li>' +
              (p.room ? '<li>Room: ' + escapeHtml(p.room) + '</li>' : '') +
              (p.chair ? '<li>Chair: ' + escapeHtml(p.chair) + '</li>' : '') +
              (p.discussant ? '<li>Discussant: ' + escapeHtml(p.discussant) +
                  (p.discussant_aff ? ' (' + escapeHtml(p.discussant_aff) + ')' : '') + '</li>' : '') +
            '</ul>' +
          '</div>' +
          '<div class="detail-block">' +
            '<h4>Composite</h4>' +
            '<div style="font-size:32px;font-weight:700;' + colorForScore(s.composite) +
              ';display:inline-block;padding:6px 14px;border-radius:8px">' +
              s.composite.toFixed(1) + '</div>' +
            '<div style="color:var(--fg-faint);font-size:11px;margin-top:4px">' +
              'Weighted: novelty 1.5×, identification 1.5×, relevance 1.2×, exogenous shock 1.0×' +
            '</div>' +
          '</div>' +
        '</div>' +
        '<h4 style="margin:12px 0 4px;font-size:11px;color:var(--fg-faint);' +
          'text-transform:uppercase;letter-spacing:0.05em">All score dimensions</h4>' +
        '<div class="score-grid">' +
        SCORE_KEYS.map(([k,label]) =>
          '<div class="score-item ' + scoreClass(s[k]) + '">' +
            '<div class="label">' + label + '</div>' +
            '<div class="val">' + s[k] + '</div>' +
          '</div>').join('') +
        '</div>' +
        '</td>';
      tr.parentNode.insertBefore(expanded, tr.nextSibling);
    }});
  }});
}}

function bindEvents() {{
  document.querySelectorAll('#track-chips input, #day-chips input').forEach(i => {{
    i.addEventListener('change', render);
  }});
  ['f-ai','f-did','f-rdd','f-exo','f-ident','f-disc','f-comp'].forEach(id => {{
    document.getElementById(id).addEventListener('change', render);
  }});
  document.getElementById('search').addEventListener('input', () => {{
    clearTimeout(window._sd); window._sd = setTimeout(render, 120);
  }});
  document.querySelectorAll('th[data-sort]').forEach(th => {{
    th.addEventListener('click', () => {{
      const k = th.dataset.sort;
      if (sortKey === k) sortDir = -sortDir;
      else {{ sortKey = k; sortDir = th.dataset.numeric ? -1 : 1; }}
      document.querySelectorAll('th').forEach(t => t.classList.remove('sorted-asc','sorted-desc'));
      th.classList.add(sortDir === 1 ? 'sorted-asc' : 'sorted-desc');
      render();
    }});
  }});
}}

bindEvents();
render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
