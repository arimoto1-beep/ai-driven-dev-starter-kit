# cli_hello_greeting 結合試験計画

## 対象コマンド/アプリ

- コマンド/アプリ名: `cli_hello_greeting`
- 入口ファイル: `src/cli_hello_greeting/entrypoint.py`
- 対象 feature: `greeting`

## 結合試験の目的

`entrypoint.py` から `greeting` feature を呼び出したときに、command/app として期待どおり動くことを確認します。

feature 単体の詳細ロジックは `tests/cli_hello_greeting/features/test_greeting.py` に任せます。
結合試験では、CLI実行、標準出力、終了コード、引数エラー時の扱いを中心に確認します。

## 前提

- Python標準ライブラリのみを使う
- 結合試験は `subprocess` で `entrypoint.py` を実行する
- `entrypoint.py` は薄く保ち、CLI引数解析、feature 呼び出し、標準出力、終了コード返却を担当する
- feature 固有ロジックは `src/cli_hello_greeting/features/greeting.py` に置く

## 対象外

- feature 内部の詳細ロジックの再検証
- `argparse` の詳細なエラーメッセージの固定
- 外部API連携
- CI/CD
- デプロイ

## feature 一覧

| feature | 役割 | 結合試験で確認する観点 |
|---|---|---|
| `greeting` | 名前から `Hello, <name>!` 形式の文字列を作る | `entrypoint.py` 経由で呼び出され、標準出力に表示されること |

## entrypoint の確認観点

- `--name` をCLI引数として受け取れること
- `features.greeting.create_greeting` を呼び出せること
- 生成されたあいさつ文を標準出力に出せること
- 標準出力がUTF-8として扱えること
- 正常系で終了コード `0` になること
- `--name` 未指定時に終了コードが非ゼロになること
- feature 固有ロジックを `entrypoint.py` に持ちすぎていないこと

## 結合試験ケース

| No | ケース | 実行例 | 期待結果 |
|---|---|---|---|
| 1 | 名前指定の正常系 | `python src/cli_hello_greeting/entrypoint.py --name Alice` | 標準出力が `Hello, Alice!`、終了コードが `0` |
| 2 | 日本語名の正常系 | `python src/cli_hello_greeting/entrypoint.py --name 太郎` | 標準出力が `Hello, 太郎!`、終了コードが `0` |
| 3 | `--name` 未指定 | `python src/cli_hello_greeting/entrypoint.py` | 終了コードが非ゼロ |

## テスト実装方針

- `tests/cli_hello_greeting/test_integration_greeting.py` に実装する
- `sys.executable` を使って現在のPythonで `entrypoint.py` を実行する
- 標準出力と終了コードを確認する
- subprocessで標準出力をUTF-8としてデコードする
- 実装がUTF-8を保証していることを日本語出力ケースで確認する
- 異常系では `argparse` の詳細なメッセージまでは固定しない

## 単体試験との役割分担

- feature 単体テストでは、`create_greeting` の正常系、空文字、空白のみを確認する
- entrypoint テストでは、`parse_args` と `main` の直接呼び出しを確認する
- 結合試験では、実際に `entrypoint.py` をプロセス実行したときの入出力と終了コードを確認する

## 未決事項

該当なし

## 改善候補

`10_overview.md` の「担当しないこと」に結合試験が含まれているため、現在のスターターキット方針に合わせるなら、今後「結合試験は必要に応じて扱う」趣旨へ見直す候補があります。

## 作業後報告

この計画に基づき、`tests/cli_hello_greeting/test_integration_greeting.py` を作成します。
