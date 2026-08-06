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

---

## Cycle 3 RE-AUDIT (post-rework)

### QC-01 re-check — all 6 README blocks executed verbatim

Command per block, scratch dirs mirroring README's own setup (`/tmp/.../qc-readme-recheck`): `-h`, basic rename, `--dry-run`, `fail`, `skip`, `overwrite`.

| Block | Observed | Matches README byte-for-byte? |
|---|---|---|
| `-h` | full usage text | YES |
| basic | `exit=0`; `a_x.txt b_x.txt c.md` | YES |
| dry-run | 2x `DRY-RUN:` lines, `exit=0`, dir unchanged | YES |
| fail | `ERROR: collision at fail/b.renamed`, `EXIT=3` | YES — path prefix fixed (was `./b.renamed`) |
| skip | `SKIP: skip/b.txt (target exists)`, `EXIT=0` | YES — path prefix fixed (was `./b.txt`) |
| overwrite | `exit=0`, `b.renamed`→`NEW-CONTENT` | YES |

**QC-01: RESOLVED.** Delivery's re-capture is accurate.

### QC-02 re-check — dry-run + all three policies, in-batch (two-source-same-destination) collision

Command: `renamer.py --pattern "*.txt" --template "same.txt" --path <dir> [--dry-run] [--on-collision skip|overwrite]`, sources `a1.txt`,`a2.txt`.

| Mode | Observed exit | Verdict |
|---|---|---|
| dry-run, default(fail) | 1 | correct (was 0 before fix) |
| dry-run, skip | 1 | correct — matches new RELEASE_NOTES caveat |
| dry-run, overwrite | 1 | correct |
| real, fail | `ERROR: collision at r1/same.txt`, exit 3 | correct |
| real, skip | `SKIP: r2/a2.txt (target exists)`, exit 0 | correct |
| real, overwrite | exit 0, only `same.txt` remains | correct |

**QC-02: RESOLVED.** `execute_plan()`'s `claimed` set now catches intra-run destination collisions under dry-run and all three policies.

### Test-count claim — "Ran 26 tests / OK (skipped=1)"

Command: `python3 -m unittest deliverables.test_renamer -v`
Observed: `Ran 26 tests in 0.058s` / `OK (skipped=1)`. 25 `ok` + 1 `skipped` (criterion 18 only — criterion 16 is now `test_criterion_16_idempotent_rerun_non_self_matching ... ok`, no longer skipped). 4 new `test_regression_intra_run_conflict_*` tests present and passing.

**Verdict: TRUE.** Matches exactly.

### RELEASE_NOTES.md figures and new caveat

Command: `grep -n "22 tests\|26 tests\|skipped=1\|skipped=2\|Ran " deliverables/RELEASE_NOTES.md`

Observed: RELEASE_NOTES.md lines 24, 26, 31, 33 still read **"Ran 22 tests in 0.026s" / "OK (skipped=2)" / "22 tests, OK (skipped=2)" / "22 tests total: 20 pass, 2 skipped (criteria 16 and 18)"** — unchanged from the pre-rework version. The "Known Limitations" section still lists criterion 16 as unverified/skipped, contradicting the test suite I just ran, where criterion 16 is unskipped and passing.

**Finding QC-03 (FALSE, stale/incorrect figures):** RELEASE_NOTES.md's test-count section was not updated after QA's rework (26 tests actual vs. 22 claimed; skipped=1 actual vs. skipped=2 claimed; criterion 16 falsely still described as skipped/UNVERIFIED). This is the exact figure the Creator would read to judge test coverage — it is currently wrong.

The new dry-run/skip exit-code caveat (RELEASE_NOTES.md lines 59–65: "dry-run exits 1 under `--on-collision skip` on a colliding pair while the real run exits 0") **was independently reproduced above under QC-02 and is TRUE.**

### Final verdict

**NOT CLEARED TO SHIP.** Blocking claim: RELEASE_NOTES.md's stale test-count ("22 tests / OK (skipped=2)", 4 occurrences) contradicts the actual, independently-reproduced result ("26 tests / OK (skipped=1)") — QC-03. QC-01 and QC-02 are both RESOLVED and verified by command. No soul named for QC-03 pending Supreme Leader attribution — RELEASE_NOTES.md carries no byline.

---

## QC-03 CLOSURE CHECK

Commit `1970455` ("Refresh release-note test figures to the current suite (QC-03)") re-read via `git show 1970455 -- deliverables/RELEASE_NOTES.md`: 5 diff hunks, all inside "Observed Test Result" — `Ran 22→26 tests`, `skipped=2→1`, the re-confirmed sentence, and the `22→26 tests total... 2→1 skipped` sentence. No other section touched (confirmed by diff scope — What Ships, Pattern semantics, Not in Scope untouched).

Fresh suite run, this session: `python3 -m unittest deliverables.test_renamer -v` → `Ran 26 tests in 0.030s` / `OK (skipped=1)`; `test_criterion_16_idempotent_rerun_non_self_matching ... ok` (not skipped); `test_criterion_18_permission_denied ... skipped`. The four figures now match this run exactly.

**Finding QC-04 (FALSE, stale line left behind):** RELEASE_NOTES.md "Known Limitations" bullet 1 (lines 40–49) still reads: *"Criterion 16 (idempotence) — UNVERIFIED... Test is marked `skipTest`, not asserted true or false."* This is no longer true — criterion 16 passes (`ok`) in the suite I just ran, and it directly contradicts the document's own corrected line 34 ("26 tests total: 25 pass, 1 skipped (**criterion 18**, see below)"), which already excludes criterion 16 from the skip count. The QC-03 commit fixed the summary figures but did not remove/rewrite the now-false criterion-16 limitation paragraph — a leftover self-contradiction within the same file.

### Final verdict

**NOT CLEARED TO SHIP.** Blocking claim: RELEASE_NOTES.md lines 40–49 (Known Limitations, criterion 16) still assert criterion 16 is skipped/UNVERIFIED — false, per `python3 -m unittest deliverables.test_renamer -v` run this session, and inconsistent with the document's own line 34. QC-01, QC-02, and the four QC-03 figures are all verified TRUE and RESOLVED; this one stale paragraph is the sole remaining blocker.

---

## QC-04 FINAL CLEARANCE CHECK

**1. Criterion-16 bullet factual claims — run 1 / run 2 reproduced manually:**
`touch x.txt`; run 1: `python3 renamer.py --pattern "*.txt" --template "{name}.done" --path .` → exit=0, `x.txt`→`x.done`. Run 2, identical args: `NOTICE: no files matched`, exit=4, dir listing unchanged (`x.done` only). Matches the bullet's description exactly. Test suite: `test_criterion_16_idempotent_rerun_non_self_matching ... ok` (not skipped) in `python3 -m unittest deliverables.test_renamer -v`. **TRUE.**

**2. requirements.md §11.16 attribution:** `grep -n "^16\." -A9 deliverables/requirements.md` → text matches the bullet's paraphrase (same example pair `--pattern "*.txt" --template "{name}.done"`, exit 0 / exit 4, self-matching pairs e.g. `{name}_x{ext}` explicitly excluded). `git log --oneline -- deliverables/requirements.md` → commit `9696e3a` "Amend requirements.md criterion 16 to the non-self-matching template case" (message: "Business tightens criterion 16"), confirming the bullet's "Business amended §11.16 (Cycle 3)" claim. **TRUE.**

**3. Criterion 18 bullet + no other stale claim:** Full run confirms `test_criterion_18_permission_denied ... skipped 'UNVERIFIED: test process is root (uid=0); os.chmod-based write-protection does not block root, so exit-3-on-permission-error cannot be exercised in this environment.'` — verbatim match to the bullet text. `git log --oneline -- deliverables/renamer.py` shows no commits after the QC-02 fix (`05191a6`), so the dry-run/skip caveat (verified by command in the prior audit round) still holds unchanged. Re-read full file top to bottom: "What Ships", test-count sentences (26/25/1, matches run below), criterion 19 pass claim, and "Not in Scope" all consistent with current suite/code state. No other stale claim found. **TRUE.**

**4. Final full suite run:** `python3 -m unittest deliverables.test_renamer -v` → `Ran 26 tests in 0.031s` / `OK (skipped=1)`. Matches RELEASE_NOTES.md exactly.

### Final verdict

**CLEARED TO SHIP.** All four re-audit rounds (QC-01, QC-02, QC-03, QC-04) independently reproduced by command this session. No open finding remains.
