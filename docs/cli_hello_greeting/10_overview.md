# cli_hello_greeting overview

## コマンド/アプリの目的

`cli_hello_greeting` は、指定された名前に対してあいさつ文を標準出力へ表示する小さなCLIです。

## 入口ファイル

- `src/cli_hello_greeting/entrypoint.py`

## 機能一覧

| 機能 | 概要 | ドキュメント |
|---|---|---|
| `greeting` | 名前から `Hello, <name>!` 形式の文字列を作る | `docs/cli_hello_greeting/features/greeting/` |

## このコマンド/アプリが担当すること

- CLI引数 `--name` を受け取る
- `greeting` 機能を呼び出す
- 生成したあいさつ文を標準出力へ表示する

## 担当しないこと

- 多言語対応
- 設定ファイル対応
- GUI対応
- 外部API連携
- CI/CD
- デプロイ

結合試験は機能要件には含めません。
command/app 単位の結合確認が必要な場合は、`docs/cli_hello_greeting/11_integration_test_plan.md` で扱います。

## entrypoint の責務

- CLI引数を受け取る
- `features/greeting.py` の機能を呼び出す
- 結果をUTF-8で標準出力に出す
- 正常終了時に終了コード `0` を返す

## 標準出力の文字コード

`entrypoint.py` は、標準出力を UTF-8 として出力します。

- 日本語などASCII以外の文字を含む場合も、UTF-8で出力します。
- 出力文字コードは、実行環境の既定ロケールやコードページに依存させません。
- 標準出力を文字列として受け取る側は、UTF-8としてデコードします。

## features 配下の責務

- 機能固有のロジックを実装する
- 標準出力やCLI引数解析を持たない
- 入力値に対する最小限の機能固有チェックを行う

## common の扱い

`src/common/` は共通処理置き場ですが、人間の明示指示なしに作成・更新しません。
共通化候補がある場合は、設計書やレビュー結果、作業報告に提案として記録します。

## 変更時の注意点

- `entrypoint.py` を厚くしない
- 業務ロジックは `features/` 配下に置く
- 仕様にない便利機能を追加しない
- `src/common/` へ勝手に共通処理を切り出さない
- 対応するテストは `tests/cli_hello_greeting/` 配下に置く
