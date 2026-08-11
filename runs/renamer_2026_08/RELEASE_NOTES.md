<!-- truth-lint: historical -->
# renamer — Release Notes (Cycle 3)

## What Ships

- `deliverables/renamer.py` — batch file/directory renaming CLI, Python 3.11
  stdlib only, per `requirements.md` §2–§8.
- `deliverables/test_renamer.py` — `unittest` acceptance suite covering
  criteria 2–18, 19, 20 (requirements.md §11).
- `deliverables/README.md` — flag reference, pattern/template semantics,
  exit codes, worked example for each collision mode (skip/fail/overwrite).

## Observed Test Result

Command run from `/home/user/TRY-SL`:

```
python3 -m unittest deliverables.test_renamer -v
```

Output (tail):

```
----------------------------------------------------------------------
Ran 26 tests in 0.037s

OK (skipped=1)
```

Re-confirmed after Development's QC-02 fix landed (dry-run now tracks
in-plan destination collisions, not just on-disk ones): QA added four
intra-run collision regression tests and unskipped criterion 16,
26 tests, `OK (skipped=1)`.

26 tests total: 25 pass, 1 skipped (criterion 18, see below).
Criterion 19 (`test_criterion_19_readme_documents_flags_and_collision_modes`)
passes now that `README.md` exists.

## Known Limitations

- **Criterion 16 (idempotence) — asserted and passing, non-self-matching
  templates only.** Business amended §11.16 (Cycle 3) to scope the
  criterion to pattern/template pairs where the output does not itself
  match `--pattern` (e.g. `--pattern "*.txt" --template "{name}.done"`).
  `test_criterion_16_idempotent_rerun_non_self_matching` exercises exactly
  this pair and passes: run 1 renames `x.txt` → `x.done` (exit 0), run 2
  with identical args finds zero matches (`x.done` no longer satisfies
  `*.txt`) and exits 4, directory listing unchanged from after run 1. Per
  the amended §11.16, self-matching pairs (e.g. `--pattern "*.txt"
  --template "{name}_x{ext}"`) are explicitly excluded and are
  non-idempotent by design — a second run re-matches the first run's own
  output and renames again (`a_x.txt` → `a_x_x.txt`), which is expected
  behavior, not a defect.
- **Criterion 18 (permission-denied → exit 3) — UNVERIFIED, environment
  constraint.** This test suite executes as `uid=0` (root). `os.chmod(0o444)`
  does not block root's write/rename access on Linux, so the permission-denied
  path cannot be triggered or observed in this environment, per the
  criterion's own "run as non-root" precondition. Test is marked `skipTest`
  with the reason recorded inline.

Criterion 18 remains a pre-existing condition of the test environment, not
a defect introduced this cycle. No pass rate is claimed for it; it is
reported honestly as UNVERIFIED.
- **Dry-run exit code does not always predict the real run's, under `skip`.**
  Per spec §4 as written, `--dry-run` exits 1 for any planned collision
  regardless of `--on-collision` policy (confirmed: `--on-collision skip
  --dry-run` on a colliding pair exits 1), while the real run under
  `--on-collision skip` resolves the same collision by skipping and exits 0.
  This is spec-conformant, not a bug, but dry-run's exit code should not be
  read as a preview of the real run's exit code when policy is `skip`.

## Not in Scope

Per requirements.md §9 (WON'T): rollback/transaction log, regex patterns,
GUI/config/plugins, cross-platform case normalization, overwrite-onto-directory
collision handling, network paths. Logged, not silently dropped.
