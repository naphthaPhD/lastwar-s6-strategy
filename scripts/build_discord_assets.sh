#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="${OUTPUT_DIR:-outputs/discord_assets}"
PNG_DPI="${PNG_DPI:-180}"

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
require_command lualatex
require_command pdftoppm

mkdir -p "$OUTPUT_DIR"
rm -f "$OUTPUT_DIR"/*.pdf "$OUTPUT_DIR"/*.png

markdown_count=0
while IFS= read -r file; do
  stem="$(safe_stem "$file")"
  pdf="$OUTPUT_DIR/${stem}.pdf"
  echo "Markdown -> PDF: $file"
  pandoc "$file" \
    --from=gfm+hard_line_breaks \
    --pdf-engine=lualatex \
    -V documentclass=ltjsarticle \
    -V papersize=a4 \
    -V geometry:margin=18mm \
    -o "$pdf"
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
