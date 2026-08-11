"""Shared helpers for the Doctrine hooks.

These hooks exist because the Doctrine is otherwise a set of requests. A hook runs
whether the model cooperates or not, so the claims it checks stop being promises.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def project_dir():
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())


def read_event():
    """Read the hook payload from stdin. Never raise — a crashing hook is a silent hook."""
    try:
        return json.loads(sys.stdin.read() or "{}")
    except Exception:
        return {}


def block(reason):
    """Exit 2: blocking. stderr is fed back to the model as the reason."""
    print(reason, file=sys.stderr)
    sys.exit(2)


def ok(context=None, event=None):
    """Exit 0, optionally handing the model context it did not ask for."""
    if context and event:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": event,
                "additionalContext": context,
            }
        }))
    sys.exit(0)


# --- test suite -----------------------------------------------------------------

CLAIM_RAN = re.compile(r"\bRan\s+(\d+)\s+tests?\b")
CLAIM_OK = re.compile(r"^\s*OK\b(?:\s*\(skipped=(\d+)\))?\s*$", re.M)
CLAIM_FAILED = re.compile(r"^\s*FAILED\b", re.M)


def find_suite(root):
    """Return the dotted module names of every test file, rooted at the project dir.

    Deliberately not `unittest discover`: a directory without __init__.py is not
    importable as a start dir, and discover fails with an ImportError that looks
    exactly like a failing suite. Naming the modules works with or without
    __init__.py, since Python 3 treats them as namespace packages.
    """
    mods = []
    for d in ("deliverables", "tests", "src", "."):
        base = root / d
        if not base.is_dir():
            continue
        for f in sorted(base.rglob("test_*.py")):
            if "__pycache__" in f.parts:
                continue
            rel = f.relative_to(root).with_suffix("")
            mods.append(".".join(rel.parts))
        if mods:
            break
    return mods or None


def run_suite(root):
    """Actually execute the suite. Returns (ran, ok_flag, skipped, output) or None."""
    mods = find_suite(root)
    if not mods:
        return None
    cwd = root
    args = ["python3", "-m", "unittest", "-v", *mods]
    try:
        p = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, timeout=300)
    except Exception as exc:  # timeout, missing python, anything
        return ("ERROR", False, 0, str(exc))
    out = (p.stdout or "") + (p.stderr or "")
    m = CLAIM_RAN.search(out)
    ran = int(m.group(1)) if m else None
    okm = CLAIM_OK.search(out)
    skipped = int(okm.group(1)) if (okm and okm.group(1)) else 0
    return (ran, bool(okm), skipped, out)


# --- gates ----------------------------------------------------------------------

def deliverables_hash(root):
    """Content hash of deliverables/. Any edit invalidates every gate bound to it."""
    d = root / "deliverables"
    if not d.is_dir():
        return None
    h = hashlib.sha256()
    for f in sorted(p for p in d.rglob("*") if p.is_file()):
        if "__pycache__" in f.parts:
            continue
        h.update(str(f.relative_to(d)).encode())
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def read_gate(root, name):
    p = root / ".gates" / f"{name}.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def write_gate(root, name, digest, note=""):
    d = root / ".gates"
    d.mkdir(exist_ok=True)
    (d / f"{name}.json").write_text(json.dumps(
        {"gate": name, "deliverables": digest, "note": note}, indent=2) + "\n")
