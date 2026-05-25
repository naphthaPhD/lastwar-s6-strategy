# Codex Project Instructions

This repository is the working handoff ledger for Last War Season 6 strategy work. Keep it readable by both Codex and ChatGPT.

## Operating Rules

- Preserve the existing canonical files:
  - `docs/season6_mechanics.md` for Season 6 mechanics, confirmed facts, hypotheses, and open questions.
  - `strategy/season6_strategy.md` for the main #534/JDX strategy.
  - `strategy/action_plan.md` for execution tasks.
  - `research/source_log.md` for source and evidence tracking.
- Use `analysis/latest_handoff.md` as the first file ChatGPT should read after each completed work unit.
- Store durable analysis as Markdown, JSON, CSV, or TSV. Avoid making PDF, screenshots, or raw OCR the only source of truth.
- Do not commit bulk screenshots, crop images, OCR debug outputs, cache files, virtual environments, or generated exports.
- Commit only selected files. Do not use `git add .`.
- Before committing or pushing, check `git status`, `git diff --stat`, `git diff --name-only`, and `git diff --cached --stat`.

## Directory Roles

- `analysis/`: situation analysis, alliance comparison, operation proposals, risks, and ChatGPT handoff summaries.
- `logs/timeline/`: dated event timelines.
- `logs/chat/`: structured chat logs or OCR-cleaned conversation data.
- `logs/decisions/`: decision records, withdrawal criteria, diplomacy notes, and operation choices.
- `rules/`: focused rule notes when a topic is not yet integrated into `docs/season6_mechanics.md`.
- `data/`: committed CSV, TSV, or JSON datasets that support analysis.
- `prompts/`: prompts for Codex, OCR, or ChatGPT analysis.
- `tools/`: intentionally maintained processing scripts. The current `.gitignore` keeps broad local helpers out unless explicitly allowlisted.
- `screenshots/selected/`: only evidence images important enough to review later.

## Standard Handoff

After a meaningful work unit, update `analysis/latest_handoff.md` with:

- date
- context
- updated files
- key findings
- current risks
- recommended next actions
- questions for ChatGPT
- notes and unresolved items

## Git Scope

If the worktree contains unrelated local or untracked files, leave them alone. Stage only the files that belong to the current work unit.
