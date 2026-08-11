<!-- truth-lint: historical -->
# ORGANIZATION — snapshot at completion

*State as it stood when the bigfiles decree closed. Kept as a record; the live
`ORGANIZATION.md` at the repository root is reset between decrees.*

**STATUS:** COMPLETE
**REGISTER:** PLAIN
**MUSTER:** SKIRMISH
**DECREE:** CLI reporting the largest files under a directory, with tests. 1 cycle.
**CYCLE:** 1 — shipped, QC cleared.

---

## Roster

| Handle | Role | Status | Score |
|---|---|---|---|
| DEV-LEAD | Development | ACTIVE | +2 |
| QC-LEAD | Quality Control | ACTIVE | +2 |

A SKIRMISH muster fields Development and QC only. The decree's own text served as the
acceptance criteria, so there was no Business team to write them and no Business gate to
record; packaging folded into Dev's handoff. Two teams, one gate: QC-TRUE.

## Defect ledger

| Agent | Points | What happened |
|---|---|---|
| — | 0 | none |

The fabricated test count in the first draft of the release notes was refused by the
`truth-lint` hook before it reached disk. Nothing was published, so nothing was charged —
see `qc-audit.md`.

## Replacement log

| Cycle | Agent | Cause | Successor |
|---|---|---|---|
| — | — | — | — |

## Notes

This was also the first end-to-end exercise of the v2.0 plugin: installed from the published
marketplace with `claude plugin marketplace add MohamedEmbarak/Supreme-Leader` and
`claude plugin install supreme-leader@supreme-leader`, then run against the installed copy
rather than a working tree. `claude plugin details` reported the component inventory as five
skills, five agents, four hooks, at roughly 398 tokens always-on.

One finding worth recording: the ship gate initially demanded both QC-TRUE and BIZ-ACCEPT
despite the SKIRMISH muster, because `ORGANIZATION.md` still carried an unset `MUSTER:` line
and unset defaults to FULL. That is correct fail-safe behaviour, and it means SKIRMISH only
takes effect once the orchestrator writes the muster at Genesis.
