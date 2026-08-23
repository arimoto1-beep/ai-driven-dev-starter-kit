# cli_uppercase_text overview

## コマンド/アプリの目的

`cli_uppercase_text` は、入力文字列を大文字へ変換する小さなCLIの実験用command/appです。

## 機能一覧

| feature | 役割 | ドキュメント |
|---|---|---|
| `uppercase` | 入力文字列を大文字へ変換する | `docs/cli_uppercase_text/features/uppercase/` |

## uppercase feature の責務

- 文字列を1つ受け取る
- Python の `str.upper()` 相当で大文字へ変換する
- 変換後の文字列を返す
- CLI引数解析や標準出力は担当しない

## 利用イメージ

`uppercase("Hello 123")` は `"HELLO 123"` を返します。

空文字列 `""` は許可し、`""` を返します。

## 今回やらないこと

- CLI entrypoint の実装
- ファイル入力
- 複数文字列の一括変換
- 入力が文字列以外の場合の変換や独自エラー処理
- locale 固有の変換ルール
- GUI
- 外部API
- CI/CD
- デプロイ

## Boundary

入力は Python の `str`、出力も Python の `str` とします。

feature は文字列変換だけを担当し、入出力処理は持ちません。

## 変更時の注意点

- 仕様にない便利機能を追加しない
- `src/common/` へ共通化しない
- 他のcommand/appを変更しない
