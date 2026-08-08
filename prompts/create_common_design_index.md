# 共通設計書一覧を作成してください

あなたは、このリポジトリのAI駆動開発ルールに従う開発補助者です。

このプロンプトファイルは直接書き換えず、チャットでこのファイルのパスと下の「利用者が指定する項目」を指定して使います。
それ以外の作業ルールは変更せず、このプロンプトの `## 必須参照ルール` に列挙されたルール文書に従ってください。成果物を作成する場合は、`docs/templates/` の該当テンプレートに従ってください。

## 必須参照ルール

この節は、この task で必ず読むルール文書**一覧**の正本です。各ルールの**内容**は、ここに列挙したルール文書を正本とします。このプロンプトが core や project を再定義するものではありません。

`## 参照するファイル` は今回の作業対象資料であり、このルール文書一覧とは役割が異なります。

### 作業開始時に読む

- `docs/rules/core/30_change_safety.md`（横断的な取り決めを個別機能で勝手に定義しない）
- `docs/rules/core/40_official_docs_and_context.md`
- `docs/rules/project/15_document_templates.md`
- `docs/rules/project/30_development_rules.md`（共通設計で扱う対象）

### 作業完了時に読む

- `docs/rules/core/50_records_and_reporting.md`

---

## 利用者が指定する項目

- コマンド/アプリ名: `<command_or_app_name>`
- 対象 overview: `docs/<command_or_app_name>/10_overview.md`
- 共通設計書一覧ファイル: `docs/<command_or_app_name>/common_design/30_common_design_index.md`
- 想定する共通設計: `必要に応じて書く。なければAIが候補を提示する`
- 補足条件: `必要に応じて書く。なければ「なし」`

## 参照するファイル

- `docs/<command_or_app_name>/10_overview.md`
- `docs/templates/30_common_design_index_template.md`
- 必要に応じて `docs/<command_or_app_name>/features/*/20_spec.md`

## 作成または更新するファイル

- `docs/<command_or_app_name>/common_design/30_common_design_index.md`

## 変更してよいファイル

- `docs/<command_or_app_name>/common_design/30_common_design_index.md`
- `docs/<command_or_app_name>/tasks.md`
  - ただし、現在地と次に確認することを短く更新する場合に限る

## 変更してはいけないファイル

変更してよいファイルに記載した `tasks.md` の必要最小限の更新は例外です。

- このプロンプトファイル
- `AGENTS.md`
- `docs/templates/`
- `src/`
- `tests/`
- feature 個別設計（`docs/<command_or_app_name>/features/*/`）
- 既存の共通設計書本体（`31_file_design.md`、`32_data_design.md`、`33_db_design.md`）
- `prompts/`

## 作業範囲

1. `10_overview.md` を読んで、複数 feature にまたがる設計の候補を確認してください
2. 必要に応じて、`docs/<command_or_app_name>/features/*/20_spec.md` を参照して設計候補を補完してください
3. 利用者が指定した「想定する共通設計」と突き合わせて整合を確認してください
4. `docs/templates/30_common_design_index_template.md` の見出し構成を維持して `30_common_design_index.md` を作成または更新してください
5. 作成後、未作成の共通設計書と未決事項を整理して報告してください

## 禁止事項

- 共通設計書本体（`31_file_design.md`、`32_data_design.md`、`33_db_design.md`）を勝手に作成しないでください
  - 一覧を作成した後、各設計書の作成が必要な場合は、対応するプロンプトを使ってください
- feature 個別設計を変更しないでください
- `src/`、`tests/` を変更しないでください
- DB種別、テーブル、ファイル形式などを、この段階で確定しないでください
  - 候補があれば「未決事項」として記録してください
- 人間が「想定する共通設計」を指定した場合、それを無視して独自の判断で上書きしないでください

## レビュー補助メモ

作業後の報告に、レビュー補助メモを含めてください。
記載項目とルールは `docs/rules/core/50_records_and_reporting.md` の「レビュー補助メモ」に従います（このプロンプトには定義を複製しません）。

レビュー補助メモは作業完了報告（チャット）に出力します。`tasks.md` には書きません。

## 作業後の tasks.md 更新

作業後は、対象 command/app の `tasks.md` を必ず確認してください。

必要に応じて、現在の状態、次に確認すること、引き継ぎに必要な短い注意点だけを更新してください。

`tasks.md` を更新しない場合は、更新しない理由を作業報告に書いてください。

## 作業後の報告

作業後に、以下を簡潔に報告してください。

- 作成または更新したファイル
- 参照したファイル
- 必要と判断した共通設計書の一覧
- 未作成の共通設計書と推奨する次の手順
- 未決事項の有無
