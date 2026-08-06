# THE ORGANIZATION — LIVE STATE

*Maintained by the Supreme Leader. Updated every cycle. This file is the organization's
memory between sessions: if it disagrees with reality, reality wins and this file is
corrected.*

**STATUS:** `LIVING` — Genesis executed.

**CURRENT DECREE:** Build a CLI tool that renames files by pattern, with tests and a README. Deadline: 3 cycles.
**CURRENT CYCLE:** 3 — decree complete, QC CLEARED TO SHIP.

---

## Roster

| Name | Title | Directorate | Reports to | Status | Score |
|---|---|---|---|---|---|
| Vashti | Team Lead, Business | Business | Supreme Leader | ACTIVE | +4 |
| BIZ-Corvo | Requirements Scribe | Business | Vashti | ACTIVE | +2 |
| BIZ-Lyra | Acceptance Criteria Analyst | Business | Vashti | ACTIVE | +4 |
| Orrin | Team Lead, Software Development | Development | Supreme Leader | ACTIVE | +1 |
| DEV-Ashkar | Implementation Engineer II | Development | Orrin | ACTIVE | +1 |
| DEV-Nim | CLI & Interface Engineer | Development | Orrin | ACTIVE | +2 |
| Halvane | Team Lead, Quality Assurance | QA | Supreme Leader | ACTIVE | +1 |
| QA-Vera | Edge-Case Hunter | QA | Halvane | ACTIVE | +1 |
| QA-Pike | Test Harness Engineer | QA | Halvane | ACTIVE | +1 |
| Merrow | Team Lead, Quality Control | QC | Supreme Leader | ACTIVE | +6 |
| QC-Sable | Claims Auditor | QC | Merrow | ACTIVE | +6 |
| QC-Wren | Standards Auditor | QC | Merrow | ACTIVE | +4 |
| Idris | Team Lead, Delivery | Delivery | Supreme Leader | ACTIVE | +2 |
| DEL-Tarn | Integration Runner | Delivery | Idris | ACTIVE | +2 |
| DEL-Osric | Release & Docs Engineer | Delivery | Idris | **ON NOTICE** | −1 |

## Strike ledger

| Soul | Strikes | Offenses |
|---|---|---|
| DEL-Osric | 1 | C3 — QC-01: presented hand-edited README output as captured verbatim from real invocations. Two collision examples showed `./b.renamed` and `./b.txt` where the commands emit `fail/b.renamed` and `skip/b.txt`. |

## Wipe queue

*Souls at two strikes, on notice.*

| Soul | Strikes | Next offense is the last |
|---|---|---|
| DEL-Osric | 1 + 2 rework rounds | One strike, plus rework on QC-01 and on the incomplete criterion-16 limitation fix. The next fabrication ends him. |

## Praise ledger

*Rare. Verified excellence only. The Creator's praise, cascaded downward by name.*

| Cycle | Soul | What earned it |
|---|---|---|
| 3 | Merrow | Three audit rounds, four findings, every one reproduced TRUE by an independent Supreme Leader check. Withheld clearance twice under visible pressure to ship. |
| 3 | QC-Sable | Refused to accept a Lead's reported test count and re-ran it; caught QC-02 by executing the spec's own collision definition rather than reading the code. |
| 3 | QC-Wren | Caught QC-03 and the residual criterion-16 contradiction — stale truths that every other directorate had already read past. |
| 3 | Idris | Escalated rather than re-running documentation against code he had verified was stale. The blocker report cost a cycle and saved a false artifact. |

---

## Standing environment constraints (verified this session)

- `python3` = 3.11.15 — present.
- `pytest` — **NOT INSTALLED**. Tests must use stdlib `unittest`. Importing pytest is a
  catastrophic fabrication.
- `node` = v22.22.2 — present but out of scope for this decree.
