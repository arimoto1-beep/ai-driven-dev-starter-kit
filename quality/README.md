# 品質情報案内

## このディレクトリについて

`quality/` には、補助ツールが記録・集約した検証とレビューの情報があります。この README は生成物への入口であり、品質基準や判定値は定義しません。

## 内容

| 場所 | 内容 |
|---|---|
| [`report.md`](report.md) | 検証記録とレビュー結果を集約した品質サマリ |
| [`events/`](events/) | 検証の実行単位で生成される個別イベント記録 |

個別イベントは生成のたびに増えるため、この README ではファイルごとの一覧を管理しません。

## 生成元

- [`tools/quality_run.py`](../tools/quality_run.py): 検証コマンドを実行し、`events/` に記録する
- [`tools/quality_report.py`](../tools/quality_report.py): `events/` とレビュー結果を読み、`report.md` を生成する
- ツールの入口: [`tools/README.md`](../tools/README.md)

## 関連するルール

- レビュー結果と集計の運用: [`docs/rules/project/25_review_policy.md`](../docs/rules/project/25_review_policy.md)
- 次工程移行判定: [`docs/rules/core/20_approval_and_review.md`](../docs/rules/core/20_approval_and_review.md)
- テストの実行方法: [`docs/rules/project/40_testing_rules.md`](../docs/rules/project/40_testing_rules.md)
