# tasks

## 目的

`cli_text_masker` / `ascii_digit_masker` の作業状態を、人間とAIが引き継ぎやすくするための現在地メモです。

このファイルは作業中の現在地を示すために使います。
仕様、設計、テスト計画、レビュー結果の代わりにはしません。

## 現在の状態

- command/app: `cli_text_masker`
- feature: `ascii_digit_masker`
- 状態: G2（`23_test_plan.md`、`24_review_checklist.md` 作成済み、G2 Gate未実施）
- 最終更新: 2026-08-23

## 作業メモ

- [x] `20_spec.md` を作成・CP1承認済み（`gates/0001_20260823T135833_cp1.md` で `PASS`）
- [x] `21_design.md` を作成（`mask_ascii_digits` 関数1件、REQ-001〜REQ-006に対応）
- [x] `22_flow.md` を作成
- [x] G1 Gate のレビューを実施（`gates/0002_20260823T161708_g1.md` で `PASS`）
- [x] `23_test_plan.md` を作成（TV-001〜TV-006、REQ-001〜REQ-006に対応）
- [x] `24_review_checklist.md` を作成（実装開始条件: `auto`）
- [ ] G2 Gate のレビューを実施する

## 次に確認すること

- G2 Gate（レビュー）の実施

## 注意点

- `mask_ascii_digits` 関数1つでREQ-001〜REQ-006を満たせるため、関数分割は行っていない。
