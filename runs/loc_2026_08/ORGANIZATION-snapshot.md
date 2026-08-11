<!-- truth-lint: historical -->
# ORGANIZATION — snapshot at completion

*State as it stood when the loc decree closed. Kept as a record; the live `ORGANIZATION.md`
at the repository root is reset between decrees.*

**STATUS:** COMPLETE
**REGISTER:** PLAIN for the whole of the work; flipped to LORE after the report, on the
Creator's word. The decree was executed and reported in the plain register.
**MUSTER:** SKIRMISH
**DECREE:** CLI counting lines of code by file extension in a directory, with tests. 1 cycle.
**CYCLE:** 1 — shipped, QC cleared, deadline met.

---

## Roster

| Handle | Role | Status | Score |
|---|---|---|---|
| DEV-LEAD | Development | ACTIVE | +4 |
| QC-LEAD | Quality Control | ACTIVE | +4 |

A SKIRMISH muster fields Development and QC only. The decree's own text served as the
acceptance criteria, so there was no Business team to write them and no Business gate to
record; packaging folded into Dev's handoff. Two teams, one gate: QC-TRUE.

Each lead scored +2 for a verified first round and +2 for a verified second: Dev for the
build and then the rework, QC for the audit and then the re-audit against the changed hash.
No agent bears a bestowed name — both were seated under the plain register, and names are
granted at Genesis, never in arrears.

## Defect ledger

| Agent | Points | What happened |
|---|---|---|
| — | 0 | none charged to an agent |

## Replacement log

| Cycle | Agent | Cause | Successor |
|---|---|---|---|
| — | — | — | — |

## Gates at close

| Gate | Bound to | Note |
|---|---|---|
| QA-PASS | `fc8849532a176eb4` | `hook-verified: Ran 9, skipped 0` |
| QC-TRUE | `fc8849532a176eb4` | unittest `Ran 9 tests / OK`; pytest `9 passed`; all 9 cases confirmed preserved through the rework; CLI re-exercised in a fresh temp dir |

BIZ-ACCEPT was not required — a SKIRMISH muster puts no Business team on the field, and the
ship gate read the muster correctly and demanded only QC-TRUE.

## The defect this decree, and where it belongs

Charged to the Supreme Leader, not to either agent.

The cycle-1 directive demanded a test suite but never demanded one legible to the enforcement
layer's own runner. Dev wrote pytest function-style tests. The ship-gate hook verifies with
`python3 -m unittest`, which collected zero of them and then wrote `QA-PASS: hook-verified:
Ran 0, skipped 0` — a gate certifying a run that executed nothing, and saying so only in a
note no one was obliged to read.

Neither agent fabricated. Dev's `9 passed` was true under pytest; QC reproduced it; QC's first
audit answered exactly the five claims put in front of it. Neither was positioned to catch a
hole in the dispatch. One rework round converted the suite to `unittest.TestCase`, and both
runners now execute all nine cases.

The lesson is not that the hook was wrong to be strict. It is that a verifier which runs a
different tool than the team runs can return green over nothing, and that failure is silent —
the shape that survives longest. The renamer run showed a fabrication caught after it shipped;
the bigfiles run showed one refused before it reached disk. This run shows the third case: a
gate that passed because it had nothing to fail on.

## Notes

The hash binding earned its keep. Editing `test_loc.py` invalidated QC-TRUE and forced a real
re-audit rather than letting the earlier clearance ride — the re-audit is what confirmed no
case was lost and no assertion weakened in the conversion, which is the actual risk when a
suite is rewritten across frameworks.

One figure moved three times during the cycle and is recorded here so it is never mistaken for
drift. `loc.py` run against its own deliverables directory printed `TOTAL 2 273` when Dev ran
it, `TOTAL 3 329` once `qc-audit.md` landed beside it, and `TOTAL 3 391` after the rework grew
the suite and QC appended the re-audit. Nothing was misreported at any point. A tool that
counts a directory reports a different total when the directory changes, and this directory
changed three times — which makes the tool a poor thing to quote as a constant, including in
this file.

`qc-audit.md` carries an appended correction: §1 states line counts one too high for both
files. It is recorded there rather than edited away, and it was not charged.
