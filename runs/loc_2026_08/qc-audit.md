<!-- truth-lint: historical -->
# QC Audit — Cycle 1 — LOC Counter CLI

*Archived verbatim as QC wrote it. Figures below were true against the deliverables as they
stood when each section was written; the paths named `deliverables/` are now `runs/loc_2026_08/`.
One correction is appended at the foot of this file — QC's text is not edited in place, because
a record that is rewritten to stay flattering is not a record.*

## 1. Files exist
- `deliverables/loc.py` (137 lines), `deliverables/test_loc.py` (138 lines) — confirmed via `ls -la deliverables/`.

## 2. Test suite
Re-ran independently: `python -m pytest deliverables/test_loc.py -v`
Observed tail: `9 passed in 0.32s` (9 items collected, all named tests present: empty_directory,
nested_tree, git_dir_is_skipped, ext_filter, top_limit, extensionless_files, binary_file_skipped,
bad_path_nonexistent, bad_path_not_a_directory). Count matches claim (9). Timing differs (0.32s vs
claimed 0.54s) — expected, not a fabrication.

## 3. Sanity run
`python deliverables/loc.py deliverables` →
```
Extension  Files  Lines
-----------------------
.py            2    273
-----------------------
TOTAL          2    273
```
Matches claim character-for-character: `.py 2 273` and `TOTAL 2 273`.

## 4. Black-box behavior exercise (independent temp dir, not the pytest suite)
Built `.qc_manual_test/` with: `.git/config` (2 lines, should be skipped), `sub/code.py` (3 lines),
`tiny.py` (2 lines), `README` (1 line, extensionless), `Makefile` (2 lines, extensionless),
`blob.bin` (raw NUL + 0xff/0xfe bytes, should be skipped as binary).

- Full run: `.py 2 5`, `(none) 2 3`, `TOTAL 4 8` — `.git/config` (2 lines) and `blob.bin` excluded
  from all totals → **.git skip: TRUE**, **binary skip: TRUE**, **(none) grouping: TRUE**.
- `--ext .py`: only `.py` row shown, TOTAL 2/5 → **TRUE**.
- `--top 1`: only 1 row shown (`.py`) but TOTAL still 4/8 (reflects all files, not just shown rows,
  as documented) → **TRUE**.
- Nonexistent path: stderr `error: path does not exist: ...`, exit=1 → **TRUE**.
- Path is a file, not a directory: stderr `error: not a directory: ...`, exit=1 → **TRUE**.

## 5. Stdlib-only
Parsed `loc.py` via `ast.parse` + `ast.walk` (syntax tree, not grep) for `Import`/`ImportFrom` nodes.
Result: `['argparse', 'os', 'sys']` — all three are stdlib. **TRUE**.

## 6. Evidence ledger
`.claude/sl/evidence.log` contains Dev-lead entries at 08:12:58 (`pytest ... -q ... tail -n 30`) and
08:13:10 (`python --version && python deliverables/loc.py deliverables`), immediately after
`mkdir deliverables` at 08:11:42. Ledger backs the claimed commands were actually run by Dev.

## Findings table
| Claim | Verdict | Evidence |
|---|---|---|
| loc.py exists, meets decree feature list | TRUE | source read + black-box exercise above |
| test_loc.py has 9 named tests per decree list | TRUE | pytest -v item list matches |
| `pytest -q` → 9 passed | TRUE | re-run: 9 passed in 0.32s (count matches, time differs as expected) |
| sanity run → `.py 2 273` / `TOTAL 2 273` | TRUE | re-run: identical output |
| stdlib-only | TRUE | AST-parsed imports: argparse, os, sys |
| evidence.log backs Dev's claimed commands | TRUE | matching timestamped entries found |

No fabrications found. All decree requirements verified by direct invocation.

---

## Re-audit — Cycle 1 (rework: unittest conversion)

Prior gate (QC-TRUE, hash 7b8af30428620991) is stale: `deliverables/test_loc.py` changed. This
re-audit covers that change only; `loc.py` re-checked for regression.

### 1. `python3 -m unittest -v deliverables.test_loc`
Ran independently. Tail: `Ran 9 tests in 0.162s` / `OK`. All 9 named: test_bad_path_nonexistent,
test_bad_path_not_a_directory, test_binary_file_skipped, test_empty_directory, test_ext_filter,
test_extensionless_files, test_git_dir_is_skipped, test_nested_tree, test_top_limit — all `ok`.
Count and outcome match claim; timing differs (0.162s vs claimed 0.112s) — expected, not fabrication.

### 2. `python -m pytest deliverables/test_loc.py -q`
Ran independently. Output: `9 passed in 0.25s`. Count/outcome match claim (`9 passed`); timing
differs (0.25s vs claimed 0.30s) — expected.

### 3. Case-by-case comparison against first-audit record (§2 above)
`deliverables/` is untracked in git (no prior commit to diff), so compared current
`TestLoc` methods against the prose assertions this audit recorded the first time:
| Case | First audit recorded | Current method | Verdict |
|---|---|---|---|
| empty dir | rc==0, "TOTAL" present, 0 counts | `test_empty_directory`: same, `assertEqual`/`assertIn` | preserved |
| nested tree | per-ext file/line counts, .py before .js order | `test_nested_tree`: same 3/9 totals, order check via `assertLess` | preserved |
| .git skip | config excluded, TOTAL 1/2 | `test_git_dir_is_skipped`: `assertNotIn("config")`, TOTAL 1/2 | preserved |
| --ext filter | .py/.js in, .md excluded | `test_ext_filter`: identical | preserved |
| --top limit | only top row shown, TOTAL reflects all files | `test_top_limit`: TOTAL 3/16 over all files despite --top 1 | preserved |
| extensionless | (none) grouping, 2 files/4 lines | `test_extensionless_files`: identical | preserved |
| binary skip | .bin excluded, TOTAL 1/1 | `test_binary_file_skipped`: identical | preserved |
| bad path (nonexistent) | rc!=0, "does not exist" in stderr | `test_bad_path_nonexistent`: identical | preserved |
| bad path (not a dir) | rc!=0, "not a directory" in stderr | `test_bad_path_not_a_directory`: identical | preserved |

All 9 original checks present; no assertion weakened (each still checks the same numeric/string
conditions, now via `self.assertEqual`/`assertIn`/`assertNotIn` instead of bare `assert`), no case
lost, no case merged or renamed away.

### 4. `loc.py` regression check (fresh temp dir `/tmp/qc_recheck`, not the pytest fixture)
Built `a.py` (3 lines), `b.js` (2 lines), `c.md` (1 line).
- `--ext .py,.js`: output `.py 1 3`, `.js 1 2`, `TOTAL 2 5` — .md correctly excluded → matches
  documented filter behavior.
- Nonexistent path: stderr `error: path does not exist: ...`, exit=1 → matches first audit.
- Path is a file: stderr `error: not a directory: ...`, exit=1 → matches first audit.
`loc.py` unchanged in behavior from first audit (source also unread-diffed but re-exercised
end-to-end; no regression found).

### Re-audit findings table
| Claim | Verdict | Evidence |
|---|---|---|
| `unittest -v deliverables.test_loc` → 9 tests, OK | TRUE | re-run: Ran 9 tests in 0.162s / OK, all named |
| `pytest -q` → 9 passed | TRUE | re-run: 9 passed in 0.25s |
| No assertion weakened / no case lost in conversion | TRUE | 9/9 cases matched against first-audit record, see table above |
| `loc.py` CLI unchanged | TRUE | fresh temp-dir re-exercise: --ext filter + both bad-path exits match first audit |

No fabrications found in the rework. Original hook gap (unittest collecting 0 tests from
function-style pytest suite) is resolved by the `TestLoc` class conversion; both runners now
execute all 9 cases.

---

## Correction, appended at archival — not charged as a defect

§1 states `loc.py` (137 lines) and `test_loc.py` (138 lines). Measured at archival, `loc.py`
holds 136 newline-terminated lines and `test_loc.py` holds 142.

The `test_loc.py` figure is additionally stale — the rework grew that file after §1 was written,
which is expected and is part of why this file carries `truth-lint: historical`. But staleness
does not explain §1: both figures were one too high when written. The tool's own sanity run in
§3 measured those two files at 273 lines combined, and 136 + 137 = 273, so `loc.py` was 136 and
`test_loc.py` was 137 at that moment. §1 reports 137 and 138. A consistent +1 on both is the
signature of counting the trailing newline as a line.

Recorded, not charged. §1's purpose was to establish the files exist, and they do; no verdict,
gate, or downstream figure rests on those two counts, and the figure that mattered — the 273
measured by the tool — reproduced exactly. But it is worth naming precisely, because it is the
one place in this audit where QC stated a number it had not measured with the same rigour it
applied everywhere else: §1 cites `ls -la`, which reports bytes, not lines. A record that
quietly drops its small errors teaches the reader to distrust its large ones.
