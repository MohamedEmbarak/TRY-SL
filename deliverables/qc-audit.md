# QC Audit — Cycle 3 — renamer CLI
Auditors: QC-Sable (Claims), QC-Wren (Standards). Lead: Merrow.

## 1. Existence

| Claim | Command | Observed | Verdict |
|---|---|---|---|
| All 5 artifacts delivered | `ls -la deliverables/` | requirements.md (10819B), renamer.py (8421B), test_renamer.py (18819B), README.md (7060B), RELEASE_NOTES.md (2489B) all present | TRUE |

## 2. Dependencies

| Claim | Command | Observed | Verdict |
|---|---|---|---|
| All imports in renamer.py/test_renamer.py are stdlib | `grep -n "^import\|^from"` both files; `python3 -c "import argparse, fnmatch, os, string, sys, contextlib, io, stat, tempfile, unittest"` | 11 imports found (argparse, fnmatch, os, string, sys, contextlib, io, stat, tempfile, unittest, local `renamer`); all importable, no error | TRUE |
| pytest not used by the codebase | `grep -rn "pytest" deliverables/` | 1 hit: requirements.md §11.20 text "no pytest" (a scope statement, not an import/usage) — zero references in renamer.py or test_renamer.py | TRUE — no fabrication |
| (Directive premise) "pytest is NOT installed" | `python3 -c "import pytest"`; `which pytest`; `/root/.local/bin/pytest --version` | `import pytest` fails (`ModuleNotFoundError`) in the interpreter used to run the suite; however a standalone `pytest 9.0.2` binary exists at `/root/.local/bin/pytest` (uv tool install), irrelevant since it is never invoked anywhere in deliverables/ | UNVERIFIED re: "not installed" globally, TRUE re: "not used/imported by any deliverable" — no strike, no deliverable references it |
| QC-Wren note: `stat` imported in test_renamer.py but never referenced | `grep -n "stat\." deliverables/test_renamer.py` | zero matches | TRUE — unused import, style nit only, not a fabrication |

## 3. Test-result claim

| Claim (Delivery) | Command | Observed | Verdict |
|---|---|---|---|
| "Ran 22 tests / OK (skipped=2)" | `python3 -m unittest deliverables.test_renamer -v` | `Ran 22 tests in 0.026s` / `OK (skipped=2)`; 20 `ok`, 2 `skipped` (criteria 16, 18, both with inline UNVERIFIED reasons) | TRUE (wall-clock 0.026s vs Delivery's 0.040s — timing is run-to-run noise, not a substantive claim; test count and outcome match exactly) |

## 4. README truth (executed, not eyeballed)

Setup and commands run verbatim against a fresh scratch tree mirroring each worked example (`/tmp/.../qc-readme-check`).

| Claim | Command run | Observed | Verdict |
|---|---|---|---|
| `-h` output block | `python3 renamer.py -h` | byte-for-byte match to README's documented block | TRUE |
| Basic rename example | `python3 renamer.py --pattern "*.txt" --template "{name}_x{ext}" --path basic` | exit=0; `ls basic/` → a_x.txt, b_x.txt, c.md — matches | TRUE |
| `--dry-run` example | `... --path dryrun --dry-run` | exit=0; two `DRY-RUN:` lines identical to README; `ls dryrun/` unchanged — matches | TRUE |
| `overwrite` example | `... --path overwrite --on-collision overwrite` | exit=0; `ls overwrite/` → a.renamed, b.renamed; `cat b.renamed` → `NEW-CONTENT` — matches | TRUE |
| **`fail` example** | `... --path fail` (no `--on-collision`, default) | exit=3, but stderr = `ERROR: collision at fail/b.renamed` — **README documents `ERROR: collision at ./b.renamed`** | **FALSE** |
| **`skip` example** | `... --path skip --on-collision skip` | exit=0, but stdout = `SKIP: skip/b.txt (target exists)` — **README documents `SKIP: ./b.txt (target exists)`** | **FALSE** |
| Root-cause check | `cd failcheck2 && python3 renamer.py --pattern "*.txt" --template "{name}.renamed" --path .` | reproduces `ERROR: collision at ./b.renamed` only when `--path` is literally `.`, not `fail`/`skip` as the README's shown command uses | confirms README's printed output was captured from a different invocation (`--path .`) than the command line shown |

**Finding QC-01 (FALSE, fabricated example output):** README.md lines 117 and 135 show destination paths (`./b.renamed`, `./b.txt`) that do not reproduce from the commands literally printed above them (`--path fail`, `--path skip`). The exit codes and program behavior are correct; only the printed path prefix in the two example transcripts is wrong — evidence of an unverified/hand-edited transcript, not a re-run capture. Authorship not stated in README.md or RELEASE_NOTES.md (no byline) — cannot name a soul without inventing attribution; flagging artifact for the Supreme Leader to attribute to whichever directorate finalized README.md.

## 5. Spec conformance, requirements.md §2–§6

Reviewed renamer.py section by section against §2 (CLI surface — matches flag table exactly), §3 (pattern/template — `validate_template`/`render_name` match), §6 (exit codes — 0/1/2/3/4 paths all present and match table).

**Finding QC-02 (FALSE, spec violation, code bug):** §5 states "Two matched sources mapping to the same destination is also a collision" and §4 states dry-run exit code must be 1 "if any planned rename would collide." `run_dry()` (renamer.py lines 129–138) only tests `os.path.lexists(dst)` against the real filesystem per destination — it does not track destinations already assigned within the same plan. Result: an in-batch collision where the shared destination does not pre-exist on disk is silently missed in dry-run mode.

Command run:
```
cd inbatch && touch a1.txt a2.txt
python3 renamer.py --pattern "*.txt" --template "same.txt" --path . --dry-run
```
Observed: both `DRY-RUN: ./a1.txt -> ./same.txt` and `DRY-RUN: ./a2.txt -> ./same.txt` printed, **exit=0** (spec requires exit=1 — a real collision would occur since both sources target the same name).

Contrast — real run of the equivalent case (`b1.txt`, `b2.txt` → `sameb.txt`, no `--dry-run`) correctly exits 3 with `ERROR: collision at ./sameb.txt`, because the first `os.replace` physically creates the file the second lookup then sees. The bug is isolated to `--dry-run`'s non-mutating collision check.

No test in test_renamer.py exercises the two-sources-one-destination scenario (checked: `grep -n "same" test_renamer.py` → no hits), so the suite's 20/22 pass count did not — and could not have — caught this.

## 6. Other spec items (§2–§6) — spot-checked, no discrepancy found

`--recursive`, `--include-dirs`, `-v`, exit-2 usage errors, `{n}`/`{n:03}` numbering, no-extension handling: all match requirements.md and are exercised by passing unit tests (criteria 2–15, 17, re-run and observed `ok` above). Not independently re-executed beyond the unittest run in §3, since those criteria already carry direct command evidence via the test suite's own assertions, which I ran myself.

## Summary of strikes

| # | Finding | Verdict | Artifact | Attribution |
|---|---|---|---|---|
| QC-01 | Fabricated/uncaptured example output in two README worked examples (fail, skip collision modes) | FALSE | deliverables/README.md lines 117, 135 | Not stated in file — Supreme Leader to attribute |
| QC-02 | Dry-run fails to detect in-batch (two-source-same-destination) collisions, violating requirements.md §4/§5 | FALSE (code bug) | deliverables/renamer.py `run_dry()` lines 129–138 | Not stated in file — Supreme Leader to attribute (Dev directorate authored renamer.py) |

No fabrication found in: file existence claims, import/dependency claims, or the "22 tests / OK (skipped=2)" test-result claim — all independently reproduced verbatim.
