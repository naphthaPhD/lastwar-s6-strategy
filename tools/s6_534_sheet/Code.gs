const S6_SHEET_NAMES = {
  MANAGEMENT: '管理表たたき',
  MAP_TEMPLATE: 'マップ表示テンプレ',
  FULL_MAP: '全体マップ',
  PACTS: '連盟盟約状況',
};

const S6_FULL_MAP_RANGE_A1 = 'A1:DR135';
const S6_FULL_MAP_COLORS = {
  self: '#2563eb',
  ally: '#16a34a',
  enemy: '#dc2626',
  trade: '#020617',
  destroyed: '#6b7280',
  unowned: '#000000',
};
const S6_SELF_SERVERS = ['#534'];
const S6_ALLY_SERVERS = ['#509', '#440', '#511'];
const S6_ENEMY_SERVERS = ['#503', '#480', '#523', '#476'];
const S6_OWNER_SIDE_OVERRIDES = {
  self: ['4tH', '59U', '89M', 'CROW', 'Dao', 'JDX', 'KTVS', 'MOE', 'RGWC', 'Ryu1', 'SHA', 'SHA0', 'SKh', 'Skh', 'Trh', 'f4j', 'kOi', 'moca', 'nO9', 'noI', 'sg3', 'w6F'],
  ally: ['0TT', '2N7', 'ANH2', 'AoW', 'BAJ', 'BHE', 'CZX', 'DOLU', 'DaNG', 'FHX', 'GcC', 'GoDs', 'IMP', 'IMp', 'JL2', 'JLO', 'KOCH', 'MOn', 'OOEf', 'OTT', 'OWM', 'SVa', 'SVh', 'SVo', 'SsQ', 'TRh', 'TaW', 'TrX', 'VEX', 'WoW3', 'aTA', 'eXt', 'nv8', 'sbM', 'tWD'],
  enemy: ['299', '476A', '476B', '476C', '476H', '476K', '476M', '476T', '476X', '476Z', '476d', '5DU', 'AAOA', 'ALi', 'ALj', 'ASp', 'BgNa', 'Bye', 'CDF8', 'CDf8', 'COZy', 'Digg', 'EDFS', 'FarM', 'GX99', 'IXM', 'JL0', 'K4TR', 'Kfk', 'Lghs', 'MtG', 'NBNH', 'PmP', 'R6q', 'RCON', 'RING', 'Stj', 'TIKW', 'TkTk', 'UMN', 'UrE', 'WUG', 'WbW', 'YDR', 'fIrE', 'fzn', 'hMt', 'hOe', 'one', 'pSs', 'u3o', 'xjR'],
};
const S6_FULL_MAP_BLOCKS = [
  { startRow: 6, endRow: 46, startColumn: 1, endColumn: 41, area: '#534' },
  { startRow: 6, endRow: 46, startColumn: 42, endColumn: 81, area: '#509' },
  { startRow: 6, endRow: 46, startColumn: 82, endColumn: 122, area: '#503' },
  { startRow: 49, endRow: 89, startColumn: 1, endColumn: 41, area: '#476' },
  { startRow: 49, endRow: 89, startColumn: 82, endColumn: 122, area: '#480' },
  { startRow: 92, endRow: 132, startColumn: 1, endColumn: 41, area: '#523' },
  { startRow: 92, endRow: 132, startColumn: 42, endColumn: 81, area: '#511' },
  { startRow: 92, endRow: 132, startColumn: 82, endColumn: 122, area: '#440' },
];

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('S6#534管理')
    .addItem('全体マップ更新', 'refreshS6FullMapFromManagement')
    .addToUi();
}

function refreshS6FullMapFromManagement() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const managementSheet = ss.getSheetByName(S6_SHEET_NAMES.MANAGEMENT);
  const templateSheet = ss.getSheetByName(S6_SHEET_NAMES.MAP_TEMPLATE);
  if (!managementSheet) throw new Error(`管理表シートが見つかりません: ${S6_SHEET_NAMES.MANAGEMENT}`);
  if (!templateSheet) throw new Error(`マップテンプレートが見つかりません: ${S6_SHEET_NAMES.MAP_TEMPLATE}`);

  const targetSheet = ensureS6Sheet_(ss, S6_SHEET_NAMES.FULL_MAP);
  const templateRange = templateSheet.getRange(S6_FULL_MAP_RANGE_A1);
  const rowCount = templateRange.getNumRows();
  const columnCount = templateRange.getNumColumns();
  const templateValues = templateRange.getDisplayValues();
  const managementMap = buildS6ManagementMap_(managementSheet);
  const allianceServerMap = buildS6AllianceServerMap_(ss);
  const counts = { self: 0, ally: 0, enemy: 0, trade: 0, destroyed: 0, unowned: 0, missing: 0 };

  ensureS6GridSize_(targetSheet, rowCount, columnCount);
  targetSheet.getRange(1, 1, targetSheet.getMaxRows(), targetSheet.getMaxColumns()).breakApart();
  targetSheet.clear();
  copyS6SourceMapRange_(templateRange, targetSheet.getRange(1, 1));
  copyS6MapDimensions_(templateSheet, targetSheet, rowCount, columnCount);
  copyS6MapMerges_(templateRange, targetSheet);
  targetSheet.setFrozenRows(5);
  targetSheet.setHiddenGridlines(true);

  for (let rowIndex = 0; rowIndex < templateValues.length; rowIndex++) {
    const rowNumber = rowIndex + 1;
    const rowValues = templateValues[rowIndex];
    for (let columnIndex = 0; columnIndex < rowValues.length; columnIndex++) {
      const columnNumber = columnIndex + 1;
      const coordinate = normalizeS6MapCoordinate_(rowValues[columnIndex]);
      if (!coordinate) continue;
      const area = s6AreaForFullMapCell_(rowNumber, columnNumber);
      if (!area) continue;
      const key = `${area}:${coordinate}`.toUpperCase();
      const node = managementMap[key];
      if (!node) {
        counts.missing++;
        continue;
      }
      const displayValue = s6FullMapDisplayValue_(node, coordinate);
      const relation = s6FullMapRelation_(node, area, allianceServerMap);
      counts[relation] = (counts[relation] || 0) + 1;
      paintS6FullMapCell_(targetSheet, rowNumber, columnNumber, displayValue, S6_FULL_MAP_COLORS[relation], buildS6FullMapNote_(node, key));
    }
  }

  writeS6FullMapUpdateNote_(targetSheet, counts);
  ss.toast(
    `全体マップ更新: 青${counts.self} / 緑${counts.ally} / 赤${counts.enemy} / 黒${counts.trade} / 灰${counts.destroyed}`,
    'S6#534',
    8
  );
}

function buildS6ManagementMap_(sheet) {
  const values = sheet.getDataRange().getValues();
  if (values.length < 2) return {};
  const headers = values[0].map((value) => String(value || '').trim());
  const index = {
    coord: headers.indexOf('座標'),
    type: headers.indexOf('種別'),
    owner: headers.indexOf('連盟'),
    acquiredAt: headers.indexOf('取得日時(Local Time)'),
    protectUntil: headers.indexOf('保護切れ日時(JST)'),
    remaining: headers.indexOf('保護残り'),
    status: headers.indexOf('状態'),
    nextSlot: headers.indexOf('次応戦枠'),
    memo: headers.indexOf('メモ'),
    area: headers.indexOf('エリア'),
    key: headers.indexOf('位置キー'),
  };
  const result = {};
  for (let rowIndex = 2; rowIndex <= values.length; rowIndex++) {
    const row = values[rowIndex - 1];
    const area = index.area >= 0 ? String(row[index.area] || '').trim() : '';
    const coord = index.coord >= 0 ? String(row[index.coord] || '').trim() : '';
    const keyValue = index.key >= 0 ? String(row[index.key] || '').trim() : '';
    const key = (keyValue || (area && coord ? `${area}:${coord}` : '')).toUpperCase();
    if (!key || key.indexOf(':') === -1) continue;
    result[key] = {
      rowNumber: rowIndex,
      key,
      area,
      coord,
      type: index.type >= 0 ? String(row[index.type] || '').trim() : '',
      owner: index.owner >= 0 ? String(row[index.owner] || '').trim() : '',
      acquiredAt: index.acquiredAt >= 0 ? row[index.acquiredAt] : '',
      protectUntil: index.protectUntil >= 0 ? row[index.protectUntil] : '',
      remaining: index.remaining >= 0 ? row[index.remaining] : '',
      status: index.status >= 0 ? String(row[index.status] || '').trim() : '',
      nextSlot: index.nextSlot >= 0 ? row[index.nextSlot] : '',
      memo: index.memo >= 0 ? String(row[index.memo] || '').trim() : '',
    };
  }
  return result;
}

function buildS6AllianceServerMap_(ss) {
  const result = {};
  const pactSheet = ss.getSheetByName(S6_SHEET_NAMES.PACTS);
  if (!pactSheet || pactSheet.getLastRow() < 2) return result;
  const values = pactSheet.getDataRange().getValues();
  for (let rowIndex = 1; rowIndex < values.length; rowIndex++) {
    addS6AllianceServer_(result, values[rowIndex][0], values[rowIndex][1]);
    addS6AllianceServer_(result, values[rowIndex][2], values[rowIndex][3]);
  }
  return result;
}

function addS6AllianceServer_(map, alliance, server) {
  const tag = normalizeS6AllianceTag_(alliance);
  const normalizedServer = normalizeS6Server_(server);
  if (tag && normalizedServer && !map[tag]) map[tag] = normalizedServer;
}

function normalizeS6MapCoordinate_(value) {
  const text = String(value || '').trim();
  return /^[A-Ka-k]-(?:[1-9]|1[0-9]|2[0-1])$/.test(text) ? text : '';
}

function s6AreaForFullMapCell_(rowNumber, columnNumber) {
  for (let i = 0; i < S6_FULL_MAP_BLOCKS.length; i++) {
    const block = S6_FULL_MAP_BLOCKS[i];
    if (
      rowNumber >= block.startRow &&
      rowNumber <= block.endRow &&
      columnNumber >= block.startColumn &&
      columnNumber <= block.endColumn
    ) {
      return block.area;
    }
  }
  return '';
}

function s6FullMapDisplayValue_(node, fallbackCoordinate) {
  if (isS6DestroyedNode_(node)) return '破壊';
  if (node.type === '交易地') return '交易地';
  return node.owner || fallbackCoordinate;
}

function s6FullMapRelation_(node, area, allianceServerMap) {
  if (isS6DestroyedNode_(node)) return 'destroyed';
  if (node.type === '交易地') return 'trade';
  const owner = normalizeS6AllianceTag_(node.owner);
  if (!owner || isS6UnownedOwner_(owner)) return 'unowned';
  const overrideRelation = s6OwnerSideOverride_(owner);
  if (overrideRelation) return overrideRelation;
  const server = s6ServerForOwner_(owner, area, allianceServerMap);
  if (S6_SELF_SERVERS.indexOf(server) !== -1) return 'self';
  if (S6_ALLY_SERVERS.indexOf(server) !== -1) return 'ally';
  if (S6_ENEMY_SERVERS.indexOf(server) !== -1) return 'enemy';
  return 'unowned';
}

function s6OwnerSideOverride_(owner) {
  const tag = normalizeS6AllianceTag_(owner);
  if (S6_OWNER_SIDE_OVERRIDES.self.indexOf(tag) !== -1) return 'self';
  if (S6_OWNER_SIDE_OVERRIDES.ally.indexOf(tag) !== -1) return 'ally';
  if (S6_OWNER_SIDE_OVERRIDES.enemy.indexOf(tag) !== -1) return 'enemy';
  return '';
}

function s6ServerForOwner_(owner, area, allianceServerMap) {
  const directServer = normalizeS6Server_(owner);
  if (directServer) return directServer;
  const mappedServer = allianceServerMap[normalizeS6AllianceTag_(owner)];
  if (mappedServer) return mappedServer;
  return normalizeS6Server_(area);
}

function normalizeS6Server_(value) {
  const text = String(value || '').trim();
  const match = text.match(/#?(534|509|440|511|503|480|523|476)/);
  return match ? `#${match[1]}` : '';
}

function normalizeS6AllianceTag_(value) {
  return String(value || '').trim();
}

function isS6DestroyedNode_(node) {
  return String(node.type || '').indexOf('破壊') !== -1 ||
    String(node.owner || '').indexOf('破壊') !== -1 ||
    String(node.status || '').indexOf('破壊') !== -1 ||
    (String(node.memo || '').indexOf('破壊') !== -1 && !node.owner);
}

function isS6UnownedOwner_(owner) {
  const text = String(owner || '').trim();
  return text === '' || text === 'unknown' || text === '未取得' || text === '未登録' || text === '中立' || text === '中立/未登録';
}

function paintS6FullMapCell_(sheet, rowNumber, columnNumber, value, fontColor, note) {
  const cell = sheet.getRange(rowNumber, columnNumber);
  const mergedRanges = cell.getMergedRanges();
  const paintRange = mergedRanges.length > 0 ? mergedRanges[0] : cell;
  paintRange.setValue(value).setFontColor(fontColor || '#000000').setFontWeight('bold');
  paintRange.getCell(1, 1).setNote(note);
}

function buildS6FullMapNote_(node, key) {
  const lines = [
    key,
    `種別: ${node.type || ''}`,
    `所有連盟: ${node.owner || ''}`,
    `取得日時: ${formatS6MaybeDate_(node.acquiredAt)}`,
    `保護切れ: ${formatS6MaybeDate_(node.protectUntil)}`,
    `状態: ${node.status || ''}`,
    `管理表行: ${node.rowNumber}`,
  ];
  if (node.memo) lines.push(`メモ: ${node.memo}`);
  return lines.join('\n');
}

function writeS6FullMapUpdateNote_(sheet, counts) {
  const updatedAt = Utilities.formatDate(new Date(), getS6TimeZone_(), 'yyyy/MM/dd HH:mm:ss');
  sheet.getRange('A1').setNote(
    `全体マップ更新: ${updatedAt}\n` +
    `青(#534): ${counts.self || 0}\n` +
    `緑(#509/#440/#511): ${counts.ally || 0}\n` +
    `赤(#503/#480/#523/#476): ${counts.enemy || 0}\n` +
    `黒(交易地): ${counts.trade || 0}\n` +
    `灰(破壊): ${counts.destroyed || 0}\n` +
    `未取得/未判定: ${counts.unowned || 0}\n` +
    `管理表未一致: ${counts.missing || 0}`
  );
}

function copyS6SourceMapRange_(sourceRange, targetRange) {
  try {
    sourceRange.copyTo(targetRange);
  } catch (error) {
    const rowCount = sourceRange.getNumRows();
    const columnCount = sourceRange.getNumColumns();
    const fallbackRange = targetRange.offset(0, 0, rowCount, columnCount);
    fallbackRange.setValues(sourceRange.getValues());
    fallbackRange.setBackgrounds(sourceRange.getBackgrounds());
    fallbackRange.setFontColors(sourceRange.getFontColors());
    fallbackRange.setFontWeights(sourceRange.getFontWeights());
    fallbackRange.setHorizontalAlignments(sourceRange.getHorizontalAlignments());
    fallbackRange.setVerticalAlignments(sourceRange.getVerticalAlignments());
  }
}

function copyS6MapDimensions_(sourceSheet, targetSheet, rowCount, columnCount) {
  for (let column = 1; column <= columnCount; column++) {
    targetSheet.setColumnWidth(column, sourceSheet.getColumnWidth(column));
  }
  for (let row = 1; row <= rowCount; row++) {
    targetSheet.setRowHeight(row, sourceSheet.getRowHeight(row));
  }
}

function copyS6MapMerges_(sourceRange, targetSheet) {
  const sourceStartRow = sourceRange.getRow();
  const sourceStartColumn = sourceRange.getColumn();
  sourceRange.getMergedRanges().forEach((mergedRange) => {
    const rowOffset = mergedRange.getRow() - sourceStartRow;
    const columnOffset = mergedRange.getColumn() - sourceStartColumn;
    if (rowOffset < 0 || columnOffset < 0) return;
    targetSheet
      .getRange(rowOffset + 1, columnOffset + 1, mergedRange.getNumRows(), mergedRange.getNumColumns())
      .merge();
  });
}

function ensureS6Sheet_(ss, name) {
  return ss.getSheetByName(name) || ss.insertSheet(name);
}

function ensureS6GridSize_(sheet, rowCount, columnCount) {
  if (sheet.getMaxRows() < rowCount) {
    sheet.insertRowsAfter(sheet.getMaxRows(), rowCount - sheet.getMaxRows());
  }
  if (sheet.getMaxColumns() < columnCount) {
    sheet.insertColumnsAfter(sheet.getMaxColumns(), columnCount - sheet.getMaxColumns());
  }
}

function formatS6MaybeDate_(value) {
  if (Object.prototype.toString.call(value) === '[object Date]' && !isNaN(value.getTime())) {
    return Utilities.formatDate(value, getS6TimeZone_(), 'yyyy/MM/dd HH:mm');
  }
  return String(value || '');
}

function getS6TimeZone_() {
  return Session.getScriptTimeZone() || 'Asia/Tokyo';
}
