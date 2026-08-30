# 品質情報案内

## このディレクトリについて

`quality/` には、補助ツールが記録・集約した検証とレビューの情報があります。この README は生成物への入口であり、品質基準や判定値は定義しません。

## 内容

| 場所 | 内容 |
|---|---|
| [`report.md`](report.md) | 検証記録とレビュー結果を集約した品質サマリ |
| [`events/`](events/) | 検証の実行単位で生成される個別イベント記録 |

個別イベントは生成のたびに増えるため、この README ではファイルごとの一覧を管理しません。

## Gate記録との違い

オートモードで feature を進めると、feature ごとに **Gate記録**（`docs/<command_or_app_name>/features/<feature_name>/gates/`）が作られます。
`quality/` とは目的が異なります。

| | 何のためのものか | どこにあるか |
|---|---|---|
| **Gate記録** | **1つの feature を進める過程の履歴。** 各段階の判定、人間の承認、停止した理由を1件1ファイルで残す | 対象 feature の `gates/` |
| **`quality/`** | **検証記録とレビュー結果の集約。** 複数の feature / command/app を横断して品質情報を確認する | このディレクトリ |

**Gate記録は `quality/` へ自動で集約されません。** `tools/quality_report.py` が読むのは、
`docs/` 配下の `25_review_result.md` と `12_command_review_result.md` です。

オートモードでも、CP3 の Reviewer が Gate記録に加えて `25_review_result.md` を作成・更新します。
**レビュー結果4値と次工程移行判定は、従来どおり `25_review_result.md` に記録されます。**
そのため、**集計の仕組みはオートモードでも変わりません。**

定義の正本は [`docs/rules/project/25_review_policy.md`](../docs/rules/project/25_review_policy.md)（レビュー結果と集計）と
[`docs/rules/project/70_feature_loop.md`](../docs/rules/project/70_feature_loop.md)（Gate記録）です。

## 生成元

- [`tools/quality_run.py`](../tools/quality_run.py): 検証コマンドを実行し、`events/` に記録する
- [`tools/quality_report.py`](../tools/quality_report.py): `events/` とレビュー結果を読み、`report.md` を生成する
- ツールの入口: [`tools/README.md`](../tools/README.md)

## 関連するルール

- レビュー結果と集計の運用: [`docs/rules/project/25_review_policy.md`](../docs/rules/project/25_review_policy.md)
- Gate記録（オートモード）: [`docs/rules/project/70_feature_loop.md`](../docs/rules/project/70_feature_loop.md)
- 次工程移行判定: [`docs/rules/core/20_approval_and_review.md`](../docs/rules/core/20_approval_and_review.md)
- テストの実行方法: [`docs/rules/project/40_testing_rules.md`](../docs/rules/project/40_testing_rules.md)
