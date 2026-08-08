# project: 工程（どの順番で進めるか）

## このファイルの目的

このプロジェクトの標準工程と、各工程で使う task プロンプトの対応を示します。

## このファイルを読む作業

- 次にどの工程へ進むか判断するとき
- 承認をどこで受けるか確認するとき
- バグ対応や仕様変更の全体像を確認するとき

## このファイルに含めないもの

- **各工程の詳細手順、出力形式、確認観点** → 対応する `prompts/*.md`（ここには複製しません）
- 成果物の配置とファイル名 → `10_document_structure.md`
- どのひな形を使うか → `15_document_templates.md`
- **レビュー結果の評価値** → `25_review_policy.md`
- 承認の原則、停止判断、次工程移行判定 → `docs/rules/core/20_approval_and_review.md`
- 工程の骨格（仕様→設計→テスト観点→実装→レビュー） → `docs/rules/core/10_workflow.md`

---

## 標準工程

原則として、以下の順番で作業します。

| # | 工程 | 主な成果物 | task プロンプト |
|---|---|---|---|
| 1 | overview を確認または作成 | `10_overview.md` | `prompts/create_overview.md` |
| 2 | 必要に応じて現在地メモを確認・作成 | `tasks.md` | — |
| 3 | overview をもとに feature 分割を確認 | — | — |
| 4 | feature 仕様を作成または確認 | `20_spec.md` | `prompts/create_feature_spec.md` |
| 5 | 必要に応じて feature 側の現在地メモを確認・作成 | `tasks.md` | — |
| 6 | 関数設計を作成または更新 | `21_design.md` | `prompts/create_function_design.md` |
| 7 | 関数呼び出しフローを作成または更新 | `22_flow.md` | `prompts/create_function_call_flow.md` |
| 8 | テスト計画を作成または更新 | `23_test_plan.md` | `prompts/create_test_design.md` |
| 9 | レビュー観点を作成または更新 | `24_review_checklist.md` | `prompts/create_review_checklist.md` |
| **9a** | **人間が実装着手承認欄を確認し、すべてチェックを入れる（AIはチェックを入れない）** | — | — |
| 10 | feature 本体と feature 単体テストを作成 | 実装・テストコード | `prompts/implement_feature.md` |
| **10a** | **実装直後にソースレビューを行う（ファイルは変更しない）** | チャット報告 | `prompts/review_feature_source.md` |
| 11 | 必要に応じて entrypoint と entrypoint テストを作成 | 実装・テストコード | `prompts/implement_entrypoint.md` |
| 12 | 必要に応じて結合試験計画を作成 | `11_integration_test_plan.md` | `prompts/create_integration_test_plan.md` |
| 13 | 必要に応じて結合試験を実装 | テストコード | `prompts/implement_integration_test.md` |
| 14 | テストを実行 | — | `40_testing_rules.md` を参照 |
| 15 | feature 単体レビューを行い記録 | `25_review_result.md` | `prompts/review_feature.md` |
| 16 | command/app 全体レビューを行い記録 | `12_command_review_result.md` | `prompts/review_command.md` |

結合試験は常に必須ではありません。entrypoint から複数 feature を束ねて確認する必要がある場合に扱います。

---

## 承認を置く工程

| 承認 | 工程 | 承認欄の場所 |
|---|---|---|
| 実装着手承認 | 9a（feature 実装の前） | `24_review_checklist.md` 末尾 |
| バグ修正実装の承認 | バグ対応フローの4段階目 | `30_bug_fix_plan.md` の人間承認欄 |
| レビュー指摘の反映承認 | レビュー後、修正作業の前 | 承認欄なし。人間がレビュー結果を確認して個別に判断 |

承認欄がすべてチェックされていない場合、AIは次の工程を開始しません。
AIは承認欄を自らチェックしません。詳細は `docs/rules/core/20_approval_and_review.md` を参照してください。

---

## 共通設計を扱う場合

複数 feature にまたがる設計が必要になった場合、標準工程とは別に、feature 設計（工程6）より前に共通設計を整えます。
feature 個別の設計書に重複して書かず、共通設計として分けて管理します。すべての command/app で必須ではありません。

対象の成果物と、それぞれに対応するプロンプトは `15_document_templates.md` の対応表を参照してください。
共通設計書は人間が直接作成してもかまいません。

---

## バグ対応フロー

```text
報告 → 調査 → 修正計画 → 人間承認 → 実装
```

| 段階 | task プロンプト |
|---|---|
| バグ報告書の作成 | `prompts/create_bug_report.md` |
| バグ調査書の作成 | `prompts/investigate_bug.md` |
| バグ修正計画書の作成 | `prompts/create_bug_fix_plan.md` |
| 人間が修正計画書の承認欄を確認 | — |
| 承認済み計画に従って修正 | `prompts/implement_bug_fix.md` |

修正計画書に記載されていないファイルは変更しません。
仕様・設計・テスト計画の更新が必要と判明した場合は、修正を中断して STOP し、別作業として報告します。

---

## レビュー工程

レビューは段階を分けて行います。

| レビュー | タイミング | task プロンプト | 記録先 |
|---|---|---|---|
| ソースレビュー | 実装直後の中間チェック | `prompts/review_feature_source.md` | チャット報告のみ |
| feature 単体レビュー | feature 完成後 | `prompts/review_feature.md` | `25_review_result.md` |
| command/app 全体レビュー | entrypoint・結合試験を含む最終確認 | `prompts/review_command.md` | `12_command_review_result.md` |
| 補助コンテキストの横断確認 | 必要に応じて随時 | `prompts/review_context.md` | チャット報告のみ |

レビュー結果に記録する評価値と、集計の運用は `25_review_policy.md` を参照してください。

---

## 変更を検討する場合

コードを読んでいて変更を思いついたが、バグか仕様変更か設計改善かが未確定な場合は、**分類を決める前に影響範囲を整理**します。

| 段階 | task プロンプト |
|---|---|
| 変更案の影響範囲と正本の整理（ファイルは変更しない） | `prompts/analyze_code_change_impact.md` |

分析結果を人間が確認し、バグ候補ならバグ対応フローへ、仕様変更なら下記の仕様変更の進め方へ接続します。

### 仕様変更の進め方

**仕様変更専用の task プロンプトはありません。** 次の流れで進めます。

```text
仕様変更の入口
  ↓
prompts/analyze_code_change_impact.md で分類・影響分析（ファイルは変更しない）
  ↓
人間が、変更の正本・更新範囲・進むフローを確認する
  ↓
下記の標準8ステップで反映する
```

#### 標準8ステップ

このスターターキットでの標準手順です。

| Step | 内容 | 使うプロンプト |
|---|---|---|
| 1 | 仕様変更内容を整理する | `prompts/analyze_code_change_impact.md` |
| 2 | 影響範囲を洗い出す | 同上 |
| 3 | 設計書の更新要否を確認する | — |
| 4 | ソースコードの更新要否を確認する | — |
| 5 | テストの更新要否を確認する | — |
| 6 | 更新対象ごとに順番に修正する | 上表の各作成系・実装系プロンプト |
| 7 | 設計書・ソースコード・テストの整合性を確認する | — |
| 8 | 最終チェックを実施する | — |

Step 6 の反映順は、このプロジェクトでは次のとおりです。

- command/app の責務や feature 分割へ影響する場合は、`10_overview.md` から確認・更新する
- 外部から見える動作へ影響する場合は、設計書や実装より先に `20_spec.md` を更新する
- その後、`21_design.md` → `22_flow.md` → `23_test_plan.md` → 実装 → テストの順に進む

正本の特定、上流から下流への反映、変更不要な資料の理由明示、一括修正の禁止は `docs/rules/core/10_workflow.md` を参照してください。
Step 7・8 の結果の報告項目は `docs/rules/core/50_records_and_reporting.md` を参照してください。ここには複製しません。

#### 将来の専用プロンプトとの関係

現時点では仕様変更専用プロンプトが存在しないため、**この8ステップを project の標準手順として保持します。**
将来、仕様変更専用プロンプトを追加した場合は、詳細手順の正本を task プロンプト側へ移し、このファイルには全体像と参照先だけを残すことを検討します。

---

なお、次の2つのプロンプトは、この標準工程（仕様→設計→実装→レビュー）には含まれない、工程外の補助taskです。無理に標準工程へ組み込まないでください。位置づけは `docs/rules/README.md` を参照してください。

- `prompts/review_prompt_integrity.md`：キット自体の完全性確認用。開発対象機能のレビューではありません。
- `prompts/prepare_work_note.md`：作業経緯の記録（作業メモ）用。仕様・設計・実装・レビューのいずれの成果物も作成しません。

---

## 変更する場合の注意

- 工程を増減する場合も、`docs/rules/core/10_workflow.md` の骨格（仕様 → 設計 → テスト観点 → 実装 → レビュー）から逸脱しないでください。
- 承認を置く工程を減らす場合は、`docs/rules/core/20_approval_and_review.md` の承認境界を満たせるか確認してください。core の承認原則を緩和することはできません。

---

## 関連するルール

- 工程の骨格 → `docs/rules/core/10_workflow.md`
- 承認と停止の判断 → `docs/rules/core/20_approval_and_review.md`
- 成果物の配置 → `10_document_structure.md`
- レビュー結果の評価値 → `25_review_policy.md`
- テストの実行方法 → `40_testing_rules.md`
