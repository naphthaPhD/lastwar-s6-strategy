# Mac migration handoff for S6 project

## Date

2026-06-06

## Verified Windows source folder

- Current project folder: `C:\Users\kitazaki\Documents\S6`
- Git branch at handoff creation: `main`
- Remote: `https://naphthaPhD@github.com/naphthaPhD/lastwar-s6-strategy.git`
- Current relation before this handoff edit: `main...origin/main`
- Pre-existing untracked local file: `jdx_run_note_latest.md`

This project is used as the Codex and ChatGPT handoff ledger for Last War Season 6 strategy work. The main workflow is: Windows Codex processes screenshots, OCR, CSV/JSON, maps, and strategy notes; outputs are committed to GitHub; ChatGPT reads the committed handoff/materials and produces interpretation, summaries, command drafts, and the next Codex instructions.

## What to copy to the MacBook

The user plans to copy the full local Windows folder to the Mac. That is acceptable, but the Mac side should treat several copied folders as local working material rather than publishable content.

Copy the whole folder if convenient:

```text
C:\Users\kitazaki\Documents\S6
```

Suggested Mac destination:

```text
~/Documents/S6
```

Important copied-but-local groups:

- `.venv/`: Windows virtual environment. Do not use it on macOS; recreate it.
- `.tessdata/`: local OCR support data. Keep if useful, but verify paths.
- `outputs/`, `tmp/`, `tmp_0531_samples/`, `map_exports/`: generated or scratch outputs. Keep for reference, but do not commit broadly.
- `S6powerrank/`, `dropbox_screenshots_20260524_084304/`, `協定スクショ/`, `拠点取得スクショ/`: local source/reference image groups. Keep local unless a specific evidence image is moved into `screenshots/selected/`.
- `jdx_run_note_latest.md`: currently untracked. Treat as local-only unless the user explicitly decides it should be formalized into `analysis/` or `strategy/`.
- `tmp_http_8000.err.log` and `tmp_http_8000.out.log`: empty local logs; not strategically important.

## Canonical files to read first on the Mac

Open these first to recover project context:

- `AGENTS.md`: repo operating rules, commit/push rules, and file placement policy.
- `analysis/latest_handoff.md`: newest ChatGPT-facing handoff. Read this before older analysis files.
- `docs/season6_mechanics.md`: Season 6 rule and mechanics reference.
- `strategy/season6_strategy.md`: #534/JDX strategy body.
- `strategy/action_plan.md`: execution tasks, checks, and open items.
- `research/source_log.md`: source and evidence log.
- `spec_phase3.md`: Phase 3 scoring/rule-engine contract.
- `tools/invasion_strategy_os/README.md`: strategy-map and Phase 3 tooling.
- `tools/fishery_protection_sheet/README.md`: Google Sheets / Apps Script fishery protection workflow.
- `tools/chat_event_preprocessor/README.md`: video-to-crop and OCR workflow.

## Current project content summary

Main strategy and handoff content:

- `analysis/`: recent OCR summaries, enemy-pressure analysis, commander review, R4/R5 briefing, fishery sheet system notes, GitHub transition notes, and this migration handoff.
- `strategy/`: stable strategy documents, member playbooks, alliance/server comparison, #534 defense planning, map planning, and archived older brief.
- `docs/`: rules, previous-thread context, Discord delta reviews, environment handoff, and project brief.
- `research/source_log.md`: evidence registry for screenshots, Discord, external references, and generated local data.
- `rules/`: focused rule notes such as fishery protection timers.
- `data/`: committed CSV/JSON datasets and templates.
- `sample_output/`: committed generated strategy outputs, including `map.html`, `state.json`, `briefing_input.json`, and `sheet_migration/*.csv`.
- `tools/invasion_strategy_os/`: map ingestion, graph construction, Phase 3 scoring, sheet-migration helpers, local interactive map server.
- `tools/fishery_protection_sheet/`: local copy of the bound Google Apps Script for the live fishery protection workbook.
- `tools/chat_event_preprocessor/`: local video crop/OCR preprocessing pipeline.

Recent strategic state recorded in `analysis/latest_handoff.md`:

- Enemy group behavior analysis says pressure is concentrated around #476, with #480 and #503 also relevant.
- Current recommended direction is selected defense, route delay, pact checks, and short command outputs such as `DEFEND`, `DELAY`, `PACT CHECK`, `ABANDON`, and `COUNTER only if weak`.
- Fishery map work has had live Google Sheets formatting regressions; if colors/borders disappear, treat it as a live sheet formatting issue and check representative cells before assuming data is wrong.
- The next useful operational layer is a command/next-action table, not more passive status tracking.

## Git and GitHub state

Before this migration file was created:

```text
branch: main
remote: https://naphthaPhD@github.com/naphthaPhD/lastwar-s6-strategy.git
recent commits:
  e721273 Add enemy group behavior analysis
  054841b Analyze zombie brother spawn pattern
  0eb716a Add stronghold occupation OCR summary
  fcf9dda Add current S6 project outputs
  6953852 Restore fishery map borders
untracked:
  jdx_run_note_latest.md
```

Operational rule: do not use `git add .`. This repo intentionally excludes large images, OCR temporary files, scratch outputs, caches, and local configs. Stage only specific files after checking:

```bash
git status --short --branch
git diff --stat
git diff --name-only
git add analysis/latest_handoff.md
git add analysis/2026-06-06_mac_migration_handoff.md
git diff --cached --stat
git diff --cached --check
git commit -m "Add Mac migration handoff"
git push
```

On the Mac, keep GitHub identity changes repo-local unless the user explicitly wants a global change:

```bash
git config --local user.name
git config --local user.email
git remote -v
```

If credentials fail after the copy, re-authenticate GitHub on the Mac instead of editing other projects' global settings.

## Mac first verification commands

From the copied folder:

```bash
cd ~/Documents/S6
git status --short --branch
git remote -v
git log --oneline -5
git diff --stat
git ls-files --others --exclude-standard
```

Confirm the repository still points to the same project and that the only expected untracked file is the local note unless newer Windows work added more files.

## Python and local tooling setup on macOS

Do not reuse the copied Windows `.venv`. Recreate it:

```bash
cd ~/Documents/S6
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r tools/invasion_strategy_os/requirements.txt
./.venv/bin/python -m pip install -r tools/chat_event_preprocessor/requirements.txt
```

Check for OS-specific paths in configs before running:

```bash
rg -n "C:\\\\|G:/|C:/|Users\\\\|/Users/" .
```

Expected path-sensitive areas:

- `tools/chat_event_preprocessor/config.json` may point to Windows video paths or external drives.
- generated metadata under `outputs/` may contain old local paths.
- older Discord/source notes may mention `/Users/...` paths from a previous Mac source; treat those as historical source references, not current paths.

## Strategy map tool on the Mac

Smoke-test with local sample data first:

```bash
./.venv/bin/python tools/invasion_strategy_os/invasion_strategy_os.py --config tools/invasion_strategy_os/config.example.json
```

Expected outputs:

```text
sample_output/map.html
sample_output/state.json
sample_output/briefing_input.json
```

Run the interactive map server when needed:

```bash
./.venv/bin/python tools/invasion_strategy_os/interactive_server.py --port 8010
```

Open:

```text
http://127.0.0.1:8010/
```

The full-map config reads Google Sheets CSV/export data and local ranking workbook data. If refresh fails on the Mac, check network access, spreadsheet permissions, and whether the Google Sheet is accessible to the current account/session.

## Chat/OCR pipeline on the Mac

The video preprocessing and OCR tools are in `tools/chat_event_preprocessor/`.

Mac setup requirements:

- Python 3.10+
- `ffmpeg`
- OpenAI API key for the OCR worker, only when the user explicitly allows external OCR upload

Basic run shape:

```bash
cd ~/Documents/S6/tools/chat_event_preprocessor
../../.venv/bin/python chat_event_preprocessor.py --config config.json
../../.venv/bin/python ocr_worker.py
```

Important policy note: raw student/institutional data and local game screenshots should not be sent externally by default. For this S6 project, OCR image upload to OpenAI should still be treated as a deliberate user-approved action when local images are involved.

## Google MCP / Sheets / Apps Script note

The Google MCP server expected for this project is the user's `sub` Google connector/server. It is not stored inside this repo. On the Mac, Codex must have that same `sub` Google MCP/server available and authorized before live Google Sheets inspection or edits will work.

Do not assume that local files automatically update live Google services:

- `tools/fishery_protection_sheet/Code.gs` is the local source copy for the bound Apps Script.
- If future menu runs in the live workbook should preserve behavior, update the bound Apps Script project from this local `Code.gs`.
- Set the Apps Script timezone to `Asia/Tokyo`.
- For fishery map regressions, inspect the live Google Sheet through the `sub` Google MCP first. The issue may be formatting/borders rather than data.
- The known map surface is the live fishery protection workbook, especially the map tab previously referred to as `萓ｵ謾ｻ莠域ｸｬ_菫晁ｭｷ蛻・ｌ濶ｲ蛻・￠` and the manual correction tab `謇句虚菫ｮ豁｣`.
- Representative cells such as `#534:A-1` and `#534:A-5` were previously enough to confirm map color/border restoration.

Before writing to production Sheets:

1. Generate or inspect local CSV/JSON first.
2. Verify calculations locally.
3. Use a review sheet or explicit user approval before touching production.
4. After any local `Code.gs` change, confirm whether the live bound Apps Script was actually updated.

## Files that should usually be committed

Good commit candidates:

- `analysis/*.md`
- `analysis/latest_handoff.md`
- `logs/timeline/*.md`
- `logs/chat/*.json`
- `logs/decisions/*.md`
- `rules/*.md`
- `data/*.json`
- `data/*.csv`
- `data/*.tsv`
- `prompts/*.md`
- selected `tools/*.py` or explicitly allowed tool subtrees
- `screenshots/selected/**` only for important evidence images

Do not broadly commit:

- `.venv/`, `venv/`
- `__pycache__/`, `*.pyc`
- `outputs/`, `tmp/`, `temp/`, `cache/`, `debug/`, `output_tmp/`, `intermediate/`
- bulk screenshots and raw/cropped OCR folders
- `.env`, `.env.local`, API keys, Google credentials, local token caches
- ambiguous root-level scratch files such as `jdx_run_note_latest.md`

## Encoding and filename cautions

Some Japanese text can appear garbled in PowerShell or terminal output even when the file itself is usable. On the Mac, prefer UTF-8-aware tools and verify before concluding a file is corrupted.

Useful checks:

```bash
python3 - <<'PY'
from pathlib import Path
for p in ["analysis/latest_handoff.md", "AGENTS.md", "README.md"]:
    try:
        Path(p).read_text(encoding="utf-8")
        print("utf-8 ok", p)
    except UnicodeDecodeError as e:
        print("decode problem", p, e)
PY
```

Japanese path names may also copy differently depending on the transfer method. After copying, compare `git status --short --branch`; if many tracked Japanese paths appear modified or deleted, stop and check Unicode normalization or copy method before committing.

## Recommended migration order

1. On Windows, finish this handoff commit/push and check `git status`.
2. Copy the full `C:\Users\kitazaki\Documents\S6` folder to the Mac.
3. On the Mac, open `analysis/2026-06-06_mac_migration_handoff.md` and `analysis/latest_handoff.md`.
4. Run Git verification commands.
5. Recreate `.venv`; do not reuse the Windows one.
6. Install Python dependencies for `invasion_strategy_os` and `chat_event_preprocessor`.
7. Confirm `sub` Google MCP/server is available and authorized.
8. Smoke-test `tools/invasion_strategy_os` with local sample config.
9. Only after local smoke tests, try Google Sheets-backed configs.
10. For any live Sheet/App Script work, verify the actual live workbook and bound script state before claiming completion.

## Open questions for the Mac side

1. Should `jdx_run_note_latest.md` remain local-only, or should its useful content be formalized into `analysis/`?
2. Is the Mac Google MCP/server already configured with the same `sub` Google connector?
3. Should generated `outputs/` be archived locally only, or should selected summaries be promoted into committed `analysis/`, `data/`, or `logs/` files?
4. After migration, should the hourly Windows-side `s6-safe-auto-push` automation be disabled or recreated for the Mac workflow?
