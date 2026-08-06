#!/usr/bin/env python3
"""renamer.py -- batch file/directory renaming CLI (glob pattern -> template).

Python 3.11, stdlib only. See README.md for usage and exit-code reference.
"""

import argparse
import fnmatch
import os
import string
import sys

ALLOWED_FIELDS = {"name", "ext", "n"}


class TemplateError(ValueError):
    """Raised when a template references an unsupported field."""


class UsageError(ValueError):
    """Raised for argument/usage problems detected outside argparse."""


# ---------------------------------------------------------------------------
# Template handling
# ---------------------------------------------------------------------------

def validate_template(template):
    """Statically check that every field in `template` is one of ALLOWED_FIELDS.

    Raises TemplateError on an unknown or malformed field. Does not require
    any matches to exist -- this is a pure string check.
    """
    formatter = string.Formatter()
    try:
        parsed = list(formatter.parse(template))
    except ValueError as exc:
        raise TemplateError(f"malformed template: {exc}") from exc
    for _literal, field_name, _format_spec, _conversion in parsed:
        if field_name is None:
            continue
        base = field_name.split(".")[0].split("[")[0]
        if base == "":
            raise TemplateError("template contains a positional/empty field; "
                                 "only {name}, {ext}, {n} are supported")
        if base not in ALLOWED_FIELDS:
            raise TemplateError(f"unknown template field: {{{field_name}}}")


def render_name(template, name, ext, n):
    mapping = {"name": name, "ext": ext, "n": n}
    try:
        return template.format_map(mapping)
    except (KeyError, IndexError, ValueError) as exc:
        raise TemplateError(f"template rendering failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Scanning / matching
# ---------------------------------------------------------------------------

def scan_entries(root, recursive):
    """Return a flat list of os.DirEntry objects under `root`.

    Non-recursive: only the top level (os.scandir, no descent).
    Recursive: descends into real (non-symlink) subdirectories only --
    symlinks are never followed for traversal.
    """
    results = []

    def _scan(dirpath):
        with os.scandir(dirpath) as it:
            entries = list(it)
        results.extend(entries)
        if recursive:
            for e in entries:
                if e.is_symlink():
                    continue
                if e.is_dir(follow_symlinks=False):
                    _scan(e.path)

    _scan(root)
    return results


def entry_is_matchable(entry, include_dirs):
    """A symlink (to file or dir) is always treated as a file-like entry.
    A real directory is only matchable when --include-dirs is set.
    Anything else (regular file) is always matchable.
    """
    if entry.is_symlink():
        return True
    if entry.is_dir(follow_symlinks=False):
        return include_dirs
    return True


def find_matches(path, pattern, recursive, include_dirs):
    entries = scan_entries(path, recursive)
    matched = [
        e.path for e in entries
        if entry_is_matchable(e, include_dirs) and fnmatch.fnmatch(e.name, pattern)
    ]
    matched.sort()  # lexicographic by full path, per spec Sec.3
    return matched


# ---------------------------------------------------------------------------
# Planning
# ---------------------------------------------------------------------------

def plan_renames(matched_paths, template):
    """Compute (src, dst) pairs in sequence-counter order. Raises TemplateError."""
    plan = []
    for i, src in enumerate(matched_paths, start=1):
        dirpath = os.path.dirname(src)
        basename = os.path.basename(src)
        name, ext = os.path.splitext(basename)
        dst_name = render_name(template, name, ext, i)
        dst = os.path.join(dirpath, dst_name) if dirpath else dst_name
        plan.append((src, dst))
    return plan


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def run_dry(plan, verbose):
    """Print DRY-RUN lines for every planned rename; return exit code (0 or 1)."""
    any_collision = False
    for src, dst in plan:
        print(f"DRY-RUN: {src} -> {dst}")
        if verbose:
            print(f"RENAME: {src} -> {dst}")
        if os.path.lexists(dst):
            any_collision = True
    return 1 if any_collision else 0


def run_real(plan, on_collision, verbose):
    """Execute renames per the collision policy. Returns exit code (0 or 3)."""
    for src, dst in plan:
        if verbose:
            print(f"RENAME: {src} -> {dst}")
        collides = os.path.lexists(dst)
        if collides:
            if on_collision == "fail":
                print(f"ERROR: collision at {dst}", file=sys.stderr)
                return 3
            if on_collision == "skip":
                print(f"SKIP: {src} (target exists)")
                continue
            # on_collision == "overwrite": fall through to replace below.
        try:
            os.replace(src, dst)
        except OSError as exc:
            print(f"ERROR: {src}: {exc}", file=sys.stderr)
            return 3
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="renamer.py",
        description="Batch-rename files (and optionally directories) matching "
                     "a glob pattern using a template.",
    )
    parser.add_argument("--pattern", required=True,
                         help="glob (fnmatch-style) matched against the base filename")
    parser.add_argument("--template", required=True,
                         help="replacement template; supports {name}, {ext}, {n} "
                              "(and {n:03}-style format specs on {n})")
    parser.add_argument("--path", default=".",
                         help="directory to scan (default: current directory)")
    parser.add_argument("--recursive", action="store_true",
                         help="descend into subdirectories")
    parser.add_argument("--dry-run", action="store_true",
                         help="print planned renames, perform none")
    parser.add_argument("--on-collision", choices=["skip", "fail", "overwrite"],
                         default="fail", help="collision policy (default: fail)")
    parser.add_argument("--include-dirs", action="store_true",
                         help="also match/rename directory entries, not just files")
    parser.add_argument("-v", "--verbose", action="store_true",
                         help="print one line per rename attempted")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)  # argparse exits 2 itself on missing/invalid flags

    # --- Sec.8 usage validation not covered by argparse -----------------
    if args.pattern == "":
        print("ERROR: --pattern must not be empty", file=sys.stderr)
        return 2
    if args.template == "":
        print("ERROR: --template must not be empty", file=sys.stderr)
        return 2
    if not os.path.isdir(args.path):
        print(f"ERROR: --path {args.path!r} is not a directory", file=sys.stderr)
        return 2

    try:
        validate_template(args.template)
    except TemplateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    matched = find_matches(args.path, args.pattern, args.recursive, args.include_dirs)

    if not matched:
        print("NOTICE: no files matched")
        return 4

    try:
        plan = plan_renames(matched, args.template)
    except TemplateError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        return run_dry(plan, args.verbose)

    return run_real(plan, args.on_collision, args.verbose)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # last-resort guard against a raw traceback
        print(f"ERROR: unexpected failure: {exc}", file=sys.stderr)
        sys.exit(3)
