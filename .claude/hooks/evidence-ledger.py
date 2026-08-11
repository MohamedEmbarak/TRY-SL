#!/usr/bin/env python3
"""PreToolUse(Bash) — the evidence ledger.

Records every command the organization runs, with a timestamp. Never blocks.

The point is not surveillance, it is falsifiability: once a ledger exists, "this
output was observed" becomes a checkable claim rather than an assertion. A terminal
transcript in a deliverable with no matching ledger entry was hand-written, by
definition. DEL-Osric's standing constraint stops depending on DEL-Osric.
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import ok, project_dir, read_event  # noqa: E402


def main():
    event = read_event()
    root = project_dir()
    cmd = (event.get("tool_input") or {}).get("command")
    if not cmd:
        ok()

    ledger = root / "evidence" / "commands.log"
    ledger.parent.mkdir(exist_ok=True)
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "agent": event.get("agent_type") or "orchestrator",
        "cmd": cmd if len(cmd) <= 2000 else cmd[:2000] + " …[truncated]",
    }
    try:
        with ledger.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # a ledger failure must never block the organization's work
    ok()


if __name__ == "__main__":
    main()
