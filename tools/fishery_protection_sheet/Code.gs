const SHEET_NAMES = {
  LIST: '漁場一覧',
  EVENTS: 'イベント一覧',
  SIMULATOR: 'シミュレーター',
  CALENDAR: 'カレンダー',
};

const LIST_HEADERS = [
  '漁場名',
  '所有連盟',
  'A/B/C列',
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
];

const EVENT_HEADERS = [
  '保護切れ日時',
  '応戦時間帯',
  '対象数',
  '漁場名',
  '所有連盟',
  'A/B/C列',
  '座標',
  'ワンパン必要',
  'ワンパン役',
  '備考',
];

const CALENDAR_HEADERS = [
  '日付',
  '曜日',
  '応戦時間帯',
  '安全期間',
  '対象数',
  '対象漁場',
  'ワンパン候補',
];

const RESPONSE_HOURS = [7, 15, 23];
const SAFE_RESPONSE_HOUR = 15;
const BATTLE_DAYS = [3, 6]; // Sunday = 0, Wednesday = 3, Saturday = 6.
const MS_PER_DAY = 24 * 60 * 60 * 1000;
const ABANDON_LOCK_MINUTES = 60;
const REACQUIRE_LOCK_HOURS = 24;

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

  setupListSheet_(listSheet);
  setupEventsSheet_(eventsSheet);
  setupSimulatorSheet_(simulatorSheet);
  setupCalendarSheet_(calendarSheet);
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

    const currentProtectUntil = parseDate_(row[4]);
    const operationAt = parseDate_(row[9]);
    const operation = String(row[10] || '').trim();
    let nextProtectUntil = null;

    if (operationAt) {
      if (operation === '放棄') {
        nextProtectUntil = calculateAbandonProtectionEnd_(operationAt);
        row[14] = addHours_(operationAt, REACQUIRE_LOCK_HOURS);
      } else {
        nextProtectUntil = calculateNextProtectionEnd_(operationAt);
        row[14] = '';
      }
    } else if (currentProtectUntil) {
      nextProtectUntil = currentProtectUntil;
      row[14] = '';
    }

    row[5] = nextProtectUntil ? formatResponseSlot_(nextProtectUntil) : '';
    row[11] = nextProtectUntil || '';
    row[12] = nextProtectUntil ? formatResponseSlot_(nextProtectUntil) : '';
    row[13] = canAbandonAt_(now) ? '可' : '不可';
    row[15] = now;

    if (shouldReplaceAutoCandidate_(row[6])) {
      row[6] = buildOnePunchCandidate_(row[2], nextProtectUntil);
    }

    outputRows.push(row);
    if (nextProtectUntil) {
      eventRows.push({
        protectUntil: nextProtectUntil,
        slot: formatResponseSlot_(nextProtectUntil),
        name: row[0],
        owner: row[1],
        line: row[2],
        coord: row[3],
        onePunch: row[6],
        assignee: row[7],
        note: row[8],
      });
    }
  }

  if (outputRows.length > 0) {
    listSheet.getRange(2, 1, outputRows.length, LIST_HEADERS.length).setValues(outputRows);
  }
  buildEventsSheet_(ss, eventRows);
  buildCalendarSheet_(ss, eventRows);
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

  sheet.getRange('B6').setValue(nextProtectUntil);
  sheet.getRange('B7').setValue(formatResponseSlot_(nextProtectUntil));
  sheet.getRange('B8').setValue(operation === '放棄' ? addHours_(operationAt, REACQUIRE_LOCK_HOURS) : '');
  sheet.getRange('B9').setValue(canAbandonAt_(operationAt) ? '可' : '不可');
  sheet.getRange('B10').setValue(
    operation === '放棄'
      ? '放棄時刻から次の応戦枠を基準に1枠後ろへ進め、15時枠は23時枠へ繰り下げ'
      : '次の宣戦日の同時刻から1枠後ろへ進め、15時枠は23時枠へ繰り下げ'
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

function setupListSheet_(sheet) {
  ensureListHeaders_(sheet);
  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, LIST_HEADERS.length).setFontWeight('bold').setBackground('#1f4e79').setFontColor('#ffffff');
  sheet.getRange('C2:C').setDataValidation(listValidation_(['A', 'B', 'C']));
  sheet.getRange('G2:G').setDataValidation(listValidation_(['自動:候補', '自動:7時要判断', '自動:不要', '必要', '不要', '見送り', '要確認']));
  sheet.getRange('K2:K').setDataValidation(listValidation_(['取得', '保護パン', '放棄']));
  sheet.getRange('E:E').setNumberFormat('yyyy/mm/dd hh:mm');
  sheet.getRange('J:J').setNumberFormat('yyyy/mm/dd hh:mm');
  sheet.getRange('L:L').setNumberFormat('yyyy/mm/dd hh:mm');
  sheet.getRange('O:P').setNumberFormat('yyyy/mm/dd hh:mm');
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
  sheet.getRange('B2').setDataValidation(listValidation_(['取得', '保護パン', '放棄']));
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
    event.name,
    event.owner,
    event.line,
    event.coord,
    event.onePunch,
    event.assignee,
    event.note,
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
    const key = slotKey_(event.protectUntil);
    if (!eventMap[key]) eventMap[key] = [];
    eventMap[key].push(event);
  });

  const slots = buildUpcomingResponseSlots_(new Date(), 21);
  const rows = slots.map((slot) => {
    const key = slotKey_(slot);
    const slotEvents = eventMap[key] || [];
    return [
      stripTime_(slot),
      weekdayLabel_(slot),
      formatResponseSlot_(slot),
      slot.getHours() === SAFE_RESPONSE_HOUR ? '安全期間' : '',
      slotEvents.length,
      slotEvents.map((event) => event.name).join('\n'),
      slotEvents
        .filter((event) => String(event.onePunch || '').indexOf('候補') !== -1 || String(event.onePunch || '').indexOf('必要') !== -1)
        .map((event) => event.name)
        .join('\n'),
    ];
  });
  if (rows.length > 0) {
    sheet.getRange(2, 1, rows.length, CALENDAR_HEADERS.length).setValues(rows);
  }
  sheet.autoResizeColumns(1, CALENDAR_HEADERS.length);
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
