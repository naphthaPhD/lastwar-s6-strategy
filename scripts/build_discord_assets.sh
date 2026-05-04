#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="${OUTPUT_DIR:-outputs/discord_assets}"
PNG_DPI="${PNG_DPI:-180}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
STYLE_FILE="$SCRIPT_DIR/discord_assets_style.html"

fail() {
  echo "error: $*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "required command not found: $1"
}

find_libreoffice() {
  if command -v libreoffice >/dev/null 2>&1; then
    command -v libreoffice
  elif command -v soffice >/dev/null 2>&1; then
    command -v soffice
  elif [[ -x /Applications/LibreOffice.app/Contents/MacOS/soffice ]]; then
    printf '%s\n' "/Applications/LibreOffice.app/Contents/MacOS/soffice"
  else
    return 1
  fi
}

find_chrome() {
  if command -v google-chrome >/dev/null 2>&1; then
    command -v google-chrome
  elif command -v google-chrome-stable >/dev/null 2>&1; then
    command -v google-chrome-stable
  elif command -v chromium >/dev/null 2>&1; then
    command -v chromium
  elif command -v chromium-browser >/dev/null 2>&1; then
    command -v chromium-browser
  elif [[ -x /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome ]]; then
    printf '%s\n' "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  elif [[ -x /Applications/Chromium.app/Contents/MacOS/Chromium ]]; then
    printf '%s\n' "/Applications/Chromium.app/Contents/MacOS/Chromium"
  else
    return 1
  fi
}

absolute_path() {
  local dir
  dir="$(cd "$(dirname "$1")" && pwd -P)"
  printf '%s/%s' "$dir" "$(basename "$1")"
}

safe_stem() {
  local path="${1#./}"
  local stem="${path%.*}"
  stem="${stem//\//__}"
  stem="${stem// /_}"
  printf '%s' "$stem" | LC_ALL=C tr -c 'A-Za-z0-9_.-' '_'
}

source_find_base=(
  .
  \( -path "./.git" -o -path "./node_modules" -o -path "./outputs" -o -path "./map_exports" \) -prune
  -o
)

require_command pandoc
require_command pdftoppm
[[ -f "$STYLE_FILE" ]] || fail "style file not found: $STYLE_FILE"

mkdir -p "$OUTPUT_DIR"
rm -f "$OUTPUT_DIR"/*.html "$OUTPUT_DIR"/*.pdf "$OUTPUT_DIR"/*.png

markdown_count=0
while IFS= read -r file; do
  chrome_bin="$(find_chrome)" || fail "Google Chrome or Chromium is required to convert Markdown files"
  stem="$(safe_stem "$file")"
  tmp_dir="$(mktemp -d)"
  html="$tmp_dir/${stem}.html"
  pdf="$OUTPUT_DIR/${stem}.pdf"
  echo "Markdown -> HTML -> PDF: $file"
  pandoc "$file" \
    --from=gfm+hard_line_breaks \
    --standalone \
    --metadata title="$file" \
    --include-in-header="$STYLE_FILE" \
    -o "$html"
  "$chrome_bin" \
    --headless \
    --disable-gpu \
    --disable-dev-shm-usage \
    --no-sandbox \
    --no-pdf-header-footer \
    --print-to-pdf-no-header \
    --print-to-pdf="$(absolute_path "$pdf")" \
    "file://$(absolute_path "$html")"
  rm -rf "$tmp_dir"
  markdown_count=$((markdown_count + 1))
done < <(find "${source_find_base[@]}" -type f -name "*.md" -print | sort)

excel_count=0
while IFS= read -r file; do
  libreoffice_bin="$(find_libreoffice)" || fail "LibreOffice is required to convert Excel files"
  stem="$(safe_stem "$file")"
  tmp_dir="$(mktemp -d)"
  echo "Excel -> PDF: $file"
  "$libreoffice_bin" --headless --convert-to pdf --outdir "$tmp_dir" "$file"
  converted_pdf="$(find "$tmp_dir" -maxdepth 1 -type f -iname "*.pdf" -print -quit)"
  [[ -n "$converted_pdf" ]] || fail "LibreOffice did not create a PDF for $file"
  mv "$converted_pdf" "$OUTPUT_DIR/${stem}.pdf"
  rm -rf "$tmp_dir"
  excel_count=$((excel_count + 1))
done < <(find "${source_find_base[@]}" -type f \( -iname "*.xls" -o -iname "*.xlsx" -o -iname "*.xlsm" \) -print | sort)

pdf_count=0
for pdf in "$OUTPUT_DIR"/*.pdf; do
  [[ -e "$pdf" ]] || continue
  echo "PDF -> PNG: $pdf"
  pdftoppm -png -r "$PNG_DPI" "$pdf" "${pdf%.pdf}"
  pdf_count=$((pdf_count + 1))
done

if [[ "$pdf_count" -eq 0 ]]; then
  fail "no Markdown or Excel files were converted"
fi

echo "Built assets in $OUTPUT_DIR"
echo "Markdown files: $markdown_count"
echo "Excel files: $excel_count"
echo "PDF files: $pdf_count"
