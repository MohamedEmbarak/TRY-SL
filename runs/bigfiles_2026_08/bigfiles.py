"""Report the largest files under a directory. Standard library only."""

import argparse
import os
import sys


def walk(root, follow_symlinks=False):
    """Yield (size, path) for every regular file under root."""
    for dirpath, _dirnames, filenames in os.walk(root, followlinks=follow_symlinks):
        for name in filenames:
            p = os.path.join(dirpath, name)
            try:
                st = os.lstat(p)
            except OSError:
                continue  # vanished or unreadable between walk and stat
            if os.path.isfile(p) and not os.path.islink(p):
                yield st.st_size, p


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024.0


def largest(root, count):
    return sorted(walk(root), key=lambda t: (-t[0], t[1]))[:count]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bigfiles", description="Report the largest files.")
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("-n", "--count", type=int, default=10)
    args = ap.parse_args(argv)
    if not os.path.isdir(args.path):
        print(f"error: not a directory: {args.path}", file=sys.stderr)
        return 2
    if args.count < 1:
        print("error: --count must be at least 1", file=sys.stderr)
        return 2
    rows = largest(args.path, args.count)
    if not rows:
        print("no files found")
        return 1
    for size, path in rows:
        print(f"{human(size):>8}  {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
