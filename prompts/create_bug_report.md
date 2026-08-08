# バグ報告書を作成または更新してください

このプロンプトは、バグ報告をもとに `docs/<command_or_app_name>/bugs/<bug_id>/10_bug_report.md` を作成または更新するためのものです。

このプロンプトファイルは直接書き換えず、チャットでこのファイルのパスと下の「利用者が指定する項目」を指定して使います。
それ以外の作業ルールは変更せず、このプロンプトの `## 必須参照ルール` に列挙されたルール文書に従ってください。成果物を作成する場合は、`docs/templates/` の該当テンプレートに従ってください。

---

## 必須参照ルール

この節は、この task で必ず読むルール文書**一覧**の正本です。各ルールの**内容**は、ここに列挙したルール文書を正本とします。このプロンプトが core や project を再定義するものではありません。

`## 参照するファイル` は今回の作業対象資料であり、このルール文書一覧とは役割が異なります。

### 作業開始時に読む

- `docs/rules/core/10_workflow.md`（バグ対応の段階分け。いきなり修正しない）
- `docs/rules/project/15_document_templates.md`
- `docs/rules/project/20_workflow.md`（バグ対応フローの全体像）

### 作業完了時に読む

- `docs/rules/core/50_records_and_reporting.md`

---

## 利用者が指定する項目

- 対象 command/app: `<command_or_app_name>`
- 対象 feature: `<feature_name>`
- バグID: `<bug_id>`（例: `bug_001`）
- バグ報告書の出力先: `docs/<command_or_app_name>/bugs/<bug_id>/10_bug_report.md`
- バグ報告の内容: チャットで提供された報告内容（現象、ログ、再現手順など）
- 補足条件: `必要に応じて書く。なければ「なし」`

## 参照するファイル

- `docs/templates/10_bug_report_template.md`
- 利用者がチャットで提供したバグ報告内容

## 変更してよいファイル

- `docs/<command_or_app_name>/bugs/<bug_id>/10_bug_report.md`（新規作成または更新）

## 変更してはいけないファイル

- このプロンプトファイル
- `AGENTS.md`
- `README.md`
- `docs/templates/`
- `prompts/`
- `src/`（実装コードは一切変更しない）
- `tests/`（テストコードは一切変更しない）
- `docs/<command_or_app_name>/features/` 配下の既存ドキュメント
- `docs/<command_or_app_name>/bugs/<bug_id>/20_bug_investigation.md`
- `docs/<command_or_app_name>/bugs/<bug_id>/30_bug_fix_plan.md`

---

## 作業範囲

1. `docs/templates/10_bug_report_template.md` を参照してください
2. `docs/<command_or_app_name>/bugs/<bug_id>/` フォルダが存在しない場合は作成してください
3. 利用者が提供したバグ報告をもとに `10_bug_report.md` を作成または更新してください
4. 不足している情報がある場合は、削除せず「不足情報」セクションに記録してください
5. この段階では原因を断定しないでください
6. この段階では修正しないでください

## 禁止事項

- 原因を断定しないでください
- 実装コード（`src/`）を変更しないでください
- テストコード（`tests/`）を変更しないでください
- 仕様・設計・テスト計画（`docs/<command_or_app_name>/features/`）を変更しないでください
- `20_bug_investigation.md` や `30_bug_fix_plan.md` を先取りして作成しないでください
- バグ報告の範囲を超えて、調査内容や修正内容を書かないでください

## レビュー補助メモ

作業後の報告に、レビュー補助メモを含めてください。
記載項目とルールは `docs/rules/core/50_records_and_reporting.md` の「レビュー補助メモ」に従います（このプロンプトには定義を複製しません）。

レビュー補助メモは作業完了報告（チャット）に出力します。`tasks.md` には書きません。

## 作業後の tasks.md 更新候補

このプロンプトでは `tasks.md` を直接更新しません。

`tasks.md` の更新が必要と判断した場合は、作業報告に「tasks.md 更新候補」として記載してください。
`tasks.md` の実際の更新は、人間が確認したうえで別作業として行います。

## 作業後の報告

作業後に、以下を簡潔に報告してください。

- 作成または更新したファイル
- バグ報告の概要
- 不足している情報の一覧（なければ「なし」）
- 次にやること（`prompts/investigate_bug.md` を使った原因調査）
