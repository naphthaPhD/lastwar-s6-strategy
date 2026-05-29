# Phase3 Strategy Rule Engine Specification

## 1. Purpose

Last War 戦況分析システムを、単なる可視化ツールから「参謀本部システム」へ発展させる。

Phase3 では GPT API は使用しない。GPT は後段で説明文生成・作戦案文章化に使う前提とし、本フェーズでは `state.json` を入力にした評価関数を整備する。

主目的は以下。

- 連盟視点で守るべき拠点、取るべき拠点、放棄可能な拠点を評価する
- 味方グループ全体で防衛線、中央接続、他連盟との接続、敵侵攻遮断を評価する
- 評価点だけでなく、スコア根拠を JSON で出力する
- `invasion_strategy_os.py` の描画・データ取得責務と、戦略評価責務を分離する

## 2. System Structure

```text
Google Sheets
  ↓
invasion_strategy_os.py
  - sheet / csv 読込
  - Node / Edge 正規化
  - networkx graph 生成
  - map.html 生成
  - state.json 生成
  ↓
state.json
  ↓
simulation.py
  - choke_score()
  - isolation_score()
  - coalition_score()
  - alliance_score()
  - invasion_score()
  - protection_score()
  - time_score()
  - 総合評価
  ↓
state.json.invasion_simulation
  ↓
briefing_input.json
  ↓
map.html / interactive_app.html
  - スコア表示
  - 候補強調
  - 後段 GPT 説明生成用 JSON
```

実装時の配置は `tools/invasion_strategy_os/simulation.py` とする。既存の `invasion_strategy_os.py` は、状態生成と HTML 生成に責務を寄せ、評価関数の詳細は持たない。

## 3. Responsibility Boundaries

### invasion_strategy_os.py

- Google Sheets / CSV / Excel の読込
- ノード・エッジの正規化
- graph 生成
- connected components / articulation points / centrality の基礎解析
- `state.json` の基礎状態出力
- `map.html` の描画
- `simulation.py` の呼び出し

### simulation.py

- `state.json` 互換の dict を入力にする
- graph は `state["nodes"]` と `state["connections"]` から再構築する
- 戦略スコアを計算する
- 連盟視点とグループ視点を両方出す
- スコア根拠を機械可読 JSON として出す
- `briefing_input.json` を生成する
- GPT API を呼ばない

## 4. Evaluation Levels

### Level 1: Alliance View

特定連盟を基準にした評価。

例:

- `JDX` / `#534` が守るべき拠点
- `JDX` / `#534` が取るべき拠点
- `JDX` / `#534` が放棄しても被害が小さい拠点
- 自連盟から見た敵隣接・反撃リスク

出力では `alliance_scope` を持たせる。

```json
{
  "alliance_scope": {
    "owner": "JDX",
    "area": "#534",
    "affiliations": ["self"]
  }
}
```

### Level 2: Coalition View

味方グループ全体を基準にした評価。

例:

- #534 / #509 / #440 / #511 の防衛ライン
- 中央接続維持
- 味方連盟間の接続維持
- 敵侵攻ルート遮断
- 連盟単体では不利でもグループ全体では守るべき拠点

出力では `coalition_scope` を持たせる。

```json
{
  "coalition_scope": {
    "affiliations": ["self", "ally"],
    "areas": ["#534", "#509", "#440", "#511"]
  }
}
```

## 5. Evaluation Function Specifications

全評価関数は、同じ基本形式を返す。

```json
{
  "score": 96,
  "reasons": [
    "中央接続",
    "敵476隣接",
    "喪失時に東側分断"
  ],
  "details": {}
}
```

スコアは原則 0-100 に正規化する。ただし内部計算では raw score を持ってよい。

```json
{
  "score": 96,
  "raw_score": 148.5,
  "normalized": true
}
```

### 5.1 choke_score(node_id, state, graph, context)

評価内容:

- CHOKE ポイントか
- 主要通路か
- 中央接続か
- articulation point か
- 周辺エッジが少なく侵攻経路が限定されるか

入力に使う項目:

- `state.articulation_points`
- `state.critical_nodes`
- `state.degree_centrality`
- `state.betweenness_centrality`
- `node.area`
- `node.type`
- `node.importance`
- graph degree
- 中央ノードとの隣接

加点例:

- articulation point: +30
- betweenness centrality 高: +20
- 中央接続: +20
- degree が低く経路限定: +10
- 重要度が高い: +10

出力例:

```json
{
  "score": 88,
  "reasons": [
    "CHOKE候補",
    "中央接続",
    "主要通路"
  ],
  "details": {
    "is_articulation_point": true,
    "degree": 2,
    "betweenness": 0.0432,
    "central_neighbors": ["中央:中央-1-1"]
  }
}
```

### 5.2 isolation_score(node_id, state, graph, context)

評価内容:

- 拠点喪失時の分断リスク
- 到達可能ノード数減少
- 孤立拠点発生
- 味方・自連盟・中央接続への影響

計算方針:

1. 現在の graph から対象ノードを除去した仮想 graph を作る
2. 基準ノード群から到達可能なノード数を計算する
3. 除去前後の到達可能数を比較する
4. 到達不能になったノードのうち、重要ノード・味方ノード・中央接続ノードを数える

到達可能数の例:

```json
{
  "before_reachable": 120,
  "after_reachable": 45,
  "lost_reachable": 75
}
```

加点例:

- 到達可能数が 50%以上減少: +40
- 重要拠点が孤立: +25
- 中央接続が消える: +20
- 味方拠点が多数孤立: +15

出力例:

```json
{
  "score": 94,
  "reasons": [
    "喪失時に東側分断",
    "到達可能数 120 → 45",
    "味方拠点 18 件が孤立"
  ],
  "details": {
    "before_reachable": 120,
    "after_reachable": 45,
    "lost_reachable": 75,
    "isolated_friendly_nodes": 18,
    "isolated_major_nodes": 3
  }
}
```

### 5.3 coalition_score(node_id, state, graph, context)

評価内容:

- 味方グループ全体への影響
- 他連盟との接続維持
- グループ防衛ライン維持
- 中央接続維持
- 敵侵攻ルート遮断

対象範囲:

- `affiliation == "self"`
- `affiliation == "ally"`
- 設定で指定した味方エリア: `#534`, `#509`, `#440`, `#511`

加点例:

- 複数味方連盟を接続している: +25
- 味方防衛ライン上にある: +20
- 中央への入口を保持している: +25
- 敵境界に接している: +10
- 失うと味方グループが分断される: +20

出力例:

```json
{
  "score": 98,
  "reasons": [
    "味方グループ防衛ライン",
    "中央接続維持",
    "#534 と #509 の接続維持"
  ],
  "details": {
    "connected_friendly_areas": ["#534", "#509"],
    "central_connection": true,
    "boundary_enemy_count": 3,
    "coalition_line": true
  }
}
```

### 5.4 alliance_score(node_id, state, graph, context)

評価内容:

- 自連盟への影響
- 戦略的重要度
- 周辺保有状況
- 自連盟からの到達性
- 自連盟が守るべきか、取るべきか、放棄可能か

対象範囲:

- `context.self_owners`
- `context.self_area`
- `node.affiliation == "self"`

加点例:

- 自連盟保有: +15
- 自連盟隣接: +15
- 重要度が高い: +20
- 失うと自連盟の到達可能数が減る: +25
- 周辺が自連盟で固まっている: +10
- 周辺が敵に囲まれている: 防衛では +15、侵攻では -10

出力例:

```json
{
  "score": 90,
  "reasons": [
    "JDX保有",
    "周辺JDX拠点多数",
    "喪失時に自連盟ルート縮小"
  ],
  "details": {
    "self_neighbor_count": 4,
    "ally_neighbor_count": 1,
    "enemy_neighbor_count": 2,
    "owned_by_self": true
  }
}
```

### 5.5 invasion_score(node_id, state, graph, context)

評価内容:

- 敵隣接
- 敵侵攻可能性
- 敵到達容易性
- 敵高戦力連盟の近さ
- 未取得地を経由した侵攻余地
- 保護終了・戦闘時間との関係

加点例:

- 敵漁場が隣接: +20
- 敵都市が隣接: +15
- 高戦力敵連盟が隣接: +20
- 敵からの到達距離が短い: +20
- 保護切れまたは保護終了間近: +15
- 未取得地経由で敵が伸びやすい: +10

出力例:

```json
{
  "score": 92,
  "reasons": [
    "敵476隣接",
    "高戦力敵連盟隣接",
    "保護切れ"
  ],
  "details": {
    "enemy_neighbor_count": 4,
    "strong_enemy_neighbors": ["476B", "476C"],
    "enemy_distance": 1,
    "protection_status": "expired"
  }
}
```

### 5.6 protection_score(node_id, state, graph, context)

評価内容:

- `protect_until`
- `protection`
- 保護終了まで残り時間
- 保護更新可能性

目的:

- 空間的に重要でも、保護中で攻撃できない拠点を過大評価しない
- 保護切れ直後または保護終了間近の拠点を優先候補に上げる
- 保護更新される可能性が高い拠点は、実行可能性を下げる

入力に使う項目:

- `node.protect_until`
- `node.protection.status`
- `node.protection.hours_remaining`
- `node.status`
- `node.memo`
- `generated_at`
- 将来追加: `protection.renewable`
- 将来追加: `protection.last_refreshed_at`
- 将来追加: `protection.renewal_probability`

加点例:

- 保護切れ: +35
- 保護終了 6h 以内: +25
- 保護終了 12h 以内: +15
- 保護終了 24h 以内: +8
- 保護中 24h 超: -20
- 保護更新可能性が高い: -15
- 保護更新不可または更新可能性が低い: +10

出力例:

```json
{
  "score": 82,
  "reasons": [
    "保護終了6h以内",
    "保護更新可能性低"
  ],
  "details": {
    "protect_until": "2026-05-30T23:00:00+09:00",
    "hours_remaining": 5.4,
    "status": "warning",
    "renewal_probability": "low"
  }
}
```

### 5.7 time_score(node_id, state, graph, context)

評価内容:

- 土曜戦闘日
- 水曜戦闘日
- 応戦期間
- 現在時刻との距離

目的:

- 空間評価だけでなく、実行可能なタイミングを評価する
- 戦闘可能時間が近い候補を上げる
- 戦闘日から遠い候補は監視候補に留める
- 応戦期間中の防衛・反撃候補を上げる

入力に使う項目:

- `generated_at`
- `timezone`
- `scenario.battle_window`
- `battle_rules.weekly_windows`
- `node.protection.hours_remaining`
- 将来追加: `response_window`
- 将来追加: `event_schedule`

加点例:

- 現在が戦闘可能時間内: +30
- 次の戦闘可能時間まで 6h 以内: +20
- 次の戦闘可能時間まで 12h 以内: +12
- 水曜戦闘日: +10
- 土曜戦闘日: +15
- 応戦期間中: +20
- 戦闘日から 24h 超離れている: -15

出力例:

```json
{
  "score": 76,
  "reasons": [
    "土曜戦闘日",
    "戦闘可能時間まで6h以内",
    "応戦期間中"
  ],
  "details": {
    "now": "2026-05-30T18:00:00+09:00",
    "next_battle_window_starts_at": "2026-05-30T20:00:00+09:00",
    "hours_to_next_battle_window": 2.0,
    "battle_day": "saturday",
    "response_window_active": true
  }
}
```

## 6. Combined Output Format

ノード単位の統合評価は以下。

```json
{
  "node": "E-11",
  "node_id": "#534:E-11",
  "score": 96,
  "classification": "defend",
  "alliance_score": 90,
  "coalition_score": 98,
  "choke_score": 88,
  "isolation_score": 94,
  "invasion_score": 92,
  "protection_score": 82,
  "time_score": 76,
  "reasons": [
    "中央接続",
    "敵476隣接",
    "喪失時に東側分断"
  ],
  "details": {
    "choke": {},
    "isolation": {},
    "coalition": {},
    "alliance": {},
    "invasion": {},
    "protection": {},
    "time": {}
  }
}
```

`classification` 候補:

- `defend`: 守るべき
- `attack`: 取るべき
- `interdict`: 遮断・破壊候補
- `risk`: 危険監視
- `optional`: 優先度低
- `abandonable`: 放棄可能

`state.json` への格納案:

```json
{
  "invasion_simulation": {
    "engine": "strategic_rule_engine_v2",
    "node_evaluations": [],
    "defense_priorities": [],
    "attack_priorities": [],
    "interdiction_priorities": [],
    "risk_watchlist": [],
    "time_sensitive_nodes": [],
    "protection_watchlist": [],
    "abandonable_nodes": [],
    "coalition_lines": []
  }
}
```

## 7. Data Flow

```text
1. Google Sheets / Excel を読む
2. Node / Edge を生成する
3. networkx graph を作る
4. state.json 基礎情報を作る
5. simulation.py に state dict を渡す
6. simulation.py 内で graph を再構築する
7. 各 node に対して評価関数を実行する
8. protection_score / time_score で実行可能性を補正する
9. スコアを統合する
10. invasion_simulation として JSON に戻す
11. briefing_input.json として重要要素だけを圧縮出力する
12. map.html が必要な部分だけ表示する
```

## 8. Required Current state.json Fields

現在の `state.json` で利用できる項目。

Top-level:

- `generated_at`
- `timezone`
- `nodes`
- `connections`
- `owner_affiliations`
- `connected_components`
- `articulation_points`
- `critical_nodes`
- `isolated_nodes`
- `degree_centrality`
- `betweenness_centrality`
- `alliance_power_rankings`
- `invasion_simulation`

Node:

- `id`
- `name`
- `type`
- `owner`
- `display_owner`
- `area`
- `x`
- `y`
- `visual_x`
- `visual_y`
- `importance`
- `protect_until`
- `protection`
- `affiliation`
- `strategic_color`
- `destroyed`
- `alliance_power`
- `status`
- `memo`
- `acquired_at`

Connection:

- `source`
- `target`
- `weight`

## 9. Additional Required Fields

Phase3 正式評価に向けて、追加が望ましい項目。

### 9.1 Scenario / Context

```json
{
  "scenario": {
    "self_owners": ["JDX"],
    "self_area": "#534",
    "ally_areas": ["#509", "#440", "#511"],
    "enemy_areas": ["#503", "#480", "#523", "#476"],
    "battle_window": {
      "active": true,
      "starts_at": "2026-05-30T00:00:00+09:00",
      "ends_at": "2026-05-30T23:59:00+09:00"
    }
  }
}
```

### 9.2 Capture Limit

現在は所有ノード数による暫定推定になりやすい。正式には連盟ごとの占領上限と現在使用数が必要。

```json
{
  "capture_limits": {
    "JDX": {
      "limit": 6,
      "used": 4,
      "remaining": 2
    }
  }
}
```

### 9.3 Pact / Temporary Access

盟約や一時的な隣接許可を通常エッジと分けて持つ。

```json
{
  "temporary_edges": [
    {
      "source": "#534:D-15",
      "target": "#534:D-17",
      "type": "pact_access",
      "valid_until": "2026-05-30T23:59:00+09:00"
    }
  ]
}
```

### 9.4 Battle Rules

```json
{
  "battle_rules": {
    "city_destroy_blocks_edges": true,
    "city_transit_allowed": false,
    "trade_posts_isolated": true,
    "altars_isolated": true,
    "central_fisheries_connect": true
  }
}
```

### 9.5 Operational Status

評価精度向上のため、後で追加したい項目。

- 連盟の実稼働人数
- 現在の集結可否
- 主力プレイヤーの参加状態
- 直近攻撃ログ
- 防衛意志
- 外交上の攻撃禁止対象
- 優先目標タグ

### 9.6 Protection Renewal

保護更新可能性を評価するため、現在の `protect_until` だけでなく、更新可能性を別項目として持つことが望ましい。

```json
{
  "protection": {
    "status": "protected",
    "protect_until": "2026-05-30T23:00:00+09:00",
    "hours_remaining": 5.4,
    "renewable": true,
    "last_refreshed_at": "2026-05-29T23:00:00+09:00",
    "renewal_probability": "medium"
  }
}
```

`renewal_probability` 候補:

- `unknown`
- `low`
- `medium`
- `high`

### 9.7 Time Windows

水曜・土曜戦闘日、応戦期間、現在時刻との距離を評価するため、時間設定を state または config に持つ。

```json
{
  "battle_rules": {
    "weekly_windows": [
      {
        "label": "wednesday_battle",
        "weekday": 2,
        "start": "00:00",
        "end": "23:59"
      },
      {
        "label": "saturday_battle",
        "weekday": 5,
        "start": "00:00",
        "end": "23:59"
      }
    ],
    "response_window_hours": 24
  }
}
```

## 10. briefing_input.json

`simulation.py` 終了時に、将来の GPT ブリーフィング生成用として `briefing_input.json` を生成する。

目的:

- `state.json` 全体を GPT に渡さない
- 戦略上重要な候補だけを圧縮する
- スコア、根拠、注意点、未確認事項を機械可読にする
- 後段の GPT が「説明生成」に集中できるようにする

出力場所案:

```text
sample_output/briefing_input.json
```

含める情報:

- 生成時刻
- 対象シナリオ
- 上位防衛候補
- 上位攻撃候補
- 上位遮断候補
- 危険監視候補
- 中央接続候補
- 保護終了が近い候補
- 戦闘時間が近い候補
- 味方グループ防衛ライン
- 主要リスク
- 評価に使った前提
- 不足データ

含めない情報:

- 全ノード一覧
- 全エッジ一覧
- HTML 用の描画座標
- 大量のメモ全文
- GPT に不要な生ログ

出力例:

```json
{
  "generated_at": "2026-05-30T01:30:00+09:00",
  "engine": "strategic_rule_engine_v2",
  "scenario": {
    "self_owners": ["JDX"],
    "coalition_affiliations": ["self", "ally"]
  },
  "top_defense": [
    {
      "node": "E-11",
      "score": 96,
      "reasons": ["中央接続", "喪失時に東側分断"]
    }
  ],
  "top_attack": [],
  "top_interdiction": [],
  "risk_watchlist": [],
  "time_sensitive": [
    {
      "node": "A-21",
      "score": 82,
      "reasons": ["保護終了6h以内", "土曜戦闘日"]
    }
  ],
  "assumptions": [
    "GPT APIは未使用",
    "占領上限は設定値または暫定値を使用"
  ],
  "missing_data": [
    "保護更新可能性",
    "実稼働人数",
    "外交上の攻撃禁止対象"
  ]
}
```

## 11. Scoring Policy

初期実装では、各関数を 0-100 に正規化し、総合点を重み付きで計算する。

防衛優先:

```text
score =
  choke_score * 0.16 +
  isolation_score * 0.24 +
  coalition_score * 0.20 +
  alliance_score * 0.12 +
  invasion_score * 0.10 +
  protection_score * 0.10 +
  time_score * 0.08
```

攻撃優先:

```text
score =
  invasion_score * 0.26 +
  choke_score * 0.16 +
  coalition_score * 0.16 +
  alliance_score * 0.16 +
  isolation_score * 0.08 +
  protection_score * 0.08 +
  time_score * 0.10
```

遮断優先:

```text
score =
  isolation_score * 0.28 +
  choke_score * 0.20 +
  coalition_score * 0.16 +
  invasion_score * 0.14 +
  alliance_score * 0.06 +
  protection_score * 0.08 +
  time_score * 0.08
```

## 12. Implementation Notes

レビュー時の確認点と、初期実装で採用した扱い。

1. 自連盟の基準は `JDX` 固定ではなく、設定値と始点連盟を優先する。
2. 味方グループは初期実装では `affiliation in ["self", "ally"]` を使う。
3. 到達可能数の基準ノードは味方グループ全体の到達性を主に見る。
4. 都市破壊済みノードは edge block とみなし、到達不能化評価にも反映する。
5. 未取得ノードは中立として扱い、境界・危険評価では敵と未取得の接触も見る。
6. `abandonable` は低スコアだけでなく、敵隣接・中央価値・保護切れを加味する。
7. 中央接続は中央漁場と中央へ接続する外周漁場の両方を評価対象にする。
8. 保護更新可能性は現時点では設定・入力値があれば使い、なければ理由に明記する。
9. 応戦期間と戦闘日は設定で切り替え可能にする。
10. `briefing_input.json` はカテゴリごとに上位10件を標準出力とする。

## 13. Review Status

Status: implemented after design review approval.

レビュー承認後、`tools/invasion_strategy_os/simulation.py` に戦略ルールエンジン v2 を実装した。`invasion_strategy_os.py` は state 生成、HTML 生成、JSON 書き出しを担当し、評価関数の詳細は `simulation.py` 側へ分離した。
