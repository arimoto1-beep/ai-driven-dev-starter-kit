---
schema: gate_record/v2
feature:
gate:
run_seq:
mode: auto
recorded_by: reviewer
verdict: IN_PROGRESS
next_step:
return_to:
blocked_reason:
triggered_by: INITIAL
triggered_by_record:
supersedes:
started_at:
finished_at:
review_rounds: 0
findings_total: 0
findings_open: 0
guard_violations: 0
req_total:
req_covered:
viewpoint_total:
viewpoint_covered:
spec_hash:
artifacts_hash:
review_independence: separate_context
feature_difficulty:
worker_model_class:
reviewer_model_class:
model_selection:
artifacts:
human_decision_required: 0
---

<!--
このファイルは Gate記録のひな形です。
`prompts/review_stage.md`（Reviewer）がこの構成で作成・更新します。

front matter のルール:
- フラットな `key: value` のみ。入れ子とリスト構文は使わない
- リストはカンマ区切り
- 空値は未設定を表す
- `tools/feature_runner.py` は front matter だけを読む。本文は解析しない

triggered_by の値:
  INITIAL       通常の進行
  RETURN        差し戻しによる再実行
  HUMAN_NOTE    人間の自然文コメントによる再判定
  MANUAL        マニュアル介入からの復帰（--review-current / --spec-review）
  RETRY_BLOCKED BLOCKED からの明示的な再試行（--retry-blocked）
  REWORK        通過済み stage の明示的なやり直し（--rework）
  RUNNER        runner 自身が停止を記録した

spec_hash:
  仕様 stage（CP1）の記録にだけ記入する。
  値は runner が計算して渡す。**自分で計算しない。渡された値をそのまま転記する。**
  製造開始時に runner が現在の 20_spec.md を再計算して照合するため、
  この値が誤っていると製造が始まらない（fail-safe）。

artifacts_hash:
  この stage が baseline 化する成果物の内容ハッシュ。全 stage で記入する。
  値は runner が計算して渡す。**自分で計算しない。渡された値をそのまま転記する。**
  次回の実行時、runner が再計算して照合し、
  「Gate 通過後に成果物が変更されたか」を判定する。

feature_difficulty:
  feature 全体の難易度。`easy` / `normal` / `hard` のいずれか。
  **仕様 stage（CP1）でのみ、あなたが判定して記入する。** 判定基準は
  `prompts/review_stage.md` にある。
  他 stage では runner から渡される。**自分で判定し直さない。転記するだけ。**

worker_model_class / reviewer_model_class / model_selection:
  runner が決めたモデル選択の結果。**自分で計算・推測しない。渡された値をそのまま転記する。**
  `model_selection` は `auto`（既定）または `manual`（`--model-class` 指定時）。
  Worker を起動していない実行では `worker_model_class` は空になる。

schema:
  `gate_record/v2` は上記の front matter 構成を表す。
  `gate_record/v1` の過去記録は履歴としてそのまま残す（書き換えない）。

immutable のルール:
- `verdict: IN_PROGRESS` の間だけ、このファイルへラウンドを追記する
- `PASS` / `RETURN` / `BLOCKED` を書いた時点で immutable
- 以後は書き換えず、新しい Gate記録を作る
- 例外は「人間確認欄」。人間だけが、確定後の記録へ記入する

不要な章がある場合も削除せず、「今回は対象外」または「該当なし」と記載してください。
-->

# Gate記録

## 判定サマリ

| 項目 | 値 |
|---|---|
| stage | 未定 |
| verdict | 未定 |
| next_step | 未定 |
| 収束ラウンド | 未定 |
| FINDING | 検出 0 / 未解決 0 |
| 要求カバレッジ | 0 / 0 |
| 観点カバレッジ | 0 / 0 |
| レビュー独立性 | 未定 |
| モデル選択 | 未定 |

人間が見る要点を3行以内で記載してください。**AIレビューの全内容をここへ書かないでください。**

## レビュー対象

- 対象機能フォルダ: 未定
- 今回のレビュー対象成果物: 未定
- baseline として参照した成果物: 未定

## FINDING

FINDING は次の形式で記録します。**根拠を示せない指摘は記録しません。**

### F-001

| 項目 | 内容 |
|---|---|
| 種別 | 矛盾 / 欠落 / 空白 / 検証不能 / 仕様外 |
| 検出ラウンド | 1 |
| 対象 | `<ファイル>` の該当箇所 |
| 根拠 | `<正式資料>` の該当記述 |
| 影響する要求 | REQ-000 |
| 内容 | 何がどう食い違うか |
| 状態 | 未対応 / 対応済み / 今回スコープ外 / BLOCKED |

## 修正の確認

Reviewer が、現在のファイルを読み直して確認した結果を記載します。
**製造AIの自己申告をそのまま転記しないでください。**

| FINDING | 変更されたファイル | 確認結果 |
|---|---|---|
| 該当なし | — | — |

## 保証範囲

直前の Gate記録の値と比較します。**減っている場合は `BLOCKED(guard_violation)` です。**

| 指標 | 前回 | 今回 | 判定 |
|---|---|---|---|
| req_total | — | 0 | — |
| req_covered | — | — | — |
| viewpoint_total | — | — | — |
| viewpoint_covered | — | — | — |

## 変更範囲のガード

runner から渡された、範囲外の変更の一覧を記載します。

- 該当なし

## 差し戻し／停止の理由

`RETURN` または `BLOCKED` の場合にだけ記載します。

- 判定: 今回は対象外
- 戻り先または理由コード: 今回は対象外
- 判断の根拠（どのファイルのどこを見て、そう判断したか）: 今回は対象外

## 人間確認欄

**AIはこの欄に記入しません。チェックを入れるのは人間です。**

AI Gate（G1 / G2）の場合、この節は「今回は対象外」と記載します。

### 判断してほしいこと

人間が判断する事項を、**選択肢の形**で提示します。3件以内にしてください。

#### A. 未定

- AI案: 未定
- 別案: 未定
- それぞれの帰結: 未定
- [ ] AI案で確定
- [ ] 別案で確定
- [ ] 保留して議論

### 仕様承認（CP1 のみ）

**この承認は、人間側で確定した仕様を AI 製造工程へ渡す境界です。**

チェックを入れると、以降の工程（`21_design.md` / `22_flow.md` 以降）を AI が自動で生成します。
**AIは、この承認済み仕様を超えて仕様判断を追加してはいけません。** 不足が見つかった場合は、
AIが補完せず、この工程へ差し戻されます。

承認前に、次を確認してください。

- 要求に矛盾・曖昧さ・未決事項が残っていないか
- 入出力、異常系、境界条件が定義されているか
- 下流工程で独自の仕様判断が必要になる空白がないか
- PJ上位者・顧客など、必要な関係者の確認が済んでいるか（runner の外の工程を含む）

**承認後に `20_spec.md` を変更した場合、この承認は無効になります。**
変更した場合は `--spec-review` で再レビューし、新しい記録で承認し直してください。

- [ ] 上記の判断事項に回答した
- [ ] 必要な関係者の確認が完了している
- [ ] この仕様を baseline として確定し、AI製造工程へ進むことを承認する

### 設計進行承認（G1 を Human Gate にした場合のみ）

**G1 は既定では AI Gate です。** `human_gates` に `G1` を含めた慎重運用の場合だけ使います。
既定の設定では「今回は対象外」と記載します。

問い：**この設計・処理フローで、テスト設計工程へ進めてよいか。**

- [ ] 上記の判断事項に回答した
- [ ] この設計を前提として、テスト設計工程へ進むことを承認する

### 実装工程進行承認（G2 を Human Gate にした場合のみ）

**G2 は既定では AI Gate です。** `human_gates` に `G2` を含めた慎重運用の場合だけ使います。
既定の設定（`human_gates = CP1, CP3`）では「今回は対象外」と記載します。

問い：**この詳細設計・テスト設計で、実装工程へ進めてよいか。**

- [ ] 上記の判断事項に回答した
- [ ] この詳細設計・テスト設計を前提として、実装工程へ進むことを承認する

### 受け入れ判断（CP3 のみ）

- [ ] feature 要約を読み、内容を理解した
- [ ] 残課題と、保証していない範囲を確認した
- [ ] この feature を完成成果物として受け入れる

### 気になる点（任意）

自然文で構いません。ファイル名や再実行手順を指定する必要はありません。
記入して runner を再実行すると、Reviewer が戻り先を判定します。

```text

```

## feature 要約（CP3 のみ）

人間が理解し、責任を持つための要約です。**1ページに収まる分量にしてください。**

- この feature が何をするか: 未定
- どう動くか（主要な流れ）: 未定
- どこに判断ロジックがあるか: 未定
- **保証していない範囲**: 未定
- 残課題: 未定

## 作業後報告

- 参照したファイル: 未定
- 実行した確認内容: 未定
- テストを実行した場合、そのコマンドと結果: 未定
- 人間判断が必要な事項: 未定
