# ファイル設計書を作成してください

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
- 共通設計書一覧: `docs/<command_or_app_name>/common_design/30_common_design_index.md`
- ファイル設計書: `docs/<command_or_app_name>/common_design/31_file_design.md`
- 補足条件: `必要に応じて書く。なければ「なし」`

## 参照するファイル

- `docs/<command_or_app_name>/10_overview.md`
- `docs/<command_or_app_name>/common_design/30_common_design_index.md`（存在する場合）
- `docs/templates/31_file_design_template.md`
- 必要に応じて `docs/<command_or_app_name>/features/*/20_spec.md`

## 作成または更新するファイル

- `docs/<command_or_app_name>/common_design/31_file_design.md`

## 変更してよいファイル

- `docs/<command_or_app_name>/common_design/31_file_design.md`
- `docs/<command_or_app_name>/common_design/30_common_design_index.md`
  - ファイル設計書の状態欄を更新する場合に限る
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
- `prompts/`

## 作業範囲

1. `10_overview.md` を確認して、入出力ファイル・中間ファイル・ディレクトリ構成の候補を整理してください
2. 必要に応じて feature の `20_spec.md` を参照し、ファイルの要件を補完してください
3. `docs/templates/31_file_design_template.md` の見出し構成を維持して `31_file_design.md` を作成または更新してください
4. 不明なファイル形式・項目・バリデーション要件は、勝手に補完せず未決事項として記録してください

## 重要ルール

- feature 個別の `21_design.md` に分散したファイル仕様を書かないでください
  - ファイル設計はこの設計書に集約し、feature 個別設計からは参照する形にしてください
- ファイル形式（文字コード・改行コード・項目定義）が不明な場合は、未決事項として記録し、AI判断で確定しないでください
- 既存のファイル設計書がある場合、既存の定義を破壊的に変更しないでください
  - 変更が必要だと判断した場合は、変更候補として報告してください

## 禁止事項

- feature 個別の `21_design.md` を変更しないでください
- `src/`、`tests/` を変更しないでください
- ファイル形式が未確定の場合、AI判断で勝手に確定しないでください
- 既存のファイル設計書を破壊的に変更しないでください

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
- 定義したファイル一覧
- 未決事項の有無
- feature 個別設計が参照すべき箇所の案内（該当する場合）
