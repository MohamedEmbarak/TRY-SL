#!/usr/bin/env python3
"""Stop — the three gates, enforced.

Delivery's rule is that nothing ships without QA PASS + QC TRUE + Business ACCEPT.
As prose that is a promise. Here it is a precondition for ending the turn.

Every gate is bound to a content hash of deliverables/. Touch any deliverable and
every gate bound to the old hash goes stale automatically — so a gate cannot be
claimed early and quietly outlived. The QA gate is not claimable at all: this hook
writes it, and only after the suite actually passes.

Loop safety: after MAX_BLOCKS refusals on the same hash the hook downgrades itself
to advisory. A hook that can trap the conversation is worse than one that can be
ignored.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (  # noqa: E402
    block, deliverables_hash, ok, project_dir, read_event, read_gate, run_suite, write_gate,
)

REQUIRED = ["QC-TRUE", "BIZ-ACCEPT"]  # QA-PASS is hook-authored, never claimed
MAX_BLOCKS = 3


def attempts(root, digest, bump=False):
    p = root / ".gates" / ".attempts.json"
    data = {}
    if p.is_file():
        try:
            data = json.loads(p.read_text())
        except Exception:
            data = {}
    n = data.get(digest, 0)
    if bump:
        data = {digest: n + 1}  # only track the current hash
        p.parent.mkdir(exist_ok=True)
        p.write_text(json.dumps(data))
    return n


def main():
    root = project_dir()
    read_event()

    digest = deliverables_hash(root)
    if not digest:
        ok()  # nothing has been produced; nothing to gate

    # QA-PASS is written by this hook alone, and only on a real pass.
    suite = run_suite(root)
    if suite and suite[0] != "ERROR":
        ran, passed, skipped, _ = suite
        if passed:
            write_gate(root, "QA-PASS", digest, f"hook-verified: Ran {ran}, skipped {skipped}")
        else:
            if attempts(root, digest) >= MAX_BLOCKS:
                ok(f"ADVISORY: the suite does not pass and the ship gate has already refused "
                   f"{MAX_BLOCKS} times. Not blocking again — but nothing here is shippable.",
                   "Stop")
            attempts(root, digest, bump=True)
            block("DELIVERY GATE — QA PASS DENIED\n"
                  "The test suite does not pass. This hook writes the QA gate itself and will "
                  "not write it for a failing suite. Fix the failures, then stop.")

    missing = []
    for name in REQUIRED:
        g = read_gate(root, name)
        if g is None:
            missing.append(f"{name}: never recorded")
        elif g.get("deliverables") != digest:
            missing.append(f"{name}: STALE — recorded against {g.get('deliverables')}, "
                           f"deliverables are now {digest}")

    if not missing:
        ok()

    if attempts(root, digest) >= MAX_BLOCKS:
        ok("ADVISORY: ship gates are still unsatisfied (" + "; ".join(missing) +
           f"). The hook has refused {MAX_BLOCKS} times and is now standing down. "
           "Whatever ships now, ships ungated.", "Stop")

    attempts(root, digest, bump=True)
    block(
        "DELIVERY GATE — SHIP REFUSED\n"
        + "\n".join("  " + m for m in missing)
        + f"\n\ndeliverables/ currently hashes to {digest}.\n"
        "Every gate is bound to that hash, so any edit invalidates the gates that "
        "preceded it. Have the responsible directorate re-verify and record:\n"
        "  python3 .claude/hooks/gate.py QC-TRUE   \"<what QC verified, with the command>\"\n"
        "  python3 .claude/hooks/gate.py BIZ-ACCEPT \"<criteria met>\"\n"
        "Recording a gate you did not verify is a false PASS — a strike of the gravest kind."
    )


if __name__ == "__main__":
    main()
