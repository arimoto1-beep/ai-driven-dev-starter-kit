# コマンド/アプリ概要を作成してください

あなたは、このリポジトリのAI駆動開発ルールに従う設計補助者です。

このプロンプトは、コマンド/アプリ単位の `10_overview.md` を作成または更新するためのものです。

`10_overview.md` は、個別 feature の仕様を作る前に、コマンド/アプリ全体の目的、Boundary、入口、feature 分割方針を整理するためのドキュメントです。

利用者は、チャットで「参照するプロンプトのパス」と「対象情報」を渡して使います。
このプロンプト本文を直接書き換える運用は想定しません。

## 必須参照ルール

この節は、この task で必ず読むルール文書**一覧**の正本です。各ルールの**内容**は、ここに列挙したルール文書を正本とします。このプロンプトが core や project を再定義するものではありません。

`## 参照するファイル` は今回の作業対象資料であり、このルール文書一覧とは役割が異なります。

### 作業開始時に読む

- `docs/rules/core/10_workflow.md`
- `docs/rules/core/40_official_docs_and_context.md`
- `docs/rules/project/10_document_structure.md`
- `docs/rules/project/15_document_templates.md`
- `docs/rules/project/30_development_rules.md`（entrypoint と features の責務、common の扱い）

### 作業完了時に読む

- `docs/rules/core/50_records_and_reporting.md`

---

## 利用者が指定する項目

利用者は、チャットで以下を指定します。

- コマンド/アプリ名: `<command_or_app_name>`
- 種別: `cli` / `api` / `batch` / `job` / `worker` / `other`
- 作りたいもの: `ここに概要を書く`
- 実行イメージまたは利用イメージ: `ここに例を書く`
- 今回やらないこと: `ここに対象外を書く`
- 補足条件: `必要に応じて書く。なければ「なし」`

## 参照するファイル

- `docs/templates/10_overview_template.md`

必要に応じて、既存の以下も参照してください。

- `docs/<command_or_app_name>/10_overview.md`
- `docs/<command_or_app_name>/features/`

## 作成または更新するファイル

- `docs/<command_or_app_name>/10_overview.md`

## 変更してよいファイル

- `docs/<command_or_app_name>/10_overview.md`
- `docs/<command_or_app_name>/tasks.md`
  - ただし、現在地と次に確認することを短く更新する場合に限る

## 変更してはいけないファイル

明示指示がない限り、以下は変更しないでください。
ただし、変更してよいファイルに記載した `tasks.md` の必要最小限の更新は例外です。

- `AGENTS.md`
- `README.md`
- `docs/overview.md`
- `docs/how_to_use_prompts.md`
- `docs/templates/`
- `prompts/`
- `src/`
- `tests/`
- `src/common/`
- 他のコマンド/アプリ配下
- 個別 feature 配下のドキュメント

## 作業範囲

1. `docs/templates/10_overview_template.md` を確認してください
2. 利用者が指定した項目を確認してください
3. 情報が不足している場合は、いきなり `10_overview.md` を作成せず、確認事項だけを提示してください
4. 情報がそろっている場合のみ、`docs/templates/10_overview_template.md` の見出し構成を維持して `10_overview.md` を作成または更新してください
5. `10_overview.md` には、コマンド/アプリ全体の目的、Boundary、入口、feature 分割方針を記載してください
6. 個別 feature の分割案を提示してください
7. ただし、このプロンプトでは個別 feature の `20_spec.md` は作成しないでください
8. 不明点を補う必要がある場合は、勝手に決めず `仮定` として明記してください

## 情報不足時のルール

利用者が指定した内容だけで `10_overview.md` を作るには情報が不足している場合は、先に「確認事項」を提示してください。

特に以下が不明な場合は、確認を優先してください。

- 何を作るか
- コマンド/アプリの利用イメージ
- 入力
- 出力
- 今回やらないこと
- 入口の種別
- 外部依存の有無
- feature 分割の前提

ただし、実行イメージや利用イメージから明確に読み取れる場合は、それをもとに整理して構いません。

## feature 分割方針

feature 分割案を出す場合は、以下の観点で整理してください。

- 入力と出力が説明できるか
- 1つの責務に閉じているか
- 単体テストの観点を書けるか
- `entrypoint.py` にロジックを寄せすぎていないか
- `src/common/` へ早すぎる共通化をしていないか
- 1つの feature が大きくなりすぎていないか
- 逆に関数単位まで細かくしすぎていないか
- 今回やらないことに含まれる feature を混ぜていないか

feature 分割案は、まだ確定ではありません。

人間レビュー後に、必要な feature について `create_feature_spec.md` を使って `20_spec.md` を作成します。

## 10_overview.md に記載する内容

`10_overview.md` には、以下を整理してください。

- 目的
- 背景
- 想定する利用者
- 実行単位
- 実行イメージ
- このコマンド/アプリが担当すること
- このコマンド/アプリが担当しないこと
- Boundary
- 機能一覧
- feature 分割方針
- entrypoint の責務
- entrypoint に入れないこと
- features 配下の責務
- common の扱い
- 今回やらないこと
- 未決事項
- 仕様変更時の扱い
- 変更時の注意点

## 禁止事項

- 情報不足のまま `10_overview.md` を作成しないでください
- 個別 feature の `20_spec.md` を勝手に作成しないでください
- `src/` を変更しないでください
- `tests/` を変更しないでください
- `src/common/` を作成・更新しないでください
- `AGENTS.md` を変更しないでください
- `prompts/` を変更しないでください
- `docs/templates/` を変更しないでください
- 仕様にない便利機能を追加しないでください
- feature 分割案を確定事項として扱わないでください

## 作業後の報告

作業後は、以下を簡潔に報告してください。

- 作成または更新したファイル
- 参照したファイル
- `10_overview.md` の概要
- 提案した feature 分割案
- 確認事項を提示した場合、その理由
- 仮定を置いた場合、その内容
- 次に作成するとよさそうな feature

## レビュー補助メモ

作業後の報告に、レビュー補助メモを含めてください。
記載項目とルールは `docs/rules/core/50_records_and_reporting.md` の「レビュー補助メモ」に従います（このプロンプトには定義を複製しません）。

レビュー補助メモは作業完了報告（チャット）に出力します。`tasks.md` には書きません。

## 作業後の tasks.md 更新

作業後は、対象 command/app または feature の `tasks.md` を必ず確認してください。

必要に応じて、現在の状態、作業メモ、次に確認すること、引き継ぎに必要な短い注意点だけを更新してください。

`tasks.md` には、仕様・設計・テスト計画・レビュー結果の詳細や長いテストログを書かないでください。
詳細は `10_overview.md`、feature 側の `20_spec.md`、`21_design.md`、`22_flow.md`、`23_test_plan.md`、`24_review_checklist.md`、レビュー結果ファイルなど、それぞれの専用ファイルに記録してください。

`tasks.md` を更新しない場合は、更新しない理由を作業報告に書いてください。
