# cli_mask_rework 概要

## 目的

`cli_mask_rework` は、入力文字列に小さな変換を行う学習用CLIです。

## 実行単位

- コマンド/アプリ名: `cli_mask_rework`
- 種別: `cli`
- 入口ファイル: `src/cli_mask_rework/entrypoint.py`

## このコマンド/アプリが担当すること

- CLI引数で入力文字列を受け取る
- feature に文字列変換を委譲する
- feature が返した文字列を標準出力へ表示する

## このコマンド/アプリが担当しないこと

- ファイル入力
- 対話式入力
- GUI対応
- 外部API連携

## Boundary

### 入力境界

- CLI引数で受け取る文字列

### 出力境界

- feature が変換した文字列

### 外部依存

- 外部API、DB、環境変数、外部ファイルへの依存はありません。

## feature 分割方針

文字列変換ごとに独立した feature として扱います。

## entrypoint の責務

- CLI引数を受け取る
- feature を呼び出す
- 結果を標準出力に出す

## features 配下の責務

- feature 固有の文字列変換のみを行う
- CLI引数解析や標準出力を持たない

## common の扱い

今回の範囲では共通化しません。
