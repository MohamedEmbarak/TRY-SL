<!-- truth-lint: historical -->
# bigfiles 1.0.0

Reports the largest files under a directory. Standard library only, Python 3.8+.

## Usage

```
python3 bigfiles.py [PATH] [-n COUNT]
```

Defaults to the current directory and the 10 largest files. Exit 0 on results, 1 when the
directory is empty, 2 on a bad path or a count below 1.

## Verification

```
Ran 10 tests in 0.005s

OK
```

Reproduce from the repository root:

```bash
python3 -m unittest runs.bigfiles_2026_08.test_bigfiles
```

## Known limitations

- Symlinks are not followed, and symlinked files are excluded from results.
- Files that vanish between the directory walk and the stat call are skipped silently.
- Sizes are apparent size, not disk usage; sparse files will over-report.
