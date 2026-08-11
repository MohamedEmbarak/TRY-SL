<!-- truth-lint: historical -->
# renamer

Single-file Python 3.11 stdlib CLI that batch-renames files (and optionally
directories) matching a glob pattern, using a template.

```
python3 renamer.py --pattern GLOB --template TEMPLATE [--path DIR]
                    [--recursive] [--dry-run]
                    [--on-collision {skip,fail,overwrite}]
                    [--include-dirs] [-v]
```

No config files, no interactive prompts, no plugins, no third-party
dependencies.

## Flags

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--pattern GLOB` | yes | — | glob (`fnmatch`-style, e.g. `*.txt`, `img_??.png`) matched against the base filename only, not the full path |
| `--template STR` | yes | — | replacement template — see Template Semantics below |
| `--path DIR` | no | `.` | directory to scan |
| `--recursive` | no | off | descend into subdirectories (`os.walk`); without it, only the top level of `--path` is scanned |
| `--dry-run` | no | off | print planned renames, perform zero filesystem writes |
| `--on-collision {skip,fail,overwrite}` | no | `fail` | collision policy — see Collision Modes below |
| `--include-dirs` | no | off | also match/rename directory entries, not just files |
| `-v`, `--verbose` | no | off | print one `RENAME: <src> -> <dst>` line per attempted rename (independent of `--dry-run`) |
| `-h`, `--help` | no | — | print usage and exit 0 |

Verified `-h` output:

```
$ python3 renamer.py -h
usage: renamer.py [-h] --pattern PATTERN --template TEMPLATE [--path PATH]
                  [--recursive] [--dry-run]
                  [--on-collision {skip,fail,overwrite}] [--include-dirs] [-v]

Batch-rename files (and optionally directories) matching a glob pattern using
a template.

options:
  -h, --help            show this help message and exit
  --pattern PATTERN     glob (fnmatch-style) matched against the base filename
  --template TEMPLATE   replacement template; supports {name}, {ext}, {n} (and
                        {n:03}-style format specs on {n})
  --path PATH           directory to scan (default: current directory)
  --recursive           descend into subdirectories
  --dry-run             print planned renames, perform none
  --on-collision {skip,fail,overwrite}
                        collision policy (default: fail)
  --include-dirs        also match/rename directory entries, not just files
  -v, --verbose         print one line per rename attempted
```

## Pattern / Template Semantics

- Matching uses `fnmatch.fnmatch` against the base filename only. A
  `--pattern` with no wildcard characters matches only that exact filename.
- Template placeholders, substituted per matched file:
  - `{name}` — filename without extension
  - `{ext}` — extension including the leading dot, or `""` if the file has none
  - `{n}` — 1-based sequence counter over matched files in the run (not
    zero-padded by default)
  - `{n:03}`-style — Python format-spec width/padding is supported on `{n}`,
    e.g. `{n:03}` → `001`
  - No other fields are recognized. An unknown field (e.g. `{bogus}`) is a
    template error, not a literal pass-through.
- Matched entries are sorted lexicographically by full path before `{n}` is
  assigned, so numbering is reproducible across runs and platforms.

## Worked Example — Basic Rename

```
$ ls basic/
a.txt  b.txt  c.md
$ python3 renamer.py --pattern "*.txt" --template "{name}_x{ext}" --path basic
exit=0
$ ls basic/
a_x.txt  b_x.txt  c.md
```

`c.md` is untouched because it does not match `--pattern`.

## Worked Example — `--dry-run`

```
$ ls dryrun/
a.txt  b.txt  c.md
$ python3 renamer.py --pattern "*.txt" --template "{name}_x{ext}" --path dryrun --dry-run
DRY-RUN: dryrun/a.txt -> dryrun/a_x.txt
DRY-RUN: dryrun/b.txt -> dryrun/b_x.txt
exit=0
$ ls dryrun/
a.txt  b.txt  c.md
```

No files were altered; disk state is identical before and after.

## Collision Modes (`--on-collision`)

A collision = the destination path already exists (as a file, dir, or
another rename's target) at rename time. In each example below, `a.txt` and
`b.txt` are matched by `--pattern "*.txt" --template "{name}.renamed"`, and
`b.renamed` already exists on disk before the run (so only `b`'s rename
collides; `a` renames cleanly first because `a` sorts before `b`).

### `fail` (default)

Stops immediately on the first collision, performs no further renames that
run, prints `ERROR: collision at <dst>` to stderr, exit code 3. Renames
already completed before the collision remain applied — no rollback.

```
$ ls fail/
a.txt  b.renamed  b.txt
$ python3 renamer.py --pattern "*.txt" --template "{name}.renamed" --path fail
ERROR: collision at fail/b.renamed
EXIT=3
$ ls fail/
a.renamed  b.renamed  b.txt
```

`a.txt` → `a.renamed` completed; `b.txt` was left in place once the
collision was hit.

### `skip`

Leaves the colliding source unrenamed, prints `SKIP: <src> (target exists)`
to stdout, continues with the remaining matches, exit 0 if no other errors.

```
$ ls skip/
a.txt  b.renamed  b.txt
$ python3 renamer.py --pattern "*.txt" --template "{name}.renamed" --path skip --on-collision skip
SKIP: skip/b.txt (target exists)
EXIT=0
$ ls skip/
a.renamed  b.renamed  b.txt
```

`b.txt` remains under its original name; `b.renamed`'s pre-existing content
is untouched.

### `overwrite`

Replaces the existing destination via `os.replace`, continues, exit 0 if no
other errors. Overwriting a directory target with `--include-dirs` is out of
scope (undefined behavior, not tested).

```
$ ls overwrite/
a.txt  b.renamed  b.txt
$ python3 renamer.py --pattern "*.txt" --template "{name}.renamed" --path overwrite --on-collision overwrite
exit=0
$ ls overwrite/
a.renamed  b.renamed
$ cat overwrite/b.renamed
NEW-CONTENT
```

`b.txt` (content `NEW-CONTENT`) replaced the old `b.renamed` (content
`OLD-CONTENT`); the old content is gone and `b.txt` no longer exists.

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | success — all applicable matches processed (renamed/skipped) per policy |
| 1 | `--dry-run` detected a would-be collision; no writes performed |
| 2 | usage/argument error — bad flags, unknown template field, `--path` not a directory |
| 3 | collision under `--on-collision fail`, or an unhandled `OSError` during rename (e.g. permission denied) |
| 4 | no files matched `--pattern` in the scanned scope |

## Other Behavior

- **Recursive mode** (`--recursive`): walks `--path` via `os.walk`. Symlinks
  are never followed for traversal; a symlink whose own name matches
  `--pattern` is treated as a file and may be renamed (the link itself, not
  its target).
- **`--include-dirs`**: directory entries are only matched/renamed when this
  flag is set; otherwise they are never touched, recursive or not.
- **No extension**: a file like `README` resolves `{ext}` to `""` — a
  template `{name}_v2{ext}` on `README` produces `README_v2`, with no
  trailing dot.

## Running the Tests

From the repository root:

```
python3 -m unittest deliverables.test_renamer
```

See `RELEASE_NOTES.md` for the observed result and known limitations.
