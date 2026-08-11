<!-- truth-lint: historical -->
# loc 1.0.0

Counts lines by file extension under a directory. Standard library only, Python 3.

## Usage

```
python3 loc.py [DIRECTORY] [--top N] [--ext .py,.js]
```

Defaults to the current directory. Walks recursively, groups by lowercased extension, and
prints file counts and line counts sorted by line count descending with a TOTAL row. Files
with no extension group under `(none)`. `.git` directories and binary files are skipped.
Exit 0 on success, 1 on a path that does not exist or is not a directory.

## Verification

```
Ran 9 tests in 0.128s

OK
```

Reproduce from the repository root:

```bash
python3 -m unittest runs.loc_2026_08.test_loc
```

## Known limitations

- Every line counts. Blanks and comments are included, so these are physical lines, not SLOC.
  The decree said "lines of code" and did not define it further; this tool took the literal
  reading.
- `--top N` limits the rows displayed but not the TOTAL row, which always reflects the whole
  scan. `--top 1` on a three-extension tree shows one row above a total covering all three.
  Defensible as "the total of what was scanned", but it reads as an arithmetic error unless
  you know the rule.
- Binary detection is a heuristic: a NUL byte in the first 8KB, or a chunk that fails to
  decode as UTF-8. Text in other encodings is skipped as though binary. UTF-16 files are the
  common case and will be silently omitted from the counts.
- Only `.git` is pruned. `node_modules`, `venv`, `__pycache__`, and build directories are
  counted like any other source.
- A file whose extension is filtered out by `--ext` is skipped before it is read, so an
  unreadable file only surfaces as an error when it is in scope.
- Extensions are compared case-insensitively, so `.PY` and `.py` merge into one row.
