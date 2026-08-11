#!/usr/bin/env python3
"""loc.py - count lines of code by file extension in a directory.

Standard-library only. Walks a directory recursively, skips .git
directories and binary files, and prints a table of line counts and
file counts grouped by extension (case-insensitive), sorted by line
count descending.
"""
import argparse
import os
import sys


def is_binary(path, chunk_size=8192):
    """Return True if the file looks binary (skip it), False if it's text.

    A file is considered binary if it can't be opened/read, or if the
    first chunk contains a NUL byte, or if it can't be decoded as UTF-8.
    """
    try:
        with open(path, "rb") as f:
            chunk = f.read(chunk_size)
    except OSError:
        return True
    if b"\x00" in chunk:
        return True
    try:
        chunk.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


def count_lines(path):
    """Count lines in a text file. Returns None if the file is binary/unreadable."""
    if is_binary(path):
        return None
    try:
        with open(path, "r", encoding="utf-8", errors="strict") as f:
            return sum(1 for _ in f)
    except (OSError, UnicodeDecodeError):
        return None


def ext_of(filename):
    _, ext = os.path.splitext(filename)
    if not ext or ext == ".":
        return "(none)"
    return ext.lower()


def scan(root, ext_filter=None):
    """Walk root, return dict: ext -> {"files": int, "lines": int}."""
    stats = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            ext = ext_of(name)
            if ext_filter is not None and ext not in ext_filter:
                continue
            full = os.path.join(dirpath, name)
            lines = count_lines(full)
            if lines is None:
                continue  # binary or unreadable, skip
            entry = stats.setdefault(ext, {"files": 0, "lines": 0})
            entry["files"] += 1
            entry["lines"] += lines
    return stats


def normalize_ext_list(raw):
    exts = set()
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        if not item.startswith("."):
            item = "." + item
        exts.add(item.lower())
    return exts


def format_table(stats, top=None):
    rows = sorted(stats.items(), key=lambda kv: (-kv[1]["lines"], kv[0]))
    if top is not None:
        rows = rows[:top]

    total_files = sum(v["files"] for v in stats.values())
    total_lines = sum(v["lines"] for v in stats.values())

    ext_w = max([len("Extension")] + [len(e) for e, _ in rows])
    files_w = max([len("Files")] + [len(str(v["files"])) for _, v in rows] + [len(str(total_files))])
    lines_w = max([len("Lines")] + [len(str(v["lines"])) for _, v in rows] + [len(str(total_lines))])

    lines_out = []
    header = f"{'Extension':<{ext_w}}  {'Files':>{files_w}}  {'Lines':>{lines_w}}"
    lines_out.append(header)
    lines_out.append("-" * len(header))
    for ext, v in rows:
        lines_out.append(f"{ext:<{ext_w}}  {v['files']:>{files_w}}  {v['lines']:>{lines_w}}")
    lines_out.append("-" * len(header))
    lines_out.append(f"{'TOTAL':<{ext_w}}  {total_files:>{files_w}}  {total_lines:>{lines_w}}")
    return "\n".join(lines_out)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="loc.py",
        description="Count lines of code by file extension in a directory.",
    )
    parser.add_argument("directory", nargs="?", default=".", help="directory to scan (default: current directory)")
    parser.add_argument("--top", type=int, default=None, help="show only the N largest extension groups")
    parser.add_argument("--ext", type=str, default=None, help="comma-separated extension list to restrict to, e.g. .py,.js")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not os.path.exists(args.directory):
        print(f"error: path does not exist: {args.directory}", file=sys.stderr)
        return 1
    if not os.path.isdir(args.directory):
        print(f"error: not a directory: {args.directory}", file=sys.stderr)
        return 1

    ext_filter = normalize_ext_list(args.ext) if args.ext else None

    stats = scan(args.directory, ext_filter=ext_filter)
    print(format_table(stats, top=args.top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
