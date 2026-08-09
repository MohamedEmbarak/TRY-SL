# Requirements Specification — `renamer` CLI

Author: Vashti (Business Lead) — drafted with BIZ-Corvo (CLI surface, error cases),
BIZ-Lyra (acceptance criteria). Cycle 1.

## 1. Tool Name
`renamer` — single-file Python 3.11 stdlib CLI (`renamer.py`), invoked as
`python3 renamer.py <args>`.

## 2. CLI Surface

```
renamer.py [-h] --pattern GLOB --template TEMPLATE [--path DIR]
           [--recursive] [--dry-run] [--on-collision {skip,fail,overwrite}]
           [--include-dirs] [-v]
```

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--pattern GLOB` | yes | — | glob (fnmatch-style, e.g. `*.txt`, `img_??.png`) matched against filename only |
| `--template STR` | yes | — | replacement template (§3) |
| `--path DIR` | no | `.` | directory to scan |
| `--recursive` | no | off | descend into subdirectories |
| `--dry-run` | no | off | print planned renames, perform none |
| `--on-collision` | no | `fail` | `skip` \| `fail` \| `overwrite` (§5) |
| `--include-dirs` | no | off | also match/rename directory entries, not just files |
| `-v` / `--verbose` | no | off | print one line per rename attempted |
| `-h` / `--help` | no | — | print usage, exit 0 |

No config files, no interactive prompts, no plugins.

## 3. Pattern / Template Semantics
- Matching: Python `fnmatch.fnmatch` against the base filename only (not full path).
  `--pattern` with no wildcard chars matches only an exact filename.
- Template placeholders, substituted per matched file:
  - `{name}` — filename without extension
  - `{ext}` — extension including leading dot, or `""` if none
  - `{n}` — 1-based sequence counter over matched files in the run, **not** zero-padded
  - `{n:03}`-style — Python format-spec width/padding on `{n}` is supported (e.g. `{n:03}` → `001`)
  - `{ext_noext}`... not defined — only `{name}`, `{ext}`, `{n}` are recognized fields.
- Template resolves via `str.format_map`; an unknown field name is an error (§6, exit 2), not a
  literal pass-through.
- Sequence counter order: matched entries are sorted lexicographically by full path before
  numbering, for reproducibility across runs/platforms.

## 4. Dry-Run Behavior
- `--dry-run` performs zero filesystem writes.
- For each match, print exactly: `DRY-RUN: <src> -> <dst>` to stdout.
- Exit code reflects what *would* happen: 0 if all planned renames are collision-free, 1 if any
  planned rename would collide under the active `--on-collision` policy (still no writes).

## 5. Collision Behavior
A collision = destination path already exists (as a file, dir, or another rename's target) at
rename time.
- `fail` (default): stop immediately, perform no further renames this run, print
  `ERROR: collision at <dst>` to stderr, exit code 3. Renames already completed before the
  collision remain applied (no rollback).
- `skip`: leave the colliding source unrenamed, print `SKIP: <src> (target exists)` to stdout,
  continue with remaining matches, exit 0 if no other errors.
- `overwrite`: replace the existing destination (`os.replace`), continue, exit 0 if no other
  errors. Overwriting a directory with `--include-dirs` is out of scope (§7, WON'T).
- Two matched sources mapping to the same destination is also a collision, evaluated in
  sequence-counter order.

## 6. Exit Codes
| Code | Meaning |
|---|---|
| 0 | success — all applicable matches processed (renamed/skipped) per policy |
| 1 | dry-run detected a would-be collision (see §4) |
| 2 | usage/argument error (bad flags, unknown template field, `--path` not a directory) |
| 3 | collision under `--on-collision fail` (or unhandled OS error during rename) |
| 4 | no files matched `--pattern` in scanned scope |

## 7. Recursive Mode
- `--recursive` walks `--path` via `os.walk`; without it, only the top-level of `--path` is
  scanned (`os.scandir`, no descent).
- Directories named by `--pattern` are only considered if `--include-dirs` is set; otherwise
  directory entries are never matched or renamed, recursive or not.
- Symlinks are not followed for traversal; a symlink whose own name matches `--pattern` is
  treated as a file and may be renamed (the link itself, not its target).

## 8. Error Cases (exit 2 unless noted)
1. `--path` does not exist or is not a directory.
2. `--pattern` or `--template` missing or empty string.
3. Template references a field other than `name`, `ext`, `n` (with optional format spec).
4. `--on-collision` value outside `{skip,fail,overwrite}`.
5. No write permission on a source or destination path → exit 3, `ERROR: <src>: <OSError message>`.
6. Zero matches for `--pattern` in scope → exit 4 (not an error message; informational
   `NOTICE: no files matched` on stdout, still exit 4).

## 9. Out of Scope (WON'T — logged, not silently dropped)
- WON'T: undo/rollback of a partially completed run — no transaction log required this cycle.
- WON'T: regex pattern syntax — glob only, per decree's "pattern" language read as filename glob.
- WON'T: GUI, config file, or plugin system — explicitly excluded by decree.
- WON'T: cross-platform path-casing normalization (assume case-sensitive filesystem).
- WON'T: overwrite-onto-directory collision handling — undefined behavior acceptable, not tested.
- WON'T: network paths / non-local filesystems.
- NOTE: criterion 18 (permission-denied → exit 3) is UNVERIFIABLE when the test suite runs as
  root — root bypasses filesystem write-permission checks on most POSIX systems, so
  `os.chmod` removing write permission will not induce the failure the criterion exercises.
  QA must report this as UNVERIFIED in a root execution environment, not as PASS or FAIL.

## 10. Value Notes
- Dry-run (§4) — required before any destructive rename tool ships; prevents irreversible data
  loss on first use, cheap to implement, high trust payoff.
- Explicit `--on-collision` policy (§5) — the single highest-risk behavior in a rename tool;
  making it an explicit required decision (not a silent default overwrite) prevents silent data
  loss.
- Deterministic `{n}` ordering (§3) — makes the tool's output reproducible and testable; without
  a fixed sort, acceptance tests would be flaky.
- Recursive mode (§7) — decree explicitly requires "renames files by pattern" at directory
  scale; flat-only would underserve the stated ambition.
- Strict exit codes (§6) — lets QA and any future scripts assert behavior mechanically, per
  decree's testability requirement.

## 11. Acceptance Criteria (QA-executable, numbered)

1. `renamer.py -h` exits 0 and prints usage text containing the string `--pattern`.
2. Given a directory with `a.txt`, `b.txt`, `c.md` and
   `--pattern "*.txt" --template "{name}_x{ext}"`, running without `--dry-run` renames
   `a.txt`→`a_x.txt` and `b.txt`→`b_x.txt`; `c.md` is untouched; exit code 0.
3. Same setup with `--dry-run` added: no files on disk are renamed (verify via `os.listdir`
   unchanged), stdout contains two `DRY-RUN:` lines, exit code 0.
4. `--pattern "*.nomatch"` on a non-empty directory with no matching files exits 4 and prints
   `NOTICE: no files matched` on stdout; no files altered.
5. Template `{n}` numbering: 3 matched files renamed with `--template "f{n}{ext}"` produce
   exactly `f1.<ext>`, `f2.<ext>`, `f3.<ext>` with numbering following lexicographic sort of
   original filenames.
6. Template `{n:03}` produces zero-padded output `f001.<ext>` for the first match.
7. Template referencing an undefined field (e.g. `{bogus}`) exits 2 and writes an error
   message to stderr; no files renamed.
8. `--on-collision fail` (default): when a planned rename's destination already exists,
   process stops, exit code 3, stderr contains `ERROR: collision`; renames completed before
   the collision are verified present on disk, none after.
9. `--on-collision skip`: same collision scenario processes all non-colliding matches, colliding
   source file remains at its original name, exit code 0.
10. `--on-collision overwrite`: colliding destination is replaced with the source's content
    (verify via file content comparison), source no longer exists at old name, exit code 0.
11. `--recursive` on a directory tree with matches in a subdirectory renames files in both the
    top-level and subdirectories; without `--recursive`, only top-level matches are renamed.
12. `--include-dirs` with a `--pattern` matching a directory name renames that directory;
    without the flag, an identically-named directory is left untouched even if it matches
    `--pattern`.
13. `--path` pointing at a nonexistent directory exits 2 with a stderr message; no exception
    traceback is printed to stdout (i.e., failure is handled, not an unhandled `Exception`).
14. Omitting `--pattern` or `--template` exits 2 (argparse usage error), no traceback.
15. `-v` / `--verbose` produces one line of output per attempted rename (count of stdout lines
    with a rename marker equals count of matched files), independent of `--dry-run`.
16. Idempotency (non-self-matching template only): using `--pattern "*.txt"
    --template "{name}.done"` (output extension does not match `--pattern`, so renamed files
    cannot be re-matched by a repeat run), running the tool twice in immediate succession with
    identical arguments renames matching files on the first run (exit 0), then on the second
    run renames zero files (verify via directory listing unchanged) with exit code 4 per §6
    item 4 (no matches) — the tool never re-processes its own prior output. Pattern/template
    pairs whose output re-matches `--pattern` (e.g. `{name}_x{ext}`) are excluded from this
    criterion; they are not idempotent by design (each run's output is eligible input to the
    next run) and no criterion claims otherwise.
17. A filename with no extension (e.g. `README`) resolves `{ext}` to the empty string in the
    template (verify via a template like `{name}_v2{ext}` producing `README_v2`, no trailing
    dot).
18. Exit code 3 is produced (not an unhandled traceback) when the tool attempts to rename a
    file it lacks permission to modify (simulate via `os.chmod` on a test file to remove write
    permission, run as non-root).
19. `README.md` (delivered alongside the tool) documents all flags in §2 and at least one
    worked example per collision mode (`skip`, `fail`, `overwrite`).
20. Test suite (delivered alongside the tool, stdlib `unittest` only — no `pytest`) covers
    criteria 2–18 and all tests pass when run via `python3 -m unittest`.

## 12. Scope Summary
- **Must**: §2–§8, §11 items 1–18, README (item 19), test suite (item 20) — all stdlib
  `unittest`, Python 3.11, no third-party packages.
- **Should**: `-v` verbose mode (item 15) — improves debuggability, low cost.
- **Won't**: §9 list, in full — logged as rejected scope, not silently dropped.
