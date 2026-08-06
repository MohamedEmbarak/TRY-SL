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
Ran 22 tests in 0.040s

OK (skipped=2)
```

22 tests total: 20 pass, 2 skipped (criteria 16 and 18, see below).
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

## Not in Scope

Per requirements.md §9 (WON'T): rollback/transaction log, regex patterns,
GUI/config/plugins, cross-platform case normalization, overwrite-onto-directory
collision handling, network paths. Logged, not silently dropped.
