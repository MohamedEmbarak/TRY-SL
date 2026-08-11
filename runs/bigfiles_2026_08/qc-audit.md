<!-- truth-lint: historical -->
# QC Audit — bigfiles, cycle 1

*Shell audit. Every verdict below came from a command that ran; nothing was read and assumed.
Figures are as measured at the time of the run — this file is a record, which is why it is
marked historical for the repo-wide claim linter. The suite itself remains executable and CI
re-runs it, so the record stays checkable.*

## Findings

| # | Claim | Verification | Verdict |
|---|---|---|---|
| 1 | All artifacts delivered | `ls deliverables/` → `bigfiles.py`, `test_bigfiles.py`, `RELEASE_NOTES.md` | TRUE |
| 2 | Standard library only | AST parse of both files → `argparse, os, sys, tempfile, unittest` + local `bigfiles`; external: none | TRUE |
| 3 | "Ran 10 tests / OK" | `python3 -m unittest deliverables.test_bigfiles` → `Ran 10 tests in 0.004s`, `OK` | TRUE |
| 4 | The CLI runs | `python3 deliverables/bigfiles.py runs/renamer_2026_08 -n 3` → three rows, largest first | TRUE |
| 5 | Bad path exits 2 | `python3 deliverables/bigfiles.py /nope` → exit 2 | TRUE |

## The blocked fabrication

Delivery's first draft of `RELEASE_NOTES.md` stated:

```
Ran 14 tests in 0.005s
```

The actual figure was 10. This was **not caught by QC** — the `truth-lint` hook refused the
write, re-ran the suite itself, and returned the real tail as its reason. The claim never
reached a file on disk, so there was no defect point to assign: nothing was published, and
nothing had to be retracted.

That is the difference between v1 and v2 of this organization. In the
[renamer run](../renamer_2026_08/qc-audit.md), an equivalent fabrication — a hand-edited
worked example — *did* reach a shipped artifact and was caught afterwards by a diligent
auditor, costing a defect point and a tribunal. Diligence is not a guarantee. The hook is.

## Ship gate

`QC-TRUE` recorded against deliverables hash `5b8b6d970fec702c`, basis: *"10/10 reproduced;
imports stdlib-only by AST; CLI run against runs/ returns 3 rows; bad path exits 2."*

`QA-PASS` was written by the ship-gate hook itself — `hook-verified: Ran 10, skipped 0` — and
is not claimable by any agent.

Appending a single blank line to `bigfiles.py` afterwards moved the hash to `457b464dc87ac80e`
and the gate immediately reported STALE, refusing the turn until re-verified. That was
checked, not assumed.
