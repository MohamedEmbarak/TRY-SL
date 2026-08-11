# TRY-SL — a demo project for the Supreme Leader plugin

A place to watch [Supreme Leader](https://github.com/MohamedEmbarak/Supreme-Leader) work, and
an archive of the run that proved it does.

As of v2.0 the organization is an installable Claude Code plugin, so this repo no longer
carries a copy of it. It carries an `ORGANIZATION.md` — which is the switch that makes the
plugin's hooks active in a project — and the preserved artifacts of the first verified run.

## Use it

```
/plugin marketplace add MohamedEmbarak/Supreme-Leader
/plugin install supreme-leader@embarak
```

Then open this repo in Claude Code and issue a decree:

```
/supreme-leader:decree Add a --dry-run flag to the renamer, with tests. 1 cycle.
```

The orchestrator triages the muster, seats the teams on first use, and dispatches. Artifacts
land in `deliverables/`. The hooks are live the whole time: a test figure that does not
reproduce is blocked at write time, an unresolvable import cannot be committed to a
deliverable, and the turn cannot end while the ship gates are missing or stale.

`/supreme-leader:lore on` if you want the tyrant back — directorates, souls, tribunals, the
kneeling line. Identical mechanism, different vocabulary.

## The archives: `runs/`

Two completed decrees, kept because they are evidence rather than decoration. Both suites
still execute from where they sit — run them yourself:

```bash
python3 -m unittest runs.renamer_2026_08.test_renamer
python3 -m unittest runs.bigfiles_2026_08.test_bigfiles
```

### `renamer_2026_08` — v1, lore register, three cycles, 26 tests

| File | What it is |
|---|---|
| `requirements.md` | 20 numbered acceptance criteria, written before implementation |
| `renamer.py`, `test_renamer.py` | The CLI and its suite |
| `README.md`, `RELEASE_NOTES.md` | What Delivery shipped |
| `qc-audit.md` | Three audit rounds, four findings — the interesting document |
| `ORGANIZATION-snapshot.md` | Roster, strike ledger, tribunal record, praise ledger at completion |

### `bigfiles_2026_08` — v2, plain register, SKIRMISH muster, 10 tests

The first run against the **installed plugin** rather than a vendored copy: added from the
published marketplace, then decreed. Two teams instead of five, one gate instead of three.
Its `qc-audit.md` records the moment that matters — Delivery's first draft of the release
notes stated a test count that was never printed, and the hook refused the write, re-ran the
suite, and returned the real output as its reason. The claim never reached disk.

**What QC caught**, before any of it reached a reader: a README worked-example whose printed
output had been hand-edited rather than captured (`./b.renamed` where the program prints
`fail/b.renamed`), a real dry-run bug where two sources renaming to the same destination went
undetected, and two rounds of stale figures in the release notes. QC withheld clearance
twice. One agent took a defect point at tribunal and survived it.

Every one of those findings was independently re-verified afterwards by re-running the
commands from a clean checkout.

That run is also *why the plugin has hooks*. QC caught the fabricated example by being
diligent — which is not a guarantee. The `truth-lint` hook now re-runs the suite against
anything written and blocks figures that do not reproduce, so that particular failure is no
longer possible rather than merely catchable.

## History

The v1 approach — the whole organization vendored into this repo as `CLAUDE.md`,
`.claude/agents/`, protocols, and writs — is preserved in this repository's git history, up
to commit `718c0b3`. Nothing was force-pushed. If you want to see how it worked before it
was installable, it is all still there.

## License

MIT. Upstream: [MohamedEmbarak/Supreme-Leader](https://github.com/MohamedEmbarak/Supreme-Leader).
