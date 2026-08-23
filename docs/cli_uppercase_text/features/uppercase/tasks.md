# tasks

## 目的

`cli_uppercase_text` / `uppercase` の作業状態を、人間とAIが引き継ぎやすくするための現在地メモです。

このファイルは作業中の現在地を示すために使います。
仕様、設計、テスト計画、レビュー結果の代わりにはしません。

## 現在の状態

- command/app: `cli_uppercase_text`
- feature: `uppercase`
- 状態: CP1（`21_design.md`、`22_flow.md` 作成済み、Gate未実施）
- 最終更新: 2026-08-23

## 作業メモ

- [x] `20_spec.md` を作成（REQ-001, REQ-002）
- [x] G0 Gate のレビューを実施する（`gates/0002_20260823T114154_g0.md` で `PASS`）
- [x] `21_design.md` を作成（`uppercase` 関数1件、REQ-001/REQ-002に対応）
- [x] `22_flow.md` を作成
- [ ] CP1 Gate のレビューを実施する

## 次に確認すること

- CP1 Gate（レビュー）の実施

## 注意点

- なお、`docs/cli_uppercase_text/features/uppercase/gates/0001_20260823T111952_g0.md` は runner が過去に `BLOCKED(state_error)` として記録した停止記録であり、AIレビューは未実施。今回の `20_spec.md` 作成はこの記録を踏まえたものではなく、`prompts/run_stage.md`（Worker, mode: create）による新規作成である。
