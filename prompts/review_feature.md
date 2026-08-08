# feature 単体レビューを行ってください

このプロンプトは、実装後の feature 単体レビューを行い、結果を `<対象機能フォルダ>/25_review_result.md` に記録するためのものです。

`24_review_checklist.md` はレビュー観点の定義です。レビュー結果や指摘事項は `24_review_checklist.md` には追記せず、`25_review_result.md` に記録してください。

このプロンプトは feature 単体レビュー専用です。`entrypoint.py`、entrypoint テスト、`11_integration_test_plan.md`、結合試験は原則として主対象にしません。feature との責務分担に関係する場合だけ関連ファイルとして参照して構いませんが、command/app 全体の判定は `prompts/review_command.md` に委ねてください。

---

## 必須参照ルール

この節は、この task で必ず読むルール文書**一覧**の正本です。各ルールの**内容**は、ここに列挙したルール文書を正本とします。このプロンプトが core や project を再定義するものではありません。

`## 参照するファイル` は今回の作業対象資料であり、このルール文書一覧とは役割が異なります。

### 作業開始時に読む

- `docs/rules/core/20_approval_and_review.md`（レビューと修正の分離、次工程移行判定 `GO` / `条件付きGO` / `STOP` の定義）
- `docs/rules/core/40_official_docs_and_context.md`（正式資料と補助コンテキストの扱い）
- `docs/rules/project/25_review_policy.md`（レビュー結果の評価値）
- `docs/rules/project/30_development_rules.md`（実装規約、entrypoint と features の責務分担の判定基準）
- `docs/rules/project/40_testing_rules.md`

### 作業完了時に読む

- `docs/rules/core/50_records_and_reporting.md`

---

## 利用者が指定する項目

以下を対象 feature に合わせて指定してください。

- 対象機能フォルダ: `docs/<command_or_app_name>/features/<feature_name>/`
- コマンド/アプリ名: `<command_or_app_name>`
- 対象機能名: `<feature_name>`
- 実装ファイル: `src/<command_or_app_name>/features/<feature_name>.py`
- テストファイル: `tests/<command_or_app_name>/features/test_<feature_name>.py`
- レビュー結果ファイル: `<対象機能フォルダ>/25_review_result.md`
- 補足条件: `必要に応じて書く。なければ「なし」`

## 参照するファイル

必ず現在の以下を読み直してください。

- `<対象機能フォルダ>/20_spec.md`
- `<対象機能フォルダ>/21_design.md`
- `<対象機能フォルダ>/22_flow.md`
- `<対象機能フォルダ>/23_test_plan.md`
- `<対象機能フォルダ>/24_review_checklist.md`
- 利用者が指定した feature 実装ファイル
- 利用者が指定した feature 単体テストファイル

必要に応じて、feature との責務分担を確認するためだけに以下を参照して構いません。

- `docs/<command_or_app_name>/10_overview.md`
- `src/<command_or_app_name>/entrypoint.py`
- `tests/<command_or_app_name>/test_entrypoint_<short_name>.py`
- `docs/<command_or_app_name>/11_integration_test_plan.md`
- `tests/<command_or_app_name>/test_integration_<short_name>.py`

ただし、これらの command/app 全体に関する最終判定は `prompts/review_command.md` の範囲です。

`docs/context/` が存在する場合は、補助資料として軽く参照して構いません。
ただし、このプロンプトの主責務は、正式資料（`20_spec.md`、`21_design.md`、`22_flow.md`、`23_test_plan.md` など）・実装・テストの整合確認です。`docs/context/` の横断探索を主責務にしないでください。context 量が増えても feature 単体レビューを完遂できるようにするためです。
`docs/context/` は確定仕様ではありません。レビュー中に偶然気づいたズレ・矛盾・反映漏れ・未決事項・却下案の混入があれば、軽い確認トリガーとして `25_review_result.md` に人間確認事項として記録する程度にとどめてください。そのまま確定仕様として採用しないでください。
`docs/context/` の横断的な深掘りが必要な場合は、このプロンプトでは行わず、`prompts/review_context.md` に委譲してください。
正式資料と矛盾する場合や、AIが判断できない場合は、勝手に解決せず人間確認事項として `25_review_result.md` に記録してください。

## 作成または更新するファイル

- `<対象機能フォルダ>/25_review_result.md`

## 変更してよいファイル

- `<対象機能フォルダ>/25_review_result.md`
- `docs/<command_or_app_name>/tasks.md`
- `<対象機能フォルダ>/tasks.md`
  - ただし、現在地と次に確認することを短く更新する場合に限る

## 変更してはいけないファイル

この節は、**今回の task で変更を許可されていないファイル**です。project が定める**保護対象**（`docs/rules/project/50_ai_permissions.md`）とは別のレイヤであり、両方を満たす必要があります。

レビュー依頼だけの場合、以下は変更しないでください。
ただし、変更してよいファイルに記載した `tasks.md` の必要最小限の更新は例外です。

- `<対象機能フォルダ>/20_spec.md`
- `<対象機能フォルダ>/21_design.md`
- `<対象機能フォルダ>/22_flow.md`
- `<対象機能フォルダ>/23_test_plan.md`
- `<対象機能フォルダ>/24_review_checklist.md`
- feature 実装ファイル
- feature 単体テストファイル
- `src/<command_or_app_name>/entrypoint.py`
- `tests/<command_or_app_name>/test_entrypoint_<short_name>.py`
- `docs/<command_or_app_name>/11_integration_test_plan.md`
- `tests/<command_or_app_name>/test_integration_<short_name>.py`
- `prompts/`
- `AGENTS.md`
- `README.md`
- `docs/templates/`
- `docs/context/`（補助資料として参照するだけにとどめ、変更しない）

レビュー中に仕様、設計、実装、テストの修正が必要だと判断した場合でも、勝手に修正しないでください。修正候補として `25_review_result.md` に記録してください。

---

## 再レビュー時のルール

既存の `25_review_result.md` が存在する場合でも、古い判定をそのまま採用しないでください。

必ず現在の `20_spec.md`、`21_design.md`、`22_flow.md`、`23_test_plan.md`、`24_review_checklist.md`、feature 実装ファイル、feature 単体テストファイルを読み直してください。

既存の `25_review_result.md` は参考情報として扱っても構いませんが、最終判定は現在のファイル群に基づいて判断し、新しいレビュー結果として `25_review_result.md` を上書き更新してください。

---

## 作業手順

1. 対象 feature の `20_spec.md` から `24_review_checklist.md` を確認してください
2. feature 実装ファイルを確認してください
3. feature 単体テストファイルを確認してください
4. `24_review_checklist.md` の観点に沿って feature 単体レビューを行ってください
5. 実装が `20_spec.md`、`21_design.md`、`22_flow.md` とズレていないか確認してください
6. 単体テストが `23_test_plan.md` とズレていないか確認してください
7. 必要に応じて `python -m pytest` または利用者が指定したテストコマンドを実行してください
8. レビュー結果を `<対象機能フォルダ>/25_review_result.md` に作成または上書き更新してください

## 共通設計書との整合確認

`docs/<command_or_app_name>/common_design/` が存在する場合は、以下を確認してください。

- feature の実装が、DB設計書（`33_db_design.md`）と整合しているか
- feature の実装が、ファイル設計書（`31_file_design.md`）と整合しているか
- feature の実装が、共通データ設計書（`32_data_design.md`）と整合しているか
- feature 個別の `21_design.md` の中で、DBテーブル・ファイル形式・共通データ項目を新規定義していないか
- 共通設計書に未定義の設計が実装されていないか

整合しない箇所がある場合は、実装を勝手に修正せず、`25_review_result.md` に指摘として記録してください。

## レビューで確認すること

- feature の仕様が明確で、実装に反映されていること
- feature の関数設計が実装と対応していること
- feature の呼び出し定義が実装と対応していること
- feature 単体テストが `23_test_plan.md` の観点を確認していること
- feature 単体テストが CLI、entrypoint、結合試験の詳細確認に広がりすぎていないこと
- feature 固有ロジックが `entrypoint.py` 側へ流出していないこと
- `src/common/` に勝手に共通化していないこと
- 仕様にない便利機能や余計な抽象化を追加していないこと
- 指定された出力先を AI 判断で変更していないこと
- `pytest` の import mismatch やテストファイル名衝突がある場合、勝手に別名ファイルを作成していないこと
- fallback import などのテスト都合の実装が feature の責務を曖昧にしていないこと

## レビュー結果に記録する内容

`25_review_result.md` には、`docs/templates/25_review_result_template.md` の見出し構成に沿って以下を記録してください。

- レビュー対象
- 参照したファイル
- 実行した確認内容
- テスト実行結果
- 仕様との整合
- 関数設計との整合
- 呼び出し定義との整合
- テスト計画との整合
- feature 実装と feature 単体テストの確認結果
- entrypoint や結合試験との責務分担に関する気づき
- 指定外変更・AIアドリブの有無
- 指摘事項
- 改善候補
- 仕様変更が必要そうな点
- 最終判定
- 次工程移行判定（GO / 条件付きGO / STOP）
- 作業後報告

## 最終判定

レビュー結果の最後に、以下のいずれかを記録してください。

ここに記載する値は出力形式上の列挙であり、**定義の正本は `docs/rules/project/25_review_policy.md` です。**

- `OK`: 大きな問題なし
- `軽微な指摘あり`: 軽微な修正または確認事項がある
- `要修正`: 実装または単体テストの修正が必要
- `要仕様確認`: 仕様に戻って確認が必要

`軽微な指摘あり` は成果物の状態を表すものであり、これを理由に次工程移行判定を `GO` にしてはいけません。

command/app 全体の判定が必要な場合は、ここでは判定せず、`prompts/review_command.md` で確認する必要があることを記録してください。

### 次工程移行判定

上記の判定に加えて、次工程へ進めるかどうかを以下のいずれかで記録してください。

**判定値そのものの定義と、STOP / 条件付きGO の使い分けの正本は `docs/rules/core/20_approval_and_review.md` です。**

- `GO`：次工程へ進んでよい
- `条件付きGO`：未解決項目・後続工程への影響・見直し条件を明記したうえで進んでよい
- `STOP`：次工程へ進んではならない。何を解決すれば進めるかを明記して停止する

人間判断待ち、承認の前提となる未決事項、安全に次工程へ進めない未決事項、または整理されていない未解決事項が残っている場合は `STOP` です。
「要検討として記録した」ことは、「解決した」ことではありません。

条件付きGOとする場合は、以下の6項目を必ず明記してください。

- 未解決項目
- 仮置きする内容と理由
- 条件付きでも進める理由
- 後続工程への影響
- 見直しが必要になる条件
- 人間判断が必要かどうか

STOPとする場合は、次工程の成果物（`21_design.md` 等）を作成せず、停止して報告してください。

## 仕様変更が必要そうな場合

レビュー中に、現在の仕様では判断できない点や、仕様変更が必要そうな点を見つけた場合は、実装やテストを勝手に修正しないでください。

`25_review_result.md` に、以下を記録してください。

- 仕様確認が必要だと判断した理由
- 影響を受ける要件
- 修正が必要そうなドキュメント
- 実装への影響
- テストへの影響

そのうえで、最終判定を `要仕様確認` としてください。

## 禁止事項

- レビュー依頼だけの場合、勝手に実装を変更しないでください
- レビュー依頼だけの場合、勝手にテストを変更しないでください
- `24_review_checklist.md` にレビュー結果を追記しないでください
- `25_review_result.md` 以外を出力先にしないでください
- レビュー結果の詳細を `tasks.md` に書かないでください
- 指定された出力先を AI 判断で変更しないでください
- `pytest` の import mismatch やテストファイル名衝突を理由に、勝手に別名のテストファイルを作成しないでください
- 共通モジュールを作成しないでください
- 仕様にない便利機能を追加しないでください
- 結合試験、外部API、CI/CD、デプロイ資産を追加しないでください
- command/app 全体レビューの最終判定を `25_review_result.md` だけで完結させないでください

## 作業後の報告

作業後に、以下を簡潔に報告してください。

- 作成または更新したファイル
- 参照したファイル
- テストを実行した場合、そのコマンドと結果
- 最終判定
- 主な指摘事項
- command/app 全体レビューに委ねる事項の有無
- 仕様確認が必要な点の有無

## 作業後の tasks.md 更新

作業後は、対象 command/app または feature の `tasks.md` を必ず確認してください。

必要に応じて、現在の状態、作業メモ、次に確認すること、引き継ぎに必要な短い注意点だけを更新してください。

`tasks.md` には、仕様・設計・テスト計画・レビュー結果の詳細や長いテストログを書かないでください。
詳細は `20_spec.md`、`21_design.md`、`22_flow.md`、`23_test_plan.md`、`24_review_checklist.md`、`25_review_result.md` など、それぞれの専用ファイルに記録してください。

`tasks.md` を更新しない場合は、更新しない理由を作業報告に書いてください。
