# ルール体系の地図

`docs/rules/` は、AI駆動開発スターターキットのルールを責務別に整理した場所です。このREADMEは、ルール体系の構造と、目的に合う正本を探すための索引です。

## 読み始める場所

AIの入口はリポジトリ直下の [`AGENTS.md`](../../AGENTS.md) です。プロジェクト設定の入口は [`project/00_project_policy.md`](project/00_project_policy.md) です。

task promptが指定されている場合は、そのpromptにある `必須参照ルール` と `参照するファイル` から、今回必要な資料へ進みます。promptを探す場合は [`prompts/README.md`](../../prompts/README.md) を参照してください。

```text
AGENTS.md
  ↓
project/00_project_policy.md
  ↓
指定された prompts/*.md
  ↓
promptが示す必須参照ルールと作業対象資料
```

task promptが指定されていない作業の入口は、[`AGENTS.md`](../../AGENTS.md) の作業分類にあります。

## core・project・taskの関係

| 層 | 役割 | 場所 |
|---|---|---|
| core | プロジェクトに依存しない共通原則 | [`core/`](core/) |
| project | coreをこのスターターキットで具体化した設定 | [`project/`](project/) |
| task | 個別作業の手順と作業対象 | [`prompts/`](../../prompts/README.md) |

各層の関係、変更時の扱い、プロジェクト設定の見方は [`project/00_project_policy.md`](project/00_project_policy.md) を参照してください。

## coreの正本

| ファイル | 主な内容 |
|---|---|
| [`core/10_workflow.md`](core/10_workflow.md) | 進め方、変更の整理、正式資料と実装の整合 |
| [`core/20_approval_and_review.md`](core/20_approval_and_review.md) | 承認、レビュー、次工程移行判定 |
| [`core/30_change_safety.md`](core/30_change_safety.md) | 変更範囲、保護対象、共通化の安全境界 |
| [`core/40_official_docs_and_context.md`](core/40_official_docs_and_context.md) | 正式資料、管理記録、補助コンテキストの区別 |
| [`core/50_records_and_reporting.md`](core/50_records_and_reporting.md) | 現在地メモ、完了報告、レビュー補助メモ |
| [`core/60_work_notes.md`](core/60_work_notes.md) | 作業メモに共通する原則 |

## projectの正本

| ファイル | 主な内容 |
|---|---|
| [`project/00_project_policy.md`](project/00_project_policy.md) | プロジェクト識別と設定索引 |
| [`project/10_document_structure.md`](project/10_document_structure.md) | 成果物の分類、配置、命名 |
| [`project/15_document_templates.md`](project/15_document_templates.md) | 成果物とテンプレートの対応 |
| [`project/20_workflow.md`](project/20_workflow.md) | 工程、承認を置く位置、各種フロー |
| [`project/25_review_policy.md`](project/25_review_policy.md) | レビュー結果と集計の運用 |
| [`project/30_development_rules.md`](project/30_development_rules.md) | 技術構成、実装規約、役割分担 |
| [`project/40_testing_rules.md`](project/40_testing_rules.md) | テストの単位、検証方法、配置 |
| [`project/50_ai_permissions.md`](project/50_ai_permissions.md) | AIの権限、保護対象、承認欄の場所 |
| [`project/60_work_notes.md`](project/60_work_notes.md) | 作業メモの保存方法と運用 |
| [`project/70_feature_loop.md`](project/70_feature_loop.md) | オートモード（stage、Gate、判定値、stage × role の変更範囲、モデル役割、Gate記録） |

## 関連する入口

- prompt一覧: [`prompts/README.md`](../../prompts/README.md)
- promptの使い方: [`docs/how_to_use_prompts.md`](../how_to_use_prompts.md)
- テンプレート一覧: [`docs/templates/README.md`](../templates/README.md)
- 補助コンテキスト: [`docs/context/README.md`](../context/README.md)
- 作業メモ: [`docs/context/work_notes/README.md`](../context/work_notes/README.md)
- 旧AI作業ログ: [`docs/context/ai_work_logs/README.md`](../context/ai_work_logs/README.md)
