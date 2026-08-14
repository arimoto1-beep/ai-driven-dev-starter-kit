# 補助ツール案内

## このディレクトリについて

`tools/` には、検証結果の記録と品質情報の集約を補助するツールがあります。判定値や品質基準の正本はここではなく、関連する [`docs/rules/`](../docs/rules/README.md) 配下にあります。

## 内容

| ツール | 目的 | 主な入力・確認対象 | 主な出力先 |
|---|---|---|---|
| [`quality_run.py`](quality_run.py) | 指定した検証コマンドを実行し、その開始と結果を記録する | task ID、実行するコマンド | [`quality/events/`](../quality/events/) 配下の JSON Lines ファイル |
| [`quality_report.py`](quality_report.py) | 検証記録とレビュー結果を集約する | `quality/events/` と `docs/` 配下のレビュー結果 | [`quality/report.md`](../quality/report.md) |

生成物の見方と各ファイルの位置づけは、[`quality/README.md`](../quality/README.md) を参照してください。ツールの引数や読み取り処理の詳細は各スクリプト自身にあります。

## 関連するルール

- テストの実行方法: [`docs/rules/project/40_testing_rules.md`](../docs/rules/project/40_testing_rules.md)
- レビュー結果と集計の運用: [`docs/rules/project/25_review_policy.md`](../docs/rules/project/25_review_policy.md)
- 次工程移行判定: [`docs/rules/core/20_approval_and_review.md`](../docs/rules/core/20_approval_and_review.md)
