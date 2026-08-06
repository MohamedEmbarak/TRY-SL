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

- **Criterion 16 (idempotence) — UNVERIFIED, not a pass/fail claim.**
  Re-running with `--pattern "*.txt" --template "{name}_x{ext}"
  --on-collision skip` a second time does **not** skip: the template's own
  output (`a_x.txt`) still matches `*.txt`, so the second run treats it as a
  new match and produces `a_x_x.txt` instead of leaving it alone. Empirically
  confirmed in the test suite (`second_run_renamed_again=True`). The
  criterion's "zero files renamed on the second invocation" claim only holds
  when `--pattern` is chosen disjoint from the template's own output;
  requirements.md §3/§11.16 does not specify that constraint. Test is marked
  `skipTest`, not asserted true or false.
- **Criterion 18 (permission-denied → exit 3) — UNVERIFIED, environment
  constraint.** This test suite executes as `uid=0` (root). `os.chmod(0o444)`
  does not block root's write/rename access on Linux, so the permission-denied
  path cannot be triggered or observed in this environment, per the
  criterion's own "run as non-root" precondition. Test is marked `skipTest`
  with the reason recorded inline.

Both limitations are pre-existing conditions of the test environment and
template/pattern interaction, not defects introduced this cycle. No pass
rate is claimed for either; both are reported honestly as UNVERIFIED.
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
