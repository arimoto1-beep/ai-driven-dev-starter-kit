# 結合試験計画を作成してください

あなたは、このリポジトリのAI駆動開発ルールに従うテスト設計補助者です。

このプロンプトは、コマンド/アプリ単位の結合試験計画を作成または更新するためのものです。

このリポジトリにおける結合試験は、`entrypoint.py` から複数の feature を束ねて呼び出し、コマンド/アプリとして期待どおり動くことを確認する試験です。

feature 単体の詳細ロジックは、各 feature の `23_test_plan.md` と単体テストで確認します。

結合試験では、entrypoint、feature 呼び出し、入出力、終了コード、エラー時の扱い、10_overview.md との整合を確認します。

このプロンプトファイルは直接書き換えず、チャットでこのファイルのパスと「利用者が指定する項目」を指定して使います。

## 必須参照ルール

この節は、この task で必ず読むルール文書**一覧**の正本です。各ルールの**内容**は、ここに列挙したルール文書を正本とします。このプロンプトが core や project を再定義するものではありません。

`## 参照するファイル` は今回の作業対象資料であり、このルール文書一覧とは役割が異なります。

### 作業開始時に読む

- `docs/rules/core/10_workflow.md`
- `docs/rules/project/15_document_templates.md`
- `docs/rules/project/40_testing_rules.md`

### 作業完了時に読む

- `docs/rules/core/50_records_and_reporting.md`

---

## 利用者が指定する項目

利用者は、チャットで以下を指定します。

- コマンド/アプリ名: `<command_or_app_name>`
- 対象 overview: `docs/<command_or_app_name>/10_overview.md`
- 作成または更新する結合試験計画: `docs/<command_or_app_name>/11_integration_test_plan.md`
- 対象 entrypoint: `src/<command_or_app_name>/entrypoint.py`
- 対象 feature: `必要に応じて feature 名を書く。全体対象の場合は「10_overview.md の機能一覧に従う」`
- 補足条件: `必要に応じて書く。なければ「なし」`

## 参照するファイル

- `docs/templates/11_integration_test_plan_template.md`
- `docs/<command_or_app_name>/10_overview.md`
- `src/<command_or_app_name>/entrypoint.py`

必要に応じて、以下も参照してください。

- `docs/<command_or_app_name>/features/<feature_name>/20_spec.md`
- `docs/<command_or_app_name>/features/<feature_name>/21_design.md`
- `docs/<command_or_app_name>/features/<feature_name>/22_flow.md`
- `docs/<command_or_app_name>/features/<feature_name>/23_test_plan.md`
- `tests/<command_or_app_name>/features/test_<feature_name>.py`

## 作成または更新するファイル

- `docs/<command_or_app_name>/11_integration_test_plan.md`

## 変更してよいファイル

- `docs/<command_or_app_name>/11_integration_test_plan.md`
- `docs/<command_or_app_name>/tasks.md`
- `docs/<command_or_app_name>/features/<feature_name>/tasks.md`
  - 対象 feature が明確な場合のみ、現在地と次に確認することを短く更新する場合に限る

## 変更してはいけないファイル

明示指示がない限り、以下は変更しないでください。
ただし、変更してよいファイルに記載した `tasks.md` の必要最小限の更新は例外です。

- このプロンプトファイル
- `AGENTS.md`
- `README.md`
- `docs/overview.md`
- `docs/how_to_use_prompts.md`
- `docs/templates/`
- `docs/<command_or_app_name>/10_overview.md`
- `docs/<command_or_app_name>/features/`
- `src/`
- `tests/`
- `src/common/`
- `prompts/`
- 他のコマンド/アプリ配下
- CI/CD、デプロイ関連のファイル

## 作業範囲

1. `docs/templates/11_integration_test_plan_template.md` を確認してください
2. `docs/<command_or_app_name>/10_overview.md` を確認してください
3. `src/<command_or_app_name>/entrypoint.py` を確認してください
4. 対象 feature の設計ドキュメントを必要に応じて確認してください
5. entrypoint から feature を束ねて呼び出す観点を整理してください
6. 単体試験と結合試験の役割を分けてください
7. `docs/templates/11_integration_test_plan_template.md` の見出し構成を維持して `11_integration_test_plan.md` を作成または更新してください
8. 不明点がある場合は、勝手に決めず `仮定` として明記するか、確認事項として提示してください

## 結合試験の考え方

このリポジトリでは、結合試験を以下のように扱います。

- feature 単体の詳細ロジックを再確認する場ではない
- entrypoint から feature を正しく呼び出せるかを見る
- 入力が feature に渡り、結果が出力へ反映される流れを見る
- 複数 feature を束ねる場合の流れを見る
- 10_overview.md の Boundary と矛盾していないかを見る
- CLIであれば、コマンド実行として期待どおり動くかを見る

## 観点整理の方針

以下の観点を整理してください。

- 正常系
- 異常系
- entrypoint から feature への受け渡し
- feature から entrypoint への戻り値
- 標準出力またはレスポンス
- 終了コード
- エラー時の扱い
- 10_overview.md との整合
- feature 単体試験と重複しすぎていないか
- 外部依存を勝手に増やしていないか

## 情報不足時のルール

結合試験計画を作るには情報が不足している場合は、いきなり `11_integration_test_plan.md` を作成しないでください。

先に「確認事項」として、不足している情報を箇条書きで提示してください。

特に以下が不明な場合は、確認を優先してください。

- 対象 entrypoint
- 結合対象となる feature
- コマンド/アプリとしての入力
- コマンド/アプリとしての出力
- 正常系の期待結果
- 異常系の期待結果
- 10_overview.md の Boundary

ただし、`10_overview.md`、`entrypoint.py`、feature の設計ドキュメントから明確に読み取れる場合は、それをもとに整理して構いません。

## 禁止事項

- 情報不足のまま `11_integration_test_plan.md` を作成しないでください
- `10_overview.md` と矛盾する結合試験計画を作成しないでください
- feature 単体試験で確認すべき詳細ロジックを、結合試験に過剰に持ち込まないでください
- `entrypoint.py` や feature 実装を変更しないでください
- テストコードを作成しないでください
- `src/common/` を作成・更新しないでください
- 外部API、CI/CD、デプロイ資産を追加しないでください
- 仕様にない便利機能を提案する場合は、今後の改善候補として分けてください
- 結合試験計画の作成中に、entrypoint や feature 実装が結合試験しにくい構造だと判断した場合でも、勝手に `src/` を変更しないでください。
  変更が必要そうな場合は、テストしにくい理由、影響するファイル、見直し候補を `11_integration_test_plan.md` の未決事項または改善候補として記載してください。
  実装側の変更が必要かどうかは、人間レビューで判断します。

## 作業後の報告

作業後は、以下を簡潔に報告してください。

- 作成または更新したファイル
- 参照したファイル
- 結合試験計画の概要
- 対象 entrypoint
- 対象 feature
- 主な正常系
- 主な異常系
- 10_overview.md との整合確認結果
- 確認事項を提示した場合、その理由
- 仮定を置いた場合、その内容

## レビュー補助メモ

作業後の報告に、レビュー補助メモを含めてください。
記載項目とルールは `docs/rules/core/50_records_and_reporting.md` の「レビュー補助メモ」に従います（このプロンプトには定義を複製しません）。

レビュー補助メモは作業完了報告（チャット）に出力します。`tasks.md` には書きません。

## 作業後の tasks.md 更新

作業後は、対象 command/app または feature の `tasks.md` を必ず確認してください。

必要に応じて、現在の状態、作業メモ、次に確認すること、引き継ぎに必要な短い注意点だけを更新してください。

`tasks.md` には、仕様・設計・テスト計画・レビュー結果の詳細や長いテストログを書かないでください。
詳細は `10_overview.md`、`20_spec.md`、`21_design.md`、`22_flow.md`、`23_test_plan.md`、`24_review_checklist.md`、`11_integration_test_plan.md`、レビュー結果ファイルなど、それぞれの専用ファイルに記録してください。

`tasks.md` を更新しない場合は、更新しない理由を作業報告に書いてください。
