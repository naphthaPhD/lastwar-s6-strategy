const SHEET_NAMES = {
  LIST: '漁場一覧',
  EVENTS: 'イベント一覧',
  SIMULATOR: 'シミュレーター',
  CALENDAR: 'カレンダー',
  LINE_DEFINITIONS: 'ライン定義',
  ROUTE_CHECK: '侵攻ルート確認',
};

const LIST_HEADERS = [
  'エリア',
  '位置キー',
  '漁場名',
  '所有連盟',
  '防衛ライン',
  'ライン順序',
  'ライン方向',
  '座標',
  '現在保護切れ日時',
  '応戦時間帯',
  'ワンパン必要',
  'ワンパン役',
  '備考',
  '最終操作日時',
  '最終操作',
  '次回保護切れ日時',
  '次回応戦時間帯',
  '放棄可否',
  '再取得不可終了',
  '更新時刻',
  '表示順',
  '状態ラベル',
  '状態表示',
  '保護パン後の次回保護切れ',
  '安全時間補正後',
];

const EVENT_HEADERS = [
  '保護切れ日時',
  '応戦時間帯',
  '対象数',
  'エリア',
  '漁場名',
  '位置キー',
  '所有連盟',
  '防衛ライン',
  '座標',
  'ワンパン必要',
  'ワンパン役',
  '備考',
  '状態ラベル',
  '状態表示',
];

const CALENDAR_HEADERS = [
  '状態ラベル',
  '表示名',
  '対象数',
  '対象漁場',
  'ワンパン候補',
  '保護パン後の状態',
];

const ROUTE_CHECK_HEADERS = [
  'エリア',
  '侵攻ルート',
  '対象漁場',
  '開放枠順',
  '判定',
  '警告',
];

const LINE_DEFINITION_HEADERS = [
  'エリア',
  'ライン軸',
  '外側からの方向',
  'ライン1',
  'ライン2',
  'ライン3',
  '位置キー例',
  'スクショフォルダ例',
  '備考',
];

const LINE_DEFINITION_ROWS = [
  ['#534', 'letter', 'A→B→C', 'A列', 'B列', 'C列', '#534:A-1', '漁場スクショ/534/ABC', '#534は従来どおりA/B/Cを防衛ラインにする'],
  ['#509', 'number', 'A→B→C→D', '1列', '3列', '5列', '#509:A-1', '漁場スクショ/509/ABC', '#509はA-1,B-1,C-1,D-1のように同じ数字でラインを見る'],
  ['#476', 'letter_reverse', 'K→J→I', 'K列', 'J列', 'I列', '#476:K-1', '漁場スクショ/476/KJI', '#476は逆向きにK,J,Iと下りるラインを見る'],
  ['#440', '未定', '要確認', '', '', '', '#440:A-1', '漁場スクショ/440/', '必要になったら方向定義を追加'],
  ['#503', '未定', '要確認', '', '', '', '#503:A-1', '漁場スクショ/503/', '必要になったら方向定義を追加'],
  ['#480', '未定', '要確認', '', '', '', '#480:A-1', '漁場スクショ/480/', '必要になったら方向定義を追加'],
  ['#523', '未定', '要確認', '', '', '', '#523:A-1', '漁場スクショ/523/', '必要になったら方向定義を追加'],
];

const AREA_VALUES = ['#534', '#509', '#476', '#440', '#503', '#480', '#523'];
const LINE_VALUES = ['A列', 'B列', 'C列', 'D列', 'K列', 'J列', 'I列', '1列', '3列', '5列', '7列', '9列'];
const ONE_PUNCH_VALUES = ['自動:候補', '自動:7時要判断', '自動:不要', '必要', '不要', '見送り', '要確認'];
const OPERATION_VALUES = ['取得', '保護パン', '放棄'];

const RESPONSE_HOURS = [7, 15, 23];
const SAFE_RESPONSE_HOUR = 15;
const BATTLE_DAYS = [3, 6]; // Sunday = 0, Wednesday = 3, Saturday = 6.
const MS_PER_DAY = 24 * 60 * 60 * 1000;
const ABANDON_LOCK_MINUTES = 60;
const REACQUIRE_LOCK_HOURS = 24;
const DISPLAY_ORDER_COLUMN = 21;

const OPERATIONAL_STATES = [
  { label: 'WED_23', display: '水曜23時', day: 3, hour: 23, next: 'SUN_07' },
  { label: 'THU_07', display: '木曜7時', day: 4, hour: 7, next: 'SAT_23' },
  { label: 'SAT_23', display: '土曜23時', day: 6, hour: 23, next: 'THU_07' },
  { label: 'SUN_07', display: '日曜7時', day: 0, hour: 7, next: 'WED_23' },
];

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('漁場保護')
    .addItem('初期セットアップ', 'setupFisheryProtectionWorkbook')
    .addItem('一覧を再計算', 'refreshFisheryProtectionSystem')
    .addItem('シミュレーター計算', 'runFisherySimulator')
    .addToUi();
}

function setupFisheryProtectionWorkbook() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const listSheet = ensureSheet_(ss, SHEET_NAMES.LIST);
  const eventsSheet = ensureSheet_(ss, SHEET_NAMES.EVENTS);
  const simulatorSheet = ensureSheet_(ss, SHEET_NAMES.SIMULATOR);
  const calendarSheet = ensureSheet_(ss, SHEET_NAMES.CALENDAR);
  const lineDefinitionSheet = ensureSheet_(ss, SHEET_NAMES.LINE_DEFINITIONS);
  const routeCheckSheet = ensureSheet_(ss, SHEET_NAMES.ROUTE_CHECK);

  setupListSheet_(listSheet);
  setupEventsSheet_(eventsSheet);
  setupSimulatorSheet_(simulatorSheet);
  setupCalendarSheet_(calendarSheet);
  setupLineDefinitionSheet_(lineDefinitionSheet);
  setupRouteCheckSheet_(routeCheckSheet);
  refreshFisheryProtectionSystem();
}

function refreshFisheryProtectionSystem() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const listSheet = ensureSheet_(ss, SHEET_NAMES.LIST);
  ensureListHeaders_(listSheet);

  const values = listSheet.getDataRange().getValues();
  if (values.length < 2) {
    buildEventsSheet_(ss, []);
    buildCalendarSheet_(ss, []);
    buildRouteCheckSheet_(ss, []);
    return;
  }

  const now = new Date();
  const outputRows = [];
  const eventRows = [];
  for (let rowIndex = 1; rowIndex < values.length; rowIndex++) {
    const row = normalizeRowLength_(values[rowIndex], LIST_HEADERS.length);
    if (!row.some((value) => value !== '' && value !== null)) {
      outputRows.push(row);
      continue;
    }

    const currentProtectUntil = parseDate_(row[8]);
    const operationAt = parseDate_(row[13]);
    const operation = String(row[14] || '').trim();
    let nextProtectUntil = null;

    if (operationAt) {
      if (operation === '放棄') {
        nextProtectUntil = calculateAbandonProtectionEnd_(operationAt);
        row[18] = addHours_(operationAt, REACQUIRE_LOCK_HOURS);
      } else {
        nextProtectUntil = calculateNextProtectionEnd_(operationAt);
        row[18] = '';
      }
    } else if (currentProtectUntil) {
      nextProtectUntil = currentProtectUntil;
      row[18] = '';
    }

    const operationalProtectUntil = normalizeOperationalSlot_(nextProtectUntil);
    const state = getProtectionState_(operationalProtectUntil);
    const punchNext = state ? nextProtectionAfterState_(state.label, operationalProtectUntil) : null;

    row[9] = operationalProtectUntil ? formatResponseSlot_(operationalProtectUntil) : '';
    row[15] = operationalProtectUntil || '';
    row[16] = operationalProtectUntil ? formatResponseSlot_(operationalProtectUntil) : '';
    row[17] = canAbandonAt_(now) ? '可' : '不可';
    row[19] = now;
    row[20] = buildDisplayOrder_(row[0], row[2], row[5]);
    row[21] = state ? state.label : '';
    row[22] = state ? state.display : '';
    row[23] = punchNext || '';
    row[24] = operationalProtectUntil || '';

    if (!row[1] && row[0] && row[2]) {
      row[1] = `${row[0]}:${row[2]}`;
    }

    if (shouldReplaceAutoCandidate_(row[10])) {
      row[10] = buildOnePunchCandidate_(row[4], operationalProtectUntil);
    }

    outputRows.push(row);
    if (operationalProtectUntil) {
      eventRows.push({
        area: row[0],
        key: row[1],
        protectUntil: operationalProtectUntil,
        slot: formatResponseSlot_(operationalProtectUntil),
        name: row[2],
        owner: row[3],
        line: row[4],
        coord: row[7],
        onePunch: row[10],
        assignee: row[11],
        note: row[12],
        stateLabel: row[21],
        stateDisplay: row[22],
        displayOrder: row[20],
      });
    }
  }

  if (outputRows.length > 0) {
    listSheet.getRange(2, 1, outputRows.length, LIST_HEADERS.length).setValues(outputRows);
    listSheet.getRange(2, 1, outputRows.length, LIST_HEADERS.length).sort({ column: DISPLAY_ORDER_COLUMN, ascending: true });
  }
  buildEventsSheet_(ss, eventRows);
  buildCalendarSheet_(ss, eventRows);
  buildRouteCheckSheet_(ss, eventRows);
}

function runFisherySimulator() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ensureSheet_(ss, SHEET_NAMES.SIMULATOR);
  const operation = String(sheet.getRange('B2').getValue() || '').trim();
  const operationAt = parseDate_(sheet.getRange('B3').getValue());

  if (!operationAt) {
    sheet.getRange('B6:B10').clearContent();
    sheet.getRange('B6').setValue('日時を入力してください');
    return;
  }

  const nextProtectUntil =
    operation === '放棄'
      ? calculateAbandonProtectionEnd_(operationAt)
      : calculateNextProtectionEnd_(operationAt);
  const operationalProtectUntil = normalizeOperationalSlot_(nextProtectUntil);
  const state = getProtectionState_(operationalProtectUntil);

  sheet.getRange('B6').setValue(operationalProtectUntil);
  sheet.getRange('B7').setValue(formatResponseSlot_(operationalProtectUntil));
  sheet.getRange('B8').setValue(operation === '放棄' ? addHours_(operationAt, REACQUIRE_LOCK_HOURS) : '');
  sheet.getRange('B9').setValue(canAbandonAt_(operationAt) ? '可' : '不可');
  sheet.getRange('B10').setValue(
    operation === '放棄'
      ? `放棄時刻から次の応戦枠を基準に1枠後ろへ進め、15時枠は23時枠へ繰り下げ。状態=${state ? state.label : '要確認'}`
      : `次の宣戦日の同時刻から1枠後ろへ進め、15時枠は23時枠へ繰り下げ。状態=${state ? state.label : '要確認'}`
  );
}

function NEXT_PROTECTION_END(acquiredAt) {
  const result = calculateNextProtectionEnd_(acquiredAt);
  return result || '';
}

function ABANDON_PROTECTION_END(abandonedAt) {
  const result = calculateAbandonProtectionEnd_(abandonedAt);
  return result || '';
}

function CAN_ABANDON(at) {
  const date = parseDate_(at);
  return date ? canAbandonAt_(date) : '';
}

function PROTECTION_STATE(protectUntil) {
  const state = getProtectionState_(normalizeOperationalSlot_(protectUntil));
  return state ? state.label : '';
}

function PROTECTION_STATE_NAME(protectUntil) {
  const state = getProtectionState_(normalizeOperationalSlot_(protectUntil));
  return state ? state.display : '';
}

function NEXT_AFTER_PROTECTION_PUNCH(protectUntil) {
  const normalized = normalizeOperationalSlot_(protectUntil);
  const state = getProtectionState_(normalized);
  return state ? nextProtectionAfterState_(state.label, normalized) : '';
}

function setupListSheet_(sheet) {
  ensureListHeaders_(sheet);
  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, LIST_HEADERS.length).setFontWeight('bold').setBackground('#1f4e79').setFontColor('#ffffff');
  sheet.getRange('A2:A').setDataValidation(listValidation_(AREA_VALUES));
  sheet.getRange('E2:E').setDataValidation(listValidation_(LINE_VALUES));
  sheet.getRange('K2:K').setDataValidation(listValidation_(ONE_PUNCH_VALUES));
  sheet.getRange('O2:O').setDataValidation(listValidation_(OPERATION_VALUES));
  sheet.getRange('I:I').setNumberFormat('yyyy/mm/dd hh:mm');
  sheet.getRange('N:N').setNumberFormat('yyyy/mm/dd hh:mm');
  sheet.getRange('P:P').setNumberFormat('yyyy/mm/dd hh:mm');
  sheet.getRange('S:T').setNumberFormat('yyyy/mm/dd hh:mm');
  sheet.getRange('X:Y').setNumberFormat('yyyy/mm/dd hh:mm');
  sheet.hideColumns(DISPLAY_ORDER_COLUMN);
  sheet.autoResizeColumns(1, LIST_HEADERS.length);
}

function setupEventsSheet_(sheet) {
  sheet.clear();
  sheet.getRange(1, 1, 1, EVENT_HEADERS.length).setValues([EVENT_HEADERS]);
  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, EVENT_HEADERS.length).setFontWeight('bold').setBackground('#674ea7').setFontColor('#ffffff');
  sheet.getRange('A:A').setNumberFormat('yyyy/mm/dd hh:mm');
}

function setupCalendarSheet_(sheet) {
  sheet.clear();
  sheet.getRange(1, 1, 1, CALENDAR_HEADERS.length).setValues([CALENDAR_HEADERS]);
  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, CALENDAR_HEADERS.length).setFontWeight('bold').setBackground('#38761d').setFontColor('#ffffff');
}

function setupRouteCheckSheet_(sheet) {
  sheet.clear();
  sheet.getRange(1, 1, 1, ROUTE_CHECK_HEADERS.length).setValues([ROUTE_CHECK_HEADERS]);
  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, ROUTE_CHECK_HEADERS.length).setFontWeight('bold').setBackground('#a64d1f').setFontColor('#ffffff');
}

function setupLineDefinitionSheet_(sheet) {
  sheet.clear();
  sheet.getRange(1, 1, 1, LINE_DEFINITION_HEADERS.length).setValues([LINE_DEFINITION_HEADERS]);
  sheet.getRange(2, 1, LINE_DEFINITION_ROWS.length, LINE_DEFINITION_HEADERS.length).setValues(LINE_DEFINITION_ROWS);
  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, LINE_DEFINITION_HEADERS.length).setFontWeight('bold').setBackground('#555555').setFontColor('#ffffff');
  sheet.autoResizeColumns(1, LINE_DEFINITION_HEADERS.length);
}

function setupSimulatorSheet_(sheet) {
  sheet.clear();
  sheet.getRange('A1:D1').setValues([['項目', '入力/出力', '補足', '例']]);
  sheet.getRange('A2:D10').setValues([
    ['操作', '取得', '取得 / 保護パン / 放棄', '保護パンは通常取得と同じ計算'],
    ['操作日時', '', 'yyyy/mm/dd hh:mm', '2026/06/03 23:00'],
    ['', '', '', ''],
    ['出力', '', '', ''],
    ['次回保護切れ日時', '', '', ''],
    ['次回応戦時間帯', '', '', ''],
    ['再取得不可終了', '', '放棄時のみ', ''],
    ['その時刻に放棄可能か', '', '応戦1時間前から不可', ''],
    ['計算メモ', '', '', ''],
  ]);
  sheet.getRange('B2').setDataValidation(listValidation_(OPERATION_VALUES));
  sheet.getRange('B3').setNumberFormat('yyyy/mm/dd hh:mm');
  sheet.getRange('B6').setNumberFormat('yyyy/mm/dd hh:mm');
  sheet.getRange('B8').setNumberFormat('yyyy/mm/dd hh:mm');
  sheet.getRange('A1:D1').setFontWeight('bold').setBackground('#3c78d8').setFontColor('#ffffff');
  sheet.autoResizeColumns(1, 4);
}

function buildEventsSheet_(ss, events) {
  const sheet = ensureSheet_(ss, SHEET_NAMES.EVENTS);
  setupEventsSheet_(sheet);
  const sorted = events.slice().sort((a, b) => a.protectUntil - b.protectUntil || String(a.name).localeCompare(String(b.name)));
  const counts = {};
  sorted.forEach((event) => {
    const key = event.protectUntil.getTime();
    counts[key] = (counts[key] || 0) + 1;
  });
  const rows = sorted.map((event) => [
    event.protectUntil,
    event.slot,
    counts[event.protectUntil.getTime()],
    event.area,
    event.name,
    event.key,
    event.owner,
    event.line,
    event.coord,
    event.onePunch,
    event.assignee,
    event.note,
    event.stateLabel,
    event.stateDisplay,
  ]);
  if (rows.length > 0) {
    sheet.getRange(2, 1, rows.length, EVENT_HEADERS.length).setValues(rows);
  }
  sheet.autoResizeColumns(1, EVENT_HEADERS.length);
}

function buildCalendarSheet_(ss, events) {
  const sheet = ensureSheet_(ss, SHEET_NAMES.CALENDAR);
  setupCalendarSheet_(sheet);
  const eventMap = {};
  events.forEach((event) => {
    const key = event.stateLabel;
    if (!eventMap[key]) eventMap[key] = [];
    eventMap[key].push(event);
  });

  const rows = OPERATIONAL_STATES.map((state) => {
    const key = state.label;
    const slotEvents = eventMap[key] || [];
    const nextState = findState_(state.next);
    return [
      state.label,
      state.display,
      slotEvents.length,
      slotEvents.map((event) => event.key || `${event.area || ''}:${event.name}`).join('\n'),
      slotEvents
        .filter((event) => String(event.onePunch || '').indexOf('候補') !== -1 || String(event.onePunch || '').indexOf('必要') !== -1)
        .map((event) => event.key || `${event.area || ''}:${event.name}`)
        .join('\n'),
      nextState ? `${nextState.label}（${nextState.display}）` : '',
    ];
  });
  if (rows.length > 0) {
    sheet.getRange(2, 1, rows.length, CALENDAR_HEADERS.length).setValues(rows);
  }
  sheet.autoResizeColumns(1, CALENDAR_HEADERS.length);
}

function buildRouteCheckSheet_(ss, events) {
  const sheet = ensureSheet_(ss, SHEET_NAMES.ROUTE_CHECK);
  setupRouteCheckSheet_(sheet);
  const routeMap = {};
  events.forEach((event) => {
    const area = String(event.area || '').trim();
    const line = String(event.line || '').trim();
    if (!area || !line || !event.stateLabel) return;
    const routeKey = `${area}\t${line}`;
    if (!routeMap[routeKey]) routeMap[routeKey] = [];
    routeMap[routeKey].push(event);
  });

  const rows = Object.keys(routeMap).sort().map((routeKey) => {
    const parts = routeKey.split('\t');
    const routeEvents = routeMap[routeKey].sort((a, b) => Number(a.displayOrder || 0) - Number(b.displayOrder || 0));
    const labels = routeEvents.map((event) => event.stateDisplay);
    const hasConsecutiveSame = labels.some((label, index) => index > 0 && label === labels[index - 1]);
    return [
      parts[0],
      parts[1],
      routeEvents.map((event) => event.key).join('\n'),
      labels.join(' → '),
      hasConsecutiveSame ? '危険' : '分散',
      hasConsecutiveSame ? '危険：同じ開放枠が連続。同時突破リスク高' : '分散：時間差あり',
    ];
  });
  if (rows.length > 0) {
    sheet.getRange(2, 1, rows.length, ROUTE_CHECK_HEADERS.length).setValues(rows);
  }
  sheet.autoResizeColumns(1, ROUTE_CHECK_HEADERS.length);
}

function calculateNextProtectionEnd_(acquiredAt) {
  const acquired = parseDate_(acquiredAt);
  if (!acquired) return null;
  const baseHour = snapResponseHour_(acquired);
  const sameHourOnNextBattleDay = nextBattleDateAtHourAfter_(acquired, baseHour);
  return advanceOneOperationalSlot_(sameHourOnNextBattleDay);
}

function calculateAbandonProtectionEnd_(abandonedAt) {
  const abandoned = parseDate_(abandonedAt);
  if (!abandoned) return null;
  const nextSlot = nextResponseSlotAtOrAfter_(abandoned);
  return advanceOneOperationalSlot_(nextSlot);
}

function advanceOneOperationalSlot_(slotDate) {
  let next = advanceOneResponseSlot_(slotDate);
  if (next.getHours() === SAFE_RESPONSE_HOUR) {
    next = advanceOneResponseSlot_(next);
  }
  return next;
}

function normalizeOperationalSlot_(date) {
  const parsed = parseDate_(date);
  if (!parsed) return null;
  let normalized = new Date(parsed.getTime());
  while (normalized.getHours() === SAFE_RESPONSE_HOUR) {
    normalized = advanceOneResponseSlot_(normalized);
  }
  return normalized;
}

function getProtectionState_(date) {
  if (!date) return null;
  const normalized = normalizeOperationalSlot_(date);
  return OPERATIONAL_STATES.find((state) => state.day === normalized.getDay() && state.hour === normalized.getHours()) || null;
}

function nextProtectionAfterState_(stateLabel, fromDate) {
  const currentState = findState_(stateLabel);
  const parsed = parseDate_(fromDate);
  if (!currentState || !parsed) return null;
  const nextState = findState_(currentState.next);
  return nextState ? nextOccurrenceAfter_(parsed, nextState.day, nextState.hour) : null;
}

function nextOccurrenceAfter_(fromDate, day, hour) {
  const base = stripTime_(fromDate);
  for (let offset = 0; offset <= 10; offset++) {
    const candidate = new Date(base.getTime() + offset * MS_PER_DAY);
    candidate.setHours(hour, 0, 0, 0);
    if (candidate.getDay() === day && candidate.getTime() > fromDate.getTime()) return candidate;
  }
  throw new Error('次の4状態枠を計算できませんでした');
}

function findState_(label) {
  return OPERATIONAL_STATES.find((state) => state.label === label) || null;
}

function advanceOneResponseSlot_(slotDate) {
  const date = new Date(slotDate.getTime());
  const hour = date.getHours();
  if (hour === 7) {
    date.setHours(15, 0, 0, 0);
  } else if (hour === 15) {
    date.setHours(23, 0, 0, 0);
  } else {
    date.setDate(date.getDate() + 1);
    date.setHours(7, 0, 0, 0);
  }
  return date;
}

function nextBattleDateAtHourAfter_(fromDate, hour) {
  const base = stripTime_(fromDate);
  for (let offset = 0; offset <= 10; offset++) {
    const candidate = new Date(base.getTime() + offset * MS_PER_DAY);
    candidate.setHours(hour, 0, 0, 0);
    if (BATTLE_DAYS.indexOf(candidate.getDay()) !== -1 && candidate.getTime() > fromDate.getTime()) {
      return candidate;
    }
  }
  throw new Error('次の宣戦日を計算できませんでした');
}

function nextResponseSlotAtOrAfter_(fromDate) {
  const base = stripTime_(fromDate);
  for (let offset = 0; offset <= 2; offset++) {
    for (let index = 0; index < RESPONSE_HOURS.length; index++) {
      const candidate = new Date(base.getTime() + offset * MS_PER_DAY);
      candidate.setHours(RESPONSE_HOURS[index], 0, 0, 0);
      if (candidate.getTime() >= fromDate.getTime()) {
        return candidate;
      }
    }
  }
  throw new Error('次の応戦枠を計算できませんでした');
}

function canAbandonAt_(at) {
  const date = parseDate_(at);
  if (!date) return false;
  const next = nextResponseSlotAtOrAfter_(date);
  const minutesUntilNext = (next.getTime() - date.getTime()) / 60000;
  if (minutesUntilNext >= 0 && minutesUntilNext <= ABANDON_LOCK_MINUTES) return false;

  const previous = previousResponseSlotAtOrBefore_(date);
  const minutesSincePrevious = (date.getTime() - previous.getTime()) / 60000;
  return !(minutesSincePrevious >= 0 && minutesSincePrevious < 60);
}

function previousResponseSlotAtOrBefore_(fromDate) {
  const base = stripTime_(fromDate);
  for (let offset = 0; offset >= -2; offset--) {
    for (let index = RESPONSE_HOURS.length - 1; index >= 0; index--) {
      const candidate = new Date(base.getTime() + offset * MS_PER_DAY);
      candidate.setHours(RESPONSE_HOURS[index], 0, 0, 0);
      if (candidate.getTime() <= fromDate.getTime()) {
        return candidate;
      }
    }
  }
  throw new Error('前の応戦枠を計算できませんでした');
}

function snapResponseHour_(date) {
  const hour = date.getHours();
  if (hour === 23 || hour === 0) return 23;
  if (hour >= 7 && hour < 8) return 7;
  if (hour >= 15 && hour < 16) return 15;
  if (RESPONSE_HOURS.indexOf(hour) !== -1) return hour;
  return nextResponseSlotAtOrAfter_(date).getHours();
}

function buildOnePunchCandidate_(line, protectUntil) {
  if (!protectUntil) return '';
  const hour = protectUntil.getHours();
  if (hour === 23) return '自動:候補';
  if (hour === 7) return '自動:7時要判断';
  return '自動:不要';
}

function shouldReplaceAutoCandidate_(value) {
  const text = String(value || '').trim();
  return text === '' || text.indexOf('自動:') === 0;
}

function buildDisplayOrder_(area, name, lineOrder) {
  const areaOrder = AREA_VALUES.indexOf(String(area || '').trim()) + 1 || 99;
  const match = String(name || '').match(/-(\d+)$/);
  const numberPart = match ? Number(match[1]) : 999;
  const linePart = Number(lineOrder) || 9;
  return areaOrder * 100000 + numberPart * 10 + linePart;
}

function buildUpcomingResponseSlots_(fromDate, days) {
  const slots = [];
  const base = stripTime_(fromDate);
  for (let offset = 0; offset < days; offset++) {
    RESPONSE_HOURS.forEach((hour) => {
      const slot = new Date(base.getTime() + offset * MS_PER_DAY);
      slot.setHours(hour, 0, 0, 0);
      if (slot.getTime() >= fromDate.getTime()) {
        slots.push(slot);
      }
    });
  }
  return slots;
}

function formatResponseSlot_(date) {
  const hour = date.getHours();
  if (hour === 7) return '07:00-08:00';
  if (hour === 15) return '15:00-16:00';
  if (hour === 23) return '23:00-24:00';
  return Utilities.formatDate(date, getTimeZone_(), 'HH:mm');
}

function slotKey_(date) {
  return Utilities.formatDate(date, getTimeZone_(), 'yyyy-MM-dd HH:00');
}

function weekdayLabel_(date) {
  return ['日', '月', '火', '水', '木', '金', '土'][date.getDay()];
}

function parseDate_(value) {
  if (!value) return null;
  if (Object.prototype.toString.call(value) === '[object Date]' && !isNaN(value.getTime())) return value;
  if (typeof value === 'number') return new Date(Math.round((value - 25569) * 86400 * 1000));
  const text = String(value).trim();
  if (!text) return null;
  const normalized = text.replace(/\./g, '/').replace(/-/g, '/');
  const date = new Date(normalized);
  return isNaN(date.getTime()) ? null : date;
}

function stripTime_(date) {
  const result = new Date(date.getTime());
  result.setHours(0, 0, 0, 0);
  return result;
}

function addHours_(date, hours) {
  return new Date(date.getTime() + hours * 60 * 60 * 1000);
}

function normalizeRowLength_(row, length) {
  const result = row.slice(0, length);
  while (result.length < length) result.push('');
  return result;
}

function ensureSheet_(ss, name) {
  return ss.getSheetByName(name) || ss.insertSheet(name);
}

function ensureListHeaders_(sheet) {
  const currentHeaders = normalizeRowLength_(sheet.getRange(1, 1, 1, LIST_HEADERS.length).getValues()[0], LIST_HEADERS.length);
  const needsHeader = currentHeaders.join('') === '' || currentHeaders.some((value, index) => value !== LIST_HEADERS[index]);
  if (needsHeader) {
    sheet.getRange(1, 1, 1, LIST_HEADERS.length).setValues([LIST_HEADERS]);
  }
}

function listValidation_(values) {
  return SpreadsheetApp.newDataValidation().requireValueInList(values, true).setAllowInvalid(false).build();
}

function getTimeZone_() {
  return Session.getScriptTimeZone() || 'Asia/Tokyo';
}
