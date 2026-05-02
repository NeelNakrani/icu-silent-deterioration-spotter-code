# Competition Submission Reference
## IBM Dev Day: Bob Edition — Hackathon

> Non-technical reference sheet. Keep this open during build and especially at submission time.

---

## Event Overview

| Field | Detail |
|---|---|
| **Event Name** | IBM Dev Day: Bob Edition |
| **Format** | Free virtual event + hackathon |
| **Main Event Date** | April 30, 2026 — 11:00 AM ET (dev talks + IBM expert sessions) |
| **Hackathon Window** | April 30 – May 3, 2026 (48-hour build after kickoff) |
| **Platform** | lablab.ai + lablab.ai Discord server |
| **Team Format** | Solo or team |
| **Cost** | Free to enter |

**Sources:**
- [IBM Community Event Page](https://community.ibm.com/community/user/events/event-description?CalendarEventKey=97a695cd-87b1-4b30-9841-019dc786ba71&CommunityKey=c9e80780-a8b2-4c57-b14f-019c1012c744)
- [IBM Bob Dev Day Hackathon (IBM Developer)](https://developer.ibm.com/events/ibm-bob-dev-day-hackathon/)
- [Eventbrite Listing](https://www.eventbrite.com/e/ibm-dev-day-bob-edition-tickets-1986269038162)
- [Hackathon.com Listing](https://www.hackathon.com/event/ibm-dev-day-bob-edition-69cad69ef75f3c59945bcbfd)

---

## Prizes

| Place | Prize |
|---|---|
| **1st Place** | Up to $5,000 USD |
| **Total Pool** | $10,000 USD |
| **Distribution Timeline** | Up to 90 days after competition ends |

---

## Judging Criteria

These are the four axes judges score on. Map every demo and submission decision back to these:

1. **Completeness & Application of IBM Bob**
   - Is the project finished and polished?
   - Is IBM Bob genuinely central to the solution — not bolted on?
   - *Our angle: Three parallel Bob agents + coordinator synthesis is architecturally what Bob was built for.*

2. **Clarity & Effectiveness of Presentation**
   - Is the demo video clear? Does it tell a story?
   - Does a non-technical judge understand the problem and solution in 90 seconds?
   - *Our angle: Real MIMIC-IV patient who deteriorated and coded — "your system would have flagged this 3 hours earlier."*

3. **Impact & Practical Value**
   - Does it solve a real, high-priority problem?
   - Is the value quantifiable?
   - *Our angle: 1.75M nurses, 300M handoffs/year, #1 cause of preventable adverse events.*

4. **Uniqueness & Creativity**
   - Is the approach novel?
   - Is IBM Bob being used in a way others aren't?
   - *Our angle: Trajectory-based risk scoring (not snapshot), concurrent specialized reasoners, expandable reasoning chains.*

---

## Submission Rules (Critical)

- [ ] Project must use **IBM Bob** in a meaningful, demonstrable way — projects without clear Bob usage may be **disqualified**
- [ ] Submission must be **original work** produced during the hackathon window
- [ ] Code license must be **MIT-compliant**
- [ ] Demo video is required
- [ ] Submit on **lablab.ai** platform

---

## What to Include in the Submission Write-Up

Write these sections for the lablab.ai submission form:

1. **Problem Statement** — The information gap at ICU shift handoff. 1.75M nurses, 300M handoffs/year, communication failure is the #1 cause of preventable adverse events. Existing tools (SBAR/I-PASS) capture state, not trajectory.

2. **Solution** — ICU Silent Deterioration Spotter: three IBM Bob agents running in parallel (Trend Agent, Lab-Vitals Conflict Agent, Time Bomb Agent), synthesized into a single-page SBAR+ pre-handoff brief per patient.

3. **How IBM Bob is Used** — Multi-agent parallel orchestration via Bob (not sequential chaining). Coordinator agent merges outputs. BobShell provides full auditability — every flag is traceable to specific data points and reasoning steps.

4. **Data** — MIMIC-IV (real deidentified ICU data from Beth Israel Deaconess Medical Center, publicly available via PhysioNet).

5. **Impact** — Catches silent deterioration patterns (compensated shock, early AKI, pre-respiratory failure) invisible in raw numbers. Flags patients 2–3 hours before coding events.

---

## IBM Bob — Key Facts to Cite

- IBM Bob is an AI-first development partner for the full SDLC
- Multi-model orchestration: Claude, Mistral, IBM Granite + specialized fine-tuned models
- **BobShell**: CLI that makes every agentic action self-documenting and traceable
- Role-based specialized agents + governed workflows
- [Official IBM Bob page](https://bob.ibm.com/)
- [IBM Bob Press Release](https://newsroom.ibm.com/2026-04-28-introducing-ibm-bob-ai-development-partner-that-takes-enterprises-from-ai-assisted-coding-to-production-ready-software)

---

## Demo Video Checklist

- [ ] Opens with the problem — "The patient looked fine at handoff. Two hours later they coded."
- [ ] Shows a real MIMIC-IV patient stay
- [ ] Shows the 3 agents running (ideally visually/concurrently)
- [ ] Shows the SBAR+ brief output — color-coded risk, reasoning chain
- [ ] Reveals that this patient coded 2–3 hours later in the real record
- [ ] Under 3 minutes total (90-second money shot is the flag-vs-real-outcome reveal)

---

## Key Links to Bookmark

- [IBM Bob](https://bob.ibm.com/)
- [lablab.ai Hackathon Page](https://lablab.ai/ai-hackathons/ibm-bob-hackathon)
- [IBM Dev Day Main Event](https://ibmdevday-bob.bemyapp.com/)
- [MIMIC-IV on PhysioNet](https://physionet.org/content/mimiciv/latest/)
- [lablab.ai Discord](https://discord.gg/lablab-ai) *(join before April 30)*
