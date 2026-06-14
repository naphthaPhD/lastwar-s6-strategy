# JDX power sheet update log

## Date

2026-05-25

## Context

JDX power screenshot automation processed the local synced screenshot folder and reflected the latest roster-matched power data into Google Sheets.

## Source note

- Local note: `jdx_run_note_latest.md`
- Source folder: `G:\マイドライブ\lastwar\S6\JDX戦力スクショ`
- Target spreadsheet: `JDX戦力など`
- Target sheet/range scope: `現在週 A:G`

## Key results

1. Processed screenshots `IMG_1055.PNG` through `IMG_1084.PNG`.
2. Updated only clear, roster-matched current-week values in columns `D:G`.
3. Did not overwrite rank or total power.
4. Google Sheets API reported 18 updated rows and 69 updated cells.
5. Verified `戦力分析` recalculated at `2026/05/25 23:36:47`.
6. Post-update counts were:
   - 一軍帯回答数: 68
   - 一軍戦力値回答数: 64
   - 一軍帯未回答者数: 28
   - 一軍戦力値未回答数: 32
7. Moved root `IMG_*.PNG` files to `G:\マイドライブ\lastwar\S6\JDX戦力スクショ\処理済み`.
8. After cleanup, root PNG remaining count was 0 and processed PNG count was 81.

## Notes

- Older `2026/05/24` and `2026/05/25 18:05` images were treated as duplicate or older captures after representative inspection.
- Temporary contact sheets were generated locally under `C:\Users\kitazaki\Documents\S6\outputs\jdx_screenshot_contact` for visual verification.
- The root local note itself is not treated as the repository source of truth; this timeline file is the durable repo copy.
