# チュートリアル案内

## このディレクトリについて

`docs/tutorials/` には、スターターキットの使い方を題材別に試すためのチュートリアルがあります。各工程の詳細は、選んだチュートリアル本文と、そこで参照される prompt・ルールを確認してください。

## どこから読むか

**初めて一連の流れを試す場合は、[`005_automode_first_feature.md`](005_automode_first_feature.md) が入口です。**
人間が仕様を書き、AIが設計から実装まで進め、人間が受け入れる一周を体験します。

### オートモードで進める

runner が各AI工程で Worker と Reviewer を分離して起動し、Gate で判定します。人間は仕様承認（CP1）と受け入れ（CP3）を判断します。

| 試したいこと | チュートリアル |
|---|---|
| **feature 新規開発を一周する（最初の一歩）** | [`005_automode_first_feature.md`](005_automode_first_feature.md) |

### マニュアルモードで進める

人間が個別プロンプトを1つずつ実行します。**工程を細かく確認したい場合に選びます。新しい feature でも利用できます。**

| 試したいこと | チュートリアル |
|---|---|
| 単一 feature の設計・実装・テスト・レビューを一通り試す | [`010_simple_calculator.md`](010_simple_calculator.md) |
| 新しいコマンド／アプリと複数 feature の初期文書構造をゼロから作る | [`020_create_new_sample_from_scratch.md`](020_create_new_sample_from_scratch.md) |
| 実装済み feature の変更について、影響と反映先を整理する | [`030_update_existing_feature.md`](030_update_existing_feature.md) |
| バグの報告から修正計画・承認・実装までの流れを確認する | [`040_bug_fix_flow.md`](040_bug_fix_flow.md) |

**マニュアルモードは旧式ではありません。** 2つの進め方の位置づけは
[`../rules/project/20_workflow.md`](../rules/project/20_workflow.md) を参照してください。

既存機能の変更（030）とバグ対応（040）は、feature 新規開発とは別のフローです。どちらの進め方で feature を作った場合でも使います。

## 関連文書

- リポジトリ全体と feature 開発の流れ: [`../../README.md`](../../README.md)
- オートモードの正本: [`../rules/project/70_feature_loop.md`](../rules/project/70_feature_loop.md)
- runner の使い方: [`../../tools/README.md`](../../tools/README.md)
- prompt の使い方: [`../how_to_use_prompts.md`](../how_to_use_prompts.md)
- prompt 一覧: [`../../prompts/README.md`](../../prompts/README.md)
- ルール体系の索引: [`../rules/README.md`](../rules/README.md)
