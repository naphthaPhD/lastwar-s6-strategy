# Windows Environment Handoff - 2026-05-24

This note records the local Windows/Codex setup work done after moving the
`lastwar-s6-strategy` workspace onto this machine. It is intentionally limited
to environment and workflow setup, not Season 6 strategy content.

## Workspace

- Working tree: `C:\Users\kitazaki\Documents\S6`
- GitHub remote: `https://github.com/kitazakis/lastwar-s6-strategy.git`
- The working tree should stay under `Documents`; use OneDrive for exports,
  screenshots, PDFs, PNGs, and backups rather than as the live Git checkout.

## Git and GitHub

- Confirmed `origin/main` was reachable from this checkout.
- Added this checkout to Git's global trusted directory list:
  `C:/Users/kitazaki/Documents/S6`
- Set Git credential helper to Git Credential Manager:
  `credential.helper=manager`
- Confirmed Git identity:
  `kitazakis <kitazaki@fit.ac.jp>`
- Installed GitHub CLI:
  `gh version 2.92.0`
- Authenticated GitHub CLI as `kitazakis` with keyring-backed storage.
- Verified GitHub CLI access with:
  `gh repo view kitazakis/lastwar-s6-strategy`

Operational notes:

- In the current Codex PowerShell session, `gh` may not appear on `PATH`
  immediately after installation. Use
  `C:\Program Files\GitHub CLI\gh.exe` directly or open a fresh shell.
- If `gh auth login --web` fails or hangs, start a fresh visible PowerShell
  window and run:
  `C:\Program Files\GitHub CLI\gh.exe auth login --hostname github.com --web --git-protocol https`
- When the goal is only GitHub CLI authentication, answer `No` to:
  `Authenticate Git with your GitHub credentials?`

## Google Sheets MCP

- Registered and validated the Windows Codex MCP setup for Google Sheets.
- Default Sheets path for this project should be `google-sheets-sub`.
- For recurring S6 sheet work, route by explicit `spreadsheet_id` rather than
  Drive browsing unless the task specifically requires Drive-level access.

## OCR Runtime

- Built a project-local OCR setup for recurring S6 screenshot and ranking image
  work.
- Validated stack:
  - Codex-bundled Python runtime
  - project-local `.venv`
  - `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - project-local `.tessdata`
  - Python packages: `pillow`, `opencv-python`, `pytesseract`, `pandas`,
    `openpyxl`
- Validated language data in `.tessdata`:
  `eng`, `jpn`, `jpn_vert`, `chi_sim`, `chi_tra`, `kor`, `osd`
- Program Files writes were blocked for tessdata, so keep language data in the
  project-local `.tessdata` directory and pass `--tessdata-dir .tessdata`.
- OCR was validated on an S6 screenshot with mixed Japanese, English, Chinese,
  and Korean text.

## GPU Check

- `nvidia-smi` is the reliable GPU check on this machine.
- Confirmed GPU:
  - NVIDIA Quadro P2200
  - Driver Version 582.16
  - CUDA Version 13.0
  - about 5GB VRAM
- CPU OCR remains the default unless a later workflow specifically benefits
  from GPU-backed OCR or image processing.

## Commit Scope Note

At the time this file was added, the working tree already contained many
modified strategy, docs, script, and input files. Those existing changes were
not staged by this environment handoff. This note is meant to make the Windows
setup reproducible without silently publishing unrelated content edits.
