const SHEET_NAMES = {
  INDEX: '00_目次',
  LIST: '漁場一覧',
  EVENTS: 'イベント一覧',
  SIMULATOR: 'シミュレーター',
  CALENDAR: 'カレンダー',
  LINE_DEFINITIONS: 'ライン定義',
  ROUTE_CHECK: '侵攻ルート確認',
  ALLIANCE_JUDGMENT: '連盟判定',
  PACTS: '盟約管理',
  CAPACITY: '連盟キャパ管理',
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
  '所有連盟関係',
  '所有連盟サーバ',
  '盟約状態',
  '保護パン可否',
  '1日残取得数',
  '都市由来余力',
  '制約メモ',
  '敵侵攻前提',
  '総合判定',
];

const INDEX_HEADERS = [
  '分類',
  '優先',
  'シート名',
  '用途',
  '見る頻度',
  'メモ',
];

const INDEX_ROWS = [
  ['日常運用', 1, '漁場一覧4枠', '漁場ごとの現在保護切れ、4状態、保護パン可否、敵味方/盟約/キャパ制約を見る', '毎回', 'まずここを見る'],
  ['日常運用', 2, '開放カレンダー4枠', '水曜23時・木曜7時・土曜23時・日曜7時の4枠で対象漁場を一覧化', '毎回', '15時は最終枠にしない'],
  ['日常運用', 3, '侵攻ルート確認', '同じ侵攻ルート上の連続開放、敵保有、同時突破リスクを見る', '毎回', '危険/分散の判断'],
  ['日常運用', 4, '連盟安全期間', '連盟ごとの安全期間と放棄後の最短取得可能時刻を確認', '必要時', '放棄判断用'],
  ['日常運用', 5, 'シミュレーター', '取得・保護パン・放棄時の次回保護切れを試算', '必要時', '個別ケース確認'],
  ['入力マスタ', 1, '漁場一覧', '元データ。漁場ごとの所有連盟、座標、保護切れを保持', '更新時', '直接編集は慎重に'],
  ['入力マスタ', 2, '連盟判定', '敵/味方/同サーバ/他サーバ味方などの判定マスタ', '更新時', 'xJR/476C/476Bは敵登録済み'],
  ['入力マスタ', 3, '盟約管理', '盟約相手と有効状態を管理。盟約中は保護パン不可', '更新時', '外交変更時に更新'],
  ['入力マスタ', 4, '連盟キャパ管理', '1日取得上限、所有都市、都市由来漁場上限、現所有数を管理', '更新時', '取得役の余力判断'],
  ['入力マスタ', 5, 'ライン定義', 'エリア別の侵攻方向・ライン軸を管理', '変更時', '#509/#476追加時に使う'],
  ['取込確認', 1, 'ABCスクショ取込確認', '#534 ABCスクショのファイル順・目視値・番号正規化確認', '取込時', 'A-1,A-3...順'],
  ['取込確認', 2, '縦スクショ再分析', '縦スクショの指定順/OCR/目視/不一致確認', '取込時', '#503/#534混入を要判断'],
  ['取込確認', 3, '縦スクショ取込確認', '縦スクショ初期取込データと並替ヘルパー', '必要時', '監査用'],
  ['取込確認', 4, '縦スクショ逆順ビュー', '縦スクショをK→A、番号降順で見る補助ビュー', '必要時', '並替確認用'],
  ['旧/自動生成', 1, 'イベント一覧', '旧時系列一覧。4枠運用では開放カレンダー4枠を優先', '通常見ない', 'Apps Script互換用'],
  ['旧/自動生成', 2, 'カレンダー', '旧カレンダー。4枠運用では開放カレンダー4枠を優先', '通常見ない', 'Apps Script互換用'],
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
  '敵連盟含有',
  '敵侵攻警戒',
  '制約メモ',
];

const ALLIANCE_JUDGMENT_HEADERS = [
  '連盟タグ',
  '正規タグ',
  'サーバ',
  '関係区分',
  '所属分類',
  '保護パン対象',
  '優先度',
  '備考',
  '更新日',
];

const PACT_HEADERS = [
  '自連盟',
  '相手連盟',
  '正規相手タグ',
  '相手サーバ',
  '盟約状態',
  '保護パン可否',
  '開始日',
  '終了日',
  '備考',
  '更新日',
];

const CAPACITY_HEADERS = [
  '連盟タグ',
  '正規タグ',
  'サーバ',
  '関係区分',
  '1日取得上限',
  '本日取得数',
  '残取得数',
  '所有都市',
  '都市数',
  '都市由来漁場上限',
  '現所有漁場数',
  '推定余力',
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

const ALLIANCE_JUDGMENT_ROWS = [
  ['xJR', 'XJR', '#503', '敵', '他サーバ敵', '可', '高', '現状敵。画像ではxjR表記あり', '2026/06/01'],
  ['xjR', 'XJR', '#503', '敵', '他サーバ敵', '可', '高', '表記揺れ吸収用。正規タグはXJR', '2026/06/01'],
  ['476C', '476C', '#476', '敵', '他サーバ敵', '可', '高', '現状敵。侵攻前提で警戒', '2026/06/01'],
  ['476B', '476B', '#476', '敵', '他サーバ敵', '可', '高', '現状敵。侵攻前提で警戒', '2026/06/01'],
  ['JDX', 'JDX', '#534', '味方', '同サーバ味方', '不可', '基準', '自陣営。必要に応じて修正', '2026/06/01'],
  ['KTVS', 'KTVS', '#534', '味方', '同サーバ味方', '不可', '高', '味方想定。必要に応じて修正', '2026/06/01'],
];

const PACT_ROWS = [
  ['JDX', '', '', '', '未登録', '', '', '', '盟約相手を追加すると、保護パン可否の判定に使う', '2026/06/01'],
  ['KTVS', '', '', '', '未登録', '', '', '', '盟約状態が有効なら保護パン不可', '2026/06/01'],
];

const CAPACITY_ROWS = [
  ['xJR', 'XJR', '#503', '敵', '', '', '', '', '', '', '', ''],
  ['476C', '476C', '#476', '敵', '', '', '', '', '', '', '', ''],
  ['476B', '476B', '#476', '敵', '', '', '', '', '', '', '', ''],
  ['JDX', 'JDX', '#534', '味方', '', '', '', '', '', '', '', ''],
  ['KTVS', 'KTVS', '#534', '味方', '', '', '', '', '', '', '', ''],
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
  const indexSheet = ensureSheet_(ss, SHEET_NAMES.INDEX);
  const listSheet = ensureSheet_(ss, SHEET_NAMES.LIST);
  const eventsSheet = ensureSheet_(ss, SHEET_NAMES.EVENTS);
  const simulatorSheet = ensureSheet_(ss, SHEET_NAMES.SIMULATOR);
  const calendarSheet = ensureSheet_(ss, SHEET_NAMES.CALENDAR);
  const lineDefinitionSheet = ensureSheet_(ss, SHEET_NAMES.LINE_DEFINITIONS);
  const routeCheckSheet = ensureSheet_(ss, SHEET_NAMES.ROUTE_CHECK);
  const allianceJudgmentSheet = ensureSheet_(ss, SHEET_NAMES.ALLIANCE_JUDGMENT);
  const pactSheet = ensureSheet_(ss, SHEET_NAMES.PACTS);
  const capacitySheet = ensureSheet_(ss, SHEET_NAMES.CAPACITY);

  setupIndexSheet_(indexSheet);
  setupListSheet_(listSheet);
  setupEventsSheet_(eventsSheet);
  setupSimulatorSheet_(simulatorSheet);
  setupCalendarSheet_(calendarSheet);
  setupLineDefinitionSheet_(lineDefinitionSheet);
  setupRouteCheckSheet_(routeCheckSheet);
  setupAllianceJudgmentSheet_(allianceJudgmentSheet);
  setupPactSheet_(pactSheet);
  setupCapacitySheet_(capacitySheet);
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
  const allianceMap = readAllianceJudgmentMap_(ss);
  const pactMap = readPactMap_(ss);
  const capacityMap = readCapacityMap_(ss);
  const ownerCounts = buildOwnerCounts_(values);
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
    applyAllianceConstraints_(row, allianceMap, pactMap, capacityMap, ownerCounts);

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
  buildRouteCheckSheet_(ss, eventRows, allianceMap);
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

function setupIndexSheet_(sheet) {
  sheet.clear();
  sheet.getRange('A1:F1').setValues([['Last War S6 漁場保護管理 目次', '', '', '', '', '']]);
  sheet.getRange(2, 1, 1, INDEX_HEADERS.length).setValues([INDEX_HEADERS]);
  sheet.getRange(3, 1, INDEX_ROWS.length, INDEX_HEADERS.length).setValues(INDEX_ROWS);
  sheet.getRange(INDEX_ROWS.length + 4, 1, 2, INDEX_HEADERS.length).setValues([
    ['整理方針', '', '', '削除はしない。日常運用は上段5タブ、編集は入力マスタ、OCR確認は取込確認へ分離。', '', ''],
    ['注意', '', '', 'A列/B列だけで時刻を固定しない。必ず漁場単位の保護切れと4状態を見る。', '', ''],
  ]);
  sheet.setFrozenRows(2);
  sheet.getRange('A1:F1').setFontWeight('bold').setFontSize(14).setBackground('#0d3b66').setFontColor('#ffffff');
  sheet.getRange(2, 1, 1, INDEX_HEADERS.length).setFontWeight('bold').setBackground('#2f5f80').setFontColor('#ffffff');
  sheet.autoResizeColumns(1, INDEX_HEADERS.length);
  sheet.setColumnWidth(4, 430);
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

function setupAllianceJudgmentSheet_(sheet) {
  setupStaticSheet_(sheet, ALLIANCE_JUDGMENT_HEADERS, ALLIANCE_JUDGMENT_ROWS, '#0b5394');
}

function setupPactSheet_(sheet) {
  setupStaticSheet_(sheet, PACT_HEADERS, PACT_ROWS, '#674ea7');
}

function setupCapacitySheet_(sheet) {
  setupStaticSheet_(sheet, CAPACITY_HEADERS, CAPACITY_ROWS, '#38761d');
}

function setupStaticSheet_(sheet, headers, rows, color) {
  const existing = sheet.getDataRange().getValues();
  if (existing.length <= 1 || existing[0].join('') === '') {
    sheet.clear();
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    if (rows.length > 0) sheet.getRange(2, 1, rows.length, headers.length).setValues(rows);
  } else {
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  }
  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold').setBackground(color).setFontColor('#ffffff');
  sheet.autoResizeColumns(1, headers.length);
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

function buildRouteCheckSheet_(ss, events, allianceMap) {
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
    const enemyEvents = routeEvents.filter((event) => {
      const alliance = allianceMap[normalizeAllianceTag_(event.owner)];
      return alliance && alliance.relation === '敵';
    });
    return [
      parts[0],
      parts[1],
      routeEvents.map((event) => event.key).join('\n'),
      labels.join(' → '),
      hasConsecutiveSame ? '危険' : '分散',
      hasConsecutiveSame ? '危険：同じ開放枠が連続。同時突破リスク高' : '分散：時間差あり',
      enemyEvents.map((event) => `${event.key} ${event.owner}`).join('\n'),
      enemyEvents.length > 0 ? (hasConsecutiveSame ? '最優先:敵ルートかつ同枠連続' : '警戒:敵保有あり') : '',
      enemyEvents.length > 0 ? '敵保有を前提に保護を検討' : '',
    ];
  });
  if (rows.length > 0) {
    sheet.getRange(2, 1, rows.length, ROUTE_CHECK_HEADERS.length).setValues(rows);
  }
  sheet.autoResizeColumns(1, ROUTE_CHECK_HEADERS.length);
}

function applyAllianceConstraints_(row, allianceMap, pactMap, capacityMap, ownerCounts) {
  const ownerTag = normalizeAllianceTag_(row[3]);
  const alliance = allianceMap[ownerTag] || {};
  const pact = pactMap[ownerTag] || {};
  const capacity = capacityMap[ownerTag] || {};
  const relation = alliance.relation || '未登録';
  const pactStatus = pact.status || '未登録';
  const ownerCount = ownerCounts[ownerTag] || 0;
  const dailyRemaining = capacity.dailyCap === '' ? '' : Math.max(0, Number(capacity.dailyCap || 0) - Number(capacity.todayCount || 0));
  const cityRemaining = capacity.cityFisheryCap === '' ? '' : Number(capacity.cityFisheryCap || 0) - ownerCount;
  const punchAvailability = buildProtectionPunchAvailability_(relation, pactStatus);
  const constraintMemo = buildAllianceConstraintMemo_(relation, pactStatus, dailyRemaining, cityRemaining);

  row[25] = relation;
  row[26] = alliance.server || '';
  row[27] = pactStatus;
  row[28] = punchAvailability;
  row[29] = dailyRemaining;
  row[30] = cityRemaining;
  row[31] = constraintMemo;
  row[32] = relation === '敵' ? '敵侵攻前提' : relation === '未登録' ? '未判定' : '';
  row[33] = buildOverallAllianceJudgment_(relation, punchAvailability, constraintMemo);
}

function buildProtectionPunchAvailability_(relation, pactStatus) {
  if (pactStatus === '有効') return '不可:盟約';
  if (relation === '敵') return '可:敵保有';
  if (String(relation).indexOf('味方') !== -1) return '不可:味方';
  if (relation === '同サーバ') return '要判断:同サーバ';
  if (relation === '未登録') return '要確認:連盟未登録';
  return '要判断';
}

function buildAllianceConstraintMemo_(relation, pactStatus, dailyRemaining, cityRemaining) {
  if (pactStatus === '有効') return '盟約中:保護パン不可';
  if (String(relation).indexOf('味方') !== -1) return '味方保有:保護パン不可';
  if (relation === '未登録') return '連盟判定未登録';
  if (dailyRemaining !== '' && dailyRemaining <= 0) return '1日取得上限到達';
  if (cityRemaining !== '' && cityRemaining <= 0) return '都市由来の保有枠不足';
  return '';
}

function buildOverallAllianceJudgment_(relation, punchAvailability, constraintMemo) {
  if (punchAvailability === '不可:盟約') return '保護パン不可:盟約';
  if (punchAvailability === '不可:味方') return '保護パン不可:味方';
  if (relation === '敵') return constraintMemo ? `敵保有:${constraintMemo}` : '敵保有:保護検討';
  if (relation === '未登録') return '要確認:連盟未登録';
  return constraintMemo || '通常確認';
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

function readAllianceJudgmentMap_(ss) {
  const sheet = ensureSheet_(ss, SHEET_NAMES.ALLIANCE_JUDGMENT);
  const rows = sheet.getDataRange().getValues().slice(1);
  const result = {};
  rows.forEach((row) => {
    const key = normalizeAllianceTag_(row[1] || row[0]);
    if (!key) return;
    result[key] = {
      tag: row[0],
      normalizedTag: key,
      server: row[2] || '',
      relation: row[3] || '未登録',
      group: row[4] || '',
      protectionPunchTarget: row[5] || '',
    };
  });
  return result;
}

function readPactMap_(ss) {
  const sheet = ensureSheet_(ss, SHEET_NAMES.PACTS);
  const rows = sheet.getDataRange().getValues().slice(1);
  const result = {};
  rows.forEach((row) => {
    const key = normalizeAllianceTag_(row[2] || row[1]);
    if (!key) return;
    result[key] = {
      status: row[4] || '',
      protectionPunchAvailability: row[5] || '',
    };
  });
  return result;
}

function readCapacityMap_(ss) {
  const sheet = ensureSheet_(ss, SHEET_NAMES.CAPACITY);
  const rows = sheet.getDataRange().getValues().slice(1);
  const result = {};
  rows.forEach((row) => {
    const key = normalizeAllianceTag_(row[1] || row[0]);
    if (!key) return;
    result[key] = {
      dailyCap: row[4] === '' ? '' : Number(row[4]),
      todayCount: row[5] === '' ? 0 : Number(row[5]),
      cityFisheryCap: row[9] === '' ? '' : Number(row[9]),
    };
  });
  return result;
}

function buildOwnerCounts_(values) {
  const counts = {};
  values.slice(1).forEach((row) => {
    const key = normalizeAllianceTag_(row[3]);
    if (!key) return;
    counts[key] = (counts[key] || 0) + 1;
  });
  return counts;
}

function normalizeAllianceTag_(value) {
  return String(value || '').trim().toUpperCase();
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
