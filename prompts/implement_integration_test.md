# 結合試験を実装してください

あなたは、このリポジトリのAI駆動開発ルールに従うテスト実装担当者です。

このプロンプトは、コマンド/アプリ単位の結合試験計画をもとに、結合試験コードを作成または更新するためのものです。

このリポジトリにおける結合試験は、`entrypoint.py` から複数の feature を束ねて呼び出し、コマンド/アプリとして期待どおり動くことを確認する試験です。

feature 単体の詳細ロジックは、各 feature の単体試験で確認します。

結合試験では、entrypoint、feature 呼び出し、入出力、終了コード、エラー時の扱い、`10_overview.md` との整合を確認します。

このプロンプトファイルは直接書き換えず、チャットでこのファイルのパスと「利用者が指定する項目」を指定して使います。

テスト実装中に、entrypoint や feature 実装がテストしにくいと判断した場合でも、勝手に `src/` を変更しないでください。
その場合は、テストしにくい理由、影響するファイル、見直し候補を作業報告に記載してください。
実装側の変更が必要かどうかは、人間レビューで判断します。

## 必須参照ルール

この節は、この task で必ず読むルール文書**一覧**の正本です。各ルールの**内容**は、ここに列挙したルール文書を正本とします。このプロンプトが core や project を再定義するものではありません。

`## 参照するファイル` は今回の作業対象資料であり、このルール文書一覧とは役割が異なります。

### 作業開始時に読む

- `docs/rules/core/10_workflow.md`
- `docs/rules/core/30_change_safety.md`（テストしにくくても `src/` を勝手に変更しない）
- `docs/rules/project/30_development_rules.md`
- `docs/rules/project/40_testing_rules.md`

### 作業完了時に読む

- `docs/rules/core/50_records_and_reporting.md`

---

## 利用者が指定する項目

利用者は、チャットで以下を指定します。

- コマンド/アプリ名: `<command_or_app_name>`
- 対象 overview: `docs/<command_or_app_name>/10_overview.md`
- 対象 結合試験計画: `docs/<command_or_app_name>/11_integration_test_plan.md`
- 対象 entrypoint: `src/<command_or_app_name>/entrypoint.py`
- 作成または更新するテストファイル: `tests/<command_or_app_name>/test_integration_<short_name>.py`
- 対象 feature: `必要に応じて feature 名を書く。全体対象の場合は「11_integration_test_plan.md に従う」`
- short_name: `単一 feature の command/app では feature 名。複数 feature を束ねる command/app では command/app を短く表す名前`
- 補足条件: `必要に応じて書く。なければ「なし」`

## 参照するファイル

- `docs/<command_or_app_name>/10_overview.md`
- `docs/<command_or_app_name>/11_integration_test_plan.md`
- `src/<command_or_app_name>/entrypoint.py`

必要に応じて、以下も参照してください。

- `docs/<command_or_app_name>/features/<feature_name>/20_spec.md`
- `docs/<command_or_app_name>/features/<feature_name>/21_design.md`
- `docs/<command_or_app_name>/features/<feature_name>/22_flow.md`
- `docs/<command_or_app_name>/features/<feature_name>/23_test_plan.md`
- `src/<command_or_app_name>/features/<feature_name>.py`
- `tests/<command_or_app_name>/features/test_<feature_name>.py`

## 作成または更新するファイル

- `tests/<command_or_app_name>/test_integration_<short_name>.py`

## 変更してよいファイル

- `tests/<command_or_app_name>/test_integration_<short_name>.py`

## 変更してはいけないファイル

この節は、**今回の task で変更を許可されていないファイル**です。project が定める**保護対象**（`docs/rules/project/50_ai_permissions.md`）とは別のレイヤであり、両方を満たす必要があります。

明示指示がない限り、以下は変更しないでください。

- このプロンプトファイル
- `AGENTS.md`
- `README.md`
- `docs/overview.md`
- `docs/how_to_use_prompts.md`
- `docs/templates/`
- `docs/<command_or_app_name>/10_overview.md`
- `docs/<command_or_app_name>/11_integration_test_plan.md`
- `docs/<command_or_app_name>/features/`
- `src/`
- `src/common/`
- `tests/<command_or_app_name>/features/`
- `prompts/`
- 他のコマンド/アプリ配下
- CI/CD、デプロイ関連のファイル

## ファイル出力先と命名に関する追加ルール（最小反映）

- 結合試験の標準出力先は `tests/<command_or_app_name>/test_integration_<short_name>.py` です。
- `<short_name>` は、単一 feature の command/app では feature 名を使います。複数 feature を束ねる command/app では、command/app を短く表す名前を使います。
- 利用者が指定した出力先パス（例: `tests/<command_or_app_name>/test_integration_<short_name>.py`）は、AIの判断で変更してはなりません。
- `pytest` の import mismatch やテストファイル名の衝突が発生した場合でも、標準命名ルールと現状の差分を確認せずに、AI判断で別名ファイルを作成しないでください。

確認事項には、発生した問題、衝突しているファイル、指定された出力先、標準命名ルールとの差分、代替案、推奨案、人間に判断してほしい点を含めて提示してください。

## 作業範囲

1. `docs/<command_or_app_name>/10_overview.md` を確認してください
2. `docs/<command_or_app_name>/11_integration_test_plan.md` を確認してください
3. `src/<command_or_app_name>/entrypoint.py` を確認してください
4. 必要に応じて対象 feature の仕様、設計、単体テストを確認してください
5. 結合試験計画に沿って、`tests/<command_or_app_name>/test_integration_<short_name>.py` を作成または更新してください
6. 結合試験は、entrypoint から feature を束ねて呼び出す流れを確認する範囲に限定してください
7. 実装後、可能であれば `python -m pytest` を実行してください
8. `python -m pytest` が環境理由で失敗する場合は、利用可能な Python 実体で代替実行してください
9. 実行したコマンドと結果を正確に報告してください

## 結合試験の実装方針

結合試験では、以下を中心に確認してください。

- entrypoint を通してコマンド/アプリとして動くこと
- CLI引数や入力が feature に渡ること
- feature の結果が、標準出力や終了コードに反映されること
- 異常系で、コマンド/アプリとして期待する扱いになること
- `10_overview.md` の Boundary と矛盾していないこと
- `11_integration_test_plan.md` の観点に対応していること

## 単体試験との分担

結合試験では、feature 内部の詳細ロジックを過剰に確認しないでください。

feature 内部の詳細は、以下で確認します。

- `docs/<command_or_app_name>/features/<feature_name>/23_test_plan.md`
- `tests/<command_or_app_name>/features/test_<feature_name>.py`

結合試験では、entrypoint と feature の接続、入出力、終了コード、エラー時の扱いを中心に確認してください。

## テスト実装の注意点

- `pytest` を使ってください
- 外部APIや外部システムには接続しないでください
- 実ファイル操作が必要な場合は、`tmp_path` などの一時領域を使ってください
- 標準出力の確認が必要な場合は、`capsys` を使ってください
- サブプロセス実行が必要な場合は、標準ライブラリの `subprocess` を使ってください
- 実行環境に依存しすぎるテストは避けてください
- テストを通すために実装側を勝手に変更しないでください

## 情報不足時のルール

結合試験を実装するには情報が不足している場合は、いきなりテストファイルを作成または更新しないでください。

先に「確認事項」として、不足している情報を箇条書きで提示してください。

特に以下が不明な場合は、確認を優先してください。

- 対象 entrypoint
- 結合試験計画
- コマンド/アプリとしての入力
- コマンド/アプリとしての出力
- 正常系の期待結果
- 異常系の期待結果
- 終了コード
- 標準出力またはレスポンス
- 外部依存の有無

ただし、`10_overview.md`、`11_integration_test_plan.md`、`entrypoint.py`、feature の設計ドキュメントから明確に読み取れる場合は、それをもとに整理して構いません。

## 禁止事項

- 情報不足のまま結合試験を実装しないでください
- `11_integration_test_plan.md` と矛盾するテストを作成しないでください
- feature 単体試験で確認すべき詳細ロジックを、結合試験に過剰に持ち込まないでください
- テストを通すために `src/` を変更しないでください
- `entrypoint.py` や feature 実装を変更しないでください
- `src/common/` を作成・更新しないでください
- `docs/` を変更しないでください
- `AGENTS.md` を変更しないでください
- `prompts/` を変更しないでください
- CI/CD、デプロイ資産を追加しないでください
- 外部APIや外部システムへ接続するテストを作成しないでください
- 仕様にない便利機能を前提にしたテストを作成しないでください
- 結合試験の実装中に、entrypoint や feature 実装がテストしにくい構造だと判断した場合でも、勝手に `src/` を変更しないでください。
  変更が必要そうな場合は、テストしにくい理由、影響するファイル、見直し候補を作業報告に記載してください。
  実装側の変更が必要かどうかは、人間レビューで判断します。

## 作業後の報告

作業後は、以下を簡潔に報告してください。

- 作成または更新したファイル
- 参照したファイル
- 実装した結合試験の概要
- 対象 entrypoint
- 対象 feature
- 主な正常系
- 主な異常系
- `11_integration_test_plan.md` との対応
- `10_overview.md` との整合確認結果
- テストを実行した場合、そのコマンドと結果
- テストを実行できなかった場合、その理由
- 確認事項を提示した場合、その理由
- 仮定を置いた場合、その内容

## レビュー補助メモ

作業後の報告に、レビュー補助メモを含めてください。
記載項目とルールは `docs/rules/core/50_records_and_reporting.md` の「レビュー補助メモ」に従います（このプロンプトには定義を複製しません）。

レビュー補助メモは作業完了報告（チャット）に出力します。`tasks.md` には書きません。

## 作業後の tasks.md 更新候補

このプロンプトでは `tasks.md` を直接更新しません。

`tasks.md` の更新が必要と判断した場合は、作業報告に「tasks.md 更新候補」として記載してください。
`tasks.md` の実際の更新は、人間が確認したうえで別作業として行います。
