# prompt 一覧

## このディレクトリについて

`prompts/` には、作業の種類ごとの task prompt があります。使い方と依頼時に渡す情報は [`docs/how_to_use_prompts.md`](../docs/how_to_use_prompts.md) を確認してください。

各 prompt の具体的な手順、必須参照ルール、参照対象、変更範囲は、その prompt 自身に記載されています。ルールの正本は [`docs/rules/`](../docs/rules/README.md) 配下です。

## オートモード（feature 収束ループ）

`tools/feature_runner.py` が、この2本を別プロセスとして分離して起動します。Reviewer だけを動かす実行もあります（`--spec-review` / `--review-current`）。単独で手動実行することもできます。
仕組みの正本は [`docs/rules/project/70_feature_loop.md`](../docs/rules/project/70_feature_loop.md) です。

| prompt | 用途 |
|---|---|
| [`run_stage.md`](run_stage.md) | **Worker**。stage の成果物を作成し、FINDING を修正する |
| [`review_stage.md`](review_stage.md) | **Reviewer**。stage をレビューし、収束を判定し、Gate記録を作成する |

下記の個別 prompt は、**マニュアルモード**として従来どおり利用できます。オートモードの Worker は、これらの個別 prompt へ委譲します。

## 文書・設計作成

| prompt | 用途 |
|---|---|
| [`create_overview.md`](create_overview.md) | コマンド／アプリ全体の概要を作成する |
| [`create_feature_spec.md`](create_feature_spec.md) | feature の仕様を作成する |
| [`create_function_design.md`](create_function_design.md) | feature の関数設計を作成する |
| [`create_function_call_flow.md`](create_function_call_flow.md) | 関数呼び出しの流れを作成する |
| [`create_test_design.md`](create_test_design.md) | feature 単体のテスト計画を作成する |
| [`create_review_checklist.md`](create_review_checklist.md) | feature のレビュー観点を作成する |
| [`create_integration_test_plan.md`](create_integration_test_plan.md) | コマンド／アプリの結合試験計画を作成する |
| [`create_common_design_index.md`](create_common_design_index.md) | 共通設計書の一覧を作成する |
| [`create_file_design.md`](create_file_design.md) | 共通のファイル設計を作成する |
| [`create_data_design.md`](create_data_design.md) | 共通のデータ設計を作成する |
| [`create_db_design.md`](create_db_design.md) | DB 設計を作成する |

## 実装

| prompt | 用途 |
|---|---|
| [`implement_feature.md`](implement_feature.md) | feature 本体と単体テストを実装する |
| [`implement_entrypoint.md`](implement_entrypoint.md) | entrypoint とそのテストを実装する |
| [`implement_integration_test.md`](implement_integration_test.md) | 結合試験を実装する |

## レビュー・分析

| prompt | 用途 |
|---|---|
| [`review_feature_source.md`](review_feature_source.md) | feature 実装直後のソースレビューを行う |
| [`review_feature.md`](review_feature.md) | feature 単体レビューを行う |
| [`review_command.md`](review_command.md) | コマンド／アプリ全体をレビューする |
| [`review_context.md`](review_context.md) | `docs/context/` を横断して関連情報を探す |
| [`review_design_code_consistency.md`](review_design_code_consistency.md) | 正式資料とコードの意味上の整合を確認する |
| [`analyze_code_change_impact.md`](analyze_code_change_impact.md) | コード変更の意味と影響範囲を整理する |

## バグ対応

| prompt | 用途 |
|---|---|
| [`create_bug_report.md`](create_bug_report.md) | バグ報告書を作成する |
| [`investigate_bug.md`](investigate_bug.md) | バグを調査し、調査書を作成する |
| [`create_bug_fix_plan.md`](create_bug_fix_plan.md) | バグ修正計画書を作成する |
| [`implement_bug_fix.md`](implement_bug_fix.md) | バグ修正を実装する |

## context・作業記録

| prompt | 用途 |
|---|---|
| [`prepare_work_note.md`](prepare_work_note.md) | 作業の経緯や現在地を作業メモとして構成する |

## スターターキットの確認・保守

| prompt | 用途 |
|---|---|
| [`review_prompt_integrity.md`](review_prompt_integrity.md) | prompt、テンプレート、導線の完全性を確認する |

## 関連文書

- prompt の使い方: [`docs/how_to_use_prompts.md`](../docs/how_to_use_prompts.md)
- 工程と prompt の対応: [`docs/rules/project/20_workflow.md`](../docs/rules/project/20_workflow.md)
- オートモードの正本: [`docs/rules/project/70_feature_loop.md`](../docs/rules/project/70_feature_loop.md)
- ルール体系の索引: [`docs/rules/README.md`](../docs/rules/README.md)
