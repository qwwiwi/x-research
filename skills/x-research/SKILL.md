---
name: x-research
description: "Search X (Twitter) from the terminal via xAI Grok Live Search (the built-in x_search tool of the xAI Responses API). Use when the user asks to research X/Twitter, find what's trending in a niche, scan a watchlist of accounts, pull posts/threads on a topic, or build a market/content radar from X. CLI only (no MCP, no cookies, no scraping). Returns a synthesized answer + citations to the source X posts."
---

# X Research — Grok Live Search from the terminal

`x_search.py` searches X (Twitter) by calling **xAI's built-in `x_search` tool** on the
Responses API (`https://api.x.ai/v1/responses`). Grok runs the search server-side and returns a
synthesized answer with citations to the originating posts. This is the official xAI path —
no cookies, no scraping, no MCP.

## Why this (and not cookies / twscrape)

xAI **Grok Live Search** is the official, sanctioned way to search X programmatically — no X ToS
risk, no account-suspension risk, no session cookies to refresh. Cookie scrapers
(twscrape/twikit) are the wrong answer; this skill is the right one.

## Auth

The script reads an xAI credential in this order:

1. env `XAI_API_KEY`;
2. a key file — `~/.config/x-research/xai.key` by default, override with env `XAI_KEY_FILE`.

**The token is never printed.** Never pass it in argv, never paste it into chats or agent memory.
Usage is billed / limited by your xAI account.

## Usage

```bash
PY=python3
SK=~/.claude/skills/x-research/scripts/x_search.py

# free-form topic
$PY $SK "что нового по AI agents за последние две недели"

# restrict to watchlist handles + a date window
$PY $SK "Claude Code skills and subagents" --handles karpathy,simonw,bcherny --from 2026-06-03

# raw JSON (for piping into a report builder)
$PY $SK "AI agent funding rounds" --json
```

Flags: `--handles a,b,c` (allowed_x_handles), `--exclude a,b`, `--from YYYY-MM-DD`, `--to YYYY-MM-DD`,
`--model` (default `grok-4.20-reasoning`, or env `XAI_MODEL`), `--images`, `--videos`, `--json`.

Output (default): synthesized answer, then a `--- Источники (X) ---` list of cited post URLs.

## Watchlist

`references/watchlist.md` — an EXAMPLE list of public AI/agents/vibe-coding accounts grouped by
role. Replace it with your own niche. xAI caps `allowed_x_handles` per call — **sweep in batches
of ~10–15** for full coverage, then merge.

## Research workflow (a full radar run)

1. Define niche + window (default 14 days). Pull the watchlist from `references/watchlist.md`.
2. Sweep handles in batches of ~10–15 with `--handles` + `--from`; also run 1–2 open queries (no
   `--handles`) for long-tail discovery of new authors.
3. Collect the synthesized answers + citations. Cluster by theme (models/releases, coding agents,
   workflows, ROI, prompt/evals, memory/context, …).
4. Rank by recurrence + which authors repeat. Produce: top themes, top posts/threads (URLs), new
   authors to add to the watchlist, content ideas.
5. Schedule: a weekly cron calling this CLI gives a recurring market/content radar.

## Notes / limits

- A complex query takes 60–120s (timeout 200s).
- The model id changes over time: if the default is rejected, pass a current one with `--model`
  or env `XAI_MODEL`.
- Grok synthesizes from X discourse; treat claims as "what X is saying", verify before publishing.
