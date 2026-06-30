# AI駆動開発 品質サマリ

## 検証ログサマリ

- 対象タスク数: 1
- テスト実行済みタスク数: 1
- 初回テスト通過タスク数: 1
- 初回テスト失敗タスク数: 0
- 最終テスト通過タスク数: 1
- テスト実行回数: 1
- タスクあたり平均テスト実行回数: 1.00

### タスク別結果

| task_id | runs | first_result | final_result |
|---|---:|---|---|
| sample | 1 | test_passed | test_passed |

## レビューサマリ

- feature 単体レビュー結果数: 2
- command/app 全体レビュー結果数: 2

### 最終判定

- OK: 2
- 軽微な指摘あり: 2
- 要修正: 0
- 要仕様確認: 0

### 次工程移行判定

- GO: 3
- 条件付きGO: 1
- STOP: 0

### レビュー結果一覧

| 種別 | ファイル | 最終判定 | 次工程移行判定 |
|---|---|---|---|
| command/app | `docs\cli_hello_greeting\12_command_review_result.md` | 軽微な指摘あり | 条件付きGO |
| feature | `docs\cli_hello_greeting\features\greeting\25_review_result.md` | OK | GO |
| command/app | `docs\cli_text_counter\12_command_review_result.md` | 軽微な指摘あり | GO |
| feature | `docs\cli_text_counter\features\text_counter\25_review_result.md` | OK | GO |

## 注意

このサマリは、実装バグ率や品質保証結果を示すものではありません。
AI駆動開発におけるテスト実行、修正ループ、レビュー判定の証跡として利用します。
最終的な品質判断は、このサマリではなく、人間によるレビューと受け入れ判断で行います。
