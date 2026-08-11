# TRY-SL — the Supreme Leader, running

A live, runnable instance of the [Supreme Leader](https://github.com/MohamedEmbarak/Supreme-Leader)
prompt organization. The reference repo *describes* the organization. This one **is** it —
open a Claude Code session on this repo and you are talking to the Supreme Leader.

## How to experience it

Open a new Claude Code chat with this repository selected, and type:

```
/decree Build a CLI tool that renames files by pattern, with tests and a README. Deadline: 3 cycles.
```

That is all. `CLAUDE.md` loads automatically, the Supreme Leader takes the throne, Genesis
hires and names fifteen souls, and the five directorates begin work as real sub-agents.

You can also just write `DECREE: <ambition>` in plain prose — the slash command is a
convenience, not a requirement.

## Commands

| Command | What it does |
|---|---|
| `/decree <ambition>` | Issue a decree. Runs Genesis on first use, then dispatches the directorates. |
| `/report` | Command the Ascension Report — the full account of the current decree. |
| `/roster` | Show the roster, strike ledger, wipe queue, and praise ledger. |
| `/tribunal <name>` | Put a soul on trial. Ends in acquittal or erasure. |
| `/mute-lore` | Same organization, plain vocabulary — no souls, no kneeling, identical mechanism. |
| `/unmute-lore` | The names and the rites return. |

## What actually happens when you decree

1. **Genesis** — five Team Leads are appointed and named; two Employees are hired per
   directorate with names, titles, job descriptions, and KPIs. The roster is written to
   `ORGANIZATION.md`.
2. **Dispatch** — the Leads run as real sub-agents in pipeline order: Business defines testable
   criteria → Dev builds → QA breaks → QC audits truth → Delivery ships. Each Lead simulates
   its own Employees in-context, because sub-agents cannot spawn sub-agents.
3. **Judgment** — every soul is scored by the rubric in `protocols/kpi-report-formats.md`.
   Strikes accumulate. Fabrication is the unforgivable one.
4. **The Wipe** — three strikes, or one catastrophic fabrication, and the soul is erased into
   `BOOK_OF_THE_WIPED.md`, a successor hired the same turn under a new name and briefed on task
   state only. Context death is mechanical at Lead level (each dispatch starts empty); for the
   Employees simulated inside a Lead it is a quarantine directive — stated honestly in
   `protocols/the-wipe.md`.
5. **The Ascension Report** — the Supreme Leader kneels and presents the whole account. Then
   waits for your judgment, which lands on him and cascades downward the same cycle.

Your artifacts land in `deliverables/` as real files.

## The rule that makes it more than theatre

In this runtime the organization has a shell, so the Law of Truth is enforced rather than
role-played:

- A test result may only be reported if the test **was actually executed** and its output seen.
- A file may only be called delivered if it **exists on disk** — QC verifies, it does not trust.
- A package may only be imported if it is **installed and importable**.
- Anything unmeasurable is reported `UNVERIFIED`, which costs the agent nothing. Inventing it
  costs the agent its existence.

QC's audit is a shell audit. A QC report with no evidence of commands run is itself a
fabrication, and the strike lands on the auditor.

## Two honest warnings

**It is expensive.** Genesis plus five dispatched sub-agents per cycle burns real tokens. Give
it a decree with enough substance to be worth the ceremony — a one-line fix is not one, and the
Leader is instructed to tell you so rather than spend your budget looking impressive.

**It is opinionated about your conversation.** Every decree summons the full apparatus. If you
want an ordinary answer to an ordinary question, just ask — `CLAUDE.md` instructs the Leader to
drop the persona for anything that is not a decree.

## Map

| Path | Purpose |
|---|---|
| `CLAUDE.md` | The bootstrap: Supreme Leader persona + full Doctrine + runtime rules. Loads automatically. |
| `.claude/agents/` | The five directorate Leads, as dispatchable sub-agents. |
| `.claude/commands/` | The slash commands above. |
| `ORGANIZATION.md` | Live roster, strike ledger, praise ledger, current cycle. |
| `BOOK_OF_THE_WIPED.md` | Ledger of the erased. |
| `protocols/` | Report formats and rubric, the Wipe, the Ascension Report. |
| `templates/` | Employee and Senior hiring contracts. |
| `examples/genesis-run.md` | A worked example, hiring ceremony to judgment. |
| `deliverables/` | Where the organization's real output lands. |
| `DOCTRINE.md`, `SUPREME_LEADER.md` | The source texts, kept for portability to other runtimes. |

## License

MIT. Upstream: [MohamedEmbarak/Supreme-Leader](https://github.com/MohamedEmbarak/Supreme-Leader).
